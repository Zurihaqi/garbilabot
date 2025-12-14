from datetime import datetime
import random
import discord
from discord import Embed, Color
from discord import app_commands
from discord.ext import commands
from services.user_service import UserService
from utils.game_logic import GameLogic
from database.db_manager import DatabaseManager

class EconomyCommands(commands.Cog):
    """Economy-related commands"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="daily", description="Claim daily rewards")
    async def daily(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        today = datetime.now().date().isoformat()
        
        UserService.ensure_user_exists(user_id, interaction.user.name)
        user = UserService.get_user(user_id)
        
        with DatabaseManager.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT last_daily FROM users WHERE user_id=?", (user_id,))
            row = c.fetchone()
            
            if row['last_daily'] == today:
                await interaction.response.send_message("⚠️ Already claimed today!", ephemeral=True)
                return
            
            base = random.randint(50, 150)
            bonus = user.level * 10
            total = base + bonus
            
            c.execute(
                "UPDATE users SET balance = balance + ?, last_daily = ? WHERE user_id = ?",
                (total, today, user_id)
            )
        
        embed = Embed(
            title="💰 Daily Reward!",
            description=f"**Base:** {base}\n**Level Bonus:** {bonus}\n**Total:** {total}",
            color=Color.green()
        )
        embed.add_field(name="Balance", value=f"{user.balance + total:,}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="heal", description="Fully restore HP (costs coins)")
    async def heal(self, interaction: discord.Interaction):
        user = UserService.get_user(interaction.user.id)
        
        if not user:
            await interaction.response.send_message("❌ Profile not found!", ephemeral=True)
            return
        
        if user.is_full_hp():
            await interaction.response.send_message("❤️ Already at full HP!", ephemeral=True)
            return
        
        cost = GameLogic.calculate_heal_cost(user.level)
        
        if user.balance < cost:
            await interaction.response.send_message(f"⚠️ Need {cost} coins!", ephemeral=True)
            return
        
        UserService.update_user_stats(
            interaction.user.id,
            hp=user.max_hp,
            balance=user.balance - cost
        )
        
        await interaction.response.send_message(
            f"✨ Fully healed for {cost} coins! HP: {user.max_hp}/{user.max_hp}"
        )
