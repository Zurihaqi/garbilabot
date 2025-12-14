import discord
from discord.ext import commands
from discord import app_commands, Embed, Color
from services.user_service import UserService
from services.inventory_service import InventoryService
from utils.game_logic import GameLogic
from typing import Literal

class ProfileCommands(commands.Cog):
    """Profile and status commands"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="profile", description="View RPG profile")
    async def profile(self, interaction: discord.Interaction, user: discord.User = None):
        target = user or interaction.user
        
        UserService.ensure_user_exists(target.id, target.name)
        user_data = UserService.get_user(target.id)
        
        if not user_data:
            await interaction.response.send_message("❌ Profile not found!", ephemeral=True)
            return
        
        inventory_count = len(InventoryService.get_inventory(target.id))
        equipped = InventoryService.get_equipped_items(target.id)
        next_xp = GameLogic.calculate_level_xp(user_data.level)
        
        embed = Embed(title=f"⚔️ {user_data.username}'s Profile", color=Color.gold())
        
        stats = (
            f"💰 **Coins:** {user_data.balance:,}\n"
            f"✨ **Level:** {user_data.level} ({user_data.xp}/{next_xp} XP)\n"
            f"🛡️ **Class:** {user_data.cls}\n"
            f"❤️ **HP:** {user_data.hp}/{user_data.max_hp}\n"
            f"⚔️ **Attack:** {user_data.attack}\n"
            f"🛡️ **Defense:** {user_data.defense}"
        )
        embed.add_field(name="📊 Stats", value=stats, inline=True)
        
        combat = (
            f"🗺️ **Adventures:** {user_data.adventure_count}\n"
            f"⚔️ **PvP Wins:** {user_data.pvp_wins}\n"
            f"💀 **PvP Losses:** {user_data.pvp_losses}\n"
            f"📈 **Win Rate:** {user_data.win_rate:.1f}%\n"
            f"🐉 **Boss Kills:** {user_data.boss_kills}"
        )
        embed.add_field(name="⚔️ Combat", value=combat, inline=True)
        
        eq_text = ", ".join(equipped) if equipped else "None"
        embed.add_field(
            name="🎒 Inventory",
            value=f"**Items:** {inventory_count}\n**Equipped:** {eq_text}",
            inline=False
        )
        
        if target.avatar:
            embed.set_thumbnail(url=target.avatar.url)
        
        embed.set_footer(text="Use /inventory • /shop • /adventure")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="leaderboard", description="View top players")
    async def leaderboard(
        self,
        interaction: discord.Interaction,
        category: Literal["level", "coins", "pvp", "bosses"] = "level"
    ):
        rows = UserService.get_leaderboard(category, 10)
        
        if not rows:
            await interaction.response.send_message("📊 No data yet!", ephemeral=True)
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
        
        desc = "\n".join(f"{i+1}. {fmt(r)}" for i, r in enumerate(rows))
        embed = Embed(title=title, description=desc, color=Color.gold())
        embed.set_footer(text=f"Showing top {len(rows)} players")
        
        await interaction.response.send_message(embed=embed)