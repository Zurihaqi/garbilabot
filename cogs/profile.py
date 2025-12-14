import discord
from discord.ext import commands
from discord import app_commands, Embed, Color
from typing import Literal
from services.user_service import UserService
from services.inventory_service import InventoryService
from utils.profile_card_gen import ProfileCardGenerator
from view.profile import ProfileView

class ProfileCommands(commands.Cog):
    """Profile and status commands"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="profile", description="View RPG profile with interactive UI")
    async def profile(self, interaction: discord.Interaction, user: discord.User = None):
        await interaction.response.defer()
        
        target = user or interaction.user
        
        await UserService.ensure_user_exists(target.id, target.name)
        user_data = await UserService.get_user(target.id)
        
        if not user_data:
            await interaction.followup.send("❌ Profile not found!", ephemeral=True)
            return
        
        inventory = await InventoryService.get_inventory(target.id)
        inventory_count = len(inventory)
        equipped = await InventoryService.get_equipped_items(target.id)
        
        # Create profile view
        view = ProfileView(user_data, target, inventory_count, equipped)
        
        # Create initial embed
        embed = view.create_stats_embed()
        
        # Try to create profile card
        profile_card = await ProfileCardGenerator.create_profile_card(user_data, target)
        
        if profile_card:
            await interaction.followup.send(embed=embed, view=view, file=profile_card)
        else:
            await interaction.followup.send(embed=embed, view=view)
    
    @app_commands.command(name="leaderboard", description="View top players")
    async def leaderboard(
        self,
        interaction: discord.Interaction,
        category: Literal["level", "coins", "pvp", "bosses"] = "level"
    ):
        await interaction.response.defer()
        
        rows = await UserService.get_leaderboard(category, 10)
        
        if not rows:
            await interaction.followup.send("📊 No data yet!", ephemeral=True)
            return
        
        # Format based on category
        if category == "level":
            title = "🏆 Top Players by Level"
            fmt = lambda r: f"**{r['username']}** - Level {r['level']} ({r['xp']} XP)"
        elif category == "coins":
            title = "💰 Richest Players"
            fmt = lambda r: f"**{r['username']}** - {r['balance']:,} coins"
        elif category == "pvp":
            title = "⚔️ PvP Champions"
            fmt = lambda r: f"**{r['username']}** - {r['pvp_wins']}W / {r['pvp_losses']}L"
        else:
            title = "🐉 Boss Slayers"
            fmt = lambda r: f"**{r['username']}** - {r['boss_kills']} kills"
        
        # Create leaderboard with medals
        desc_lines = []
        for i, r in enumerate(rows):
            if i == 0:
                medal = "🥇"
            elif i == 1:
                medal = "🥈"
            elif i == 2:
                medal = "🥉"
            else:
                medal = f"`{i+1}.`"
            
            desc_lines.append(f"{medal} {fmt(r)}")
        
        desc = "\n".join(desc_lines)
        
        embed = Embed(title=title, description=desc, color=Color.gold())
        embed.set_footer(text=f"Showing top {len(rows)} players • Updated in real-time")
        
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(ProfileCommands(bot))