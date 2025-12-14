from datetime import datetime, timedelta
import random
import discord
from discord.ext import commands
from database.db_manager import DatabaseManager
from services.user_service import UserService

class EventListener(commands.Cog):
    """Listens to Discord events"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Award coins/XP for messages"""
        if message.author.bot or not message.guild:
            return
        
        user_id = message.author.id
        now = datetime.now()
        
        await UserService.ensure_user_exists(user_id, message.author.name)
        
        # Get connection and handle it properly
        conn = await DatabaseManager.get_connection()
        try:
            # Check last message timestamp
            async with conn.execute("SELECT last_message_ts FROM users WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
            
            if row and row['last_message_ts']:
                last = datetime.fromisoformat(row['last_message_ts'])
                if now - last < timedelta(seconds=60):
                    return
            
            # Award coins and XP
            coins = random.randint(1, 5)
            xp = random.randint(1, 3)
            
            # Update last message timestamp
            await conn.execute(
                "UPDATE users SET last_message_ts = ? WHERE user_id = ?",
                (now.isoformat(), user_id)
            )
            await conn.commit()
        finally:
            await conn.close()
        
        # Handle XP/coins and level up
        result = await UserService.add_xp_and_coins(user_id, xp, coins)
        
        if result['leveled_up']:
            try:
                user = await UserService.get_user(user_id)
                await message.channel.send(
                    f"🎉 {message.author.mention} leveled up to **Level {result['new_level']}** ({user.cls})!"
                )
            except Exception as e:
                print(f"Error sending level up message: {e}")