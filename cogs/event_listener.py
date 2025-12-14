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
        
        UserService.ensure_user_exists(user_id, message.author.name)
        
        with DatabaseManager.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT last_message_ts FROM users WHERE user_id = ?", (user_id,))
            row = c.fetchone()
            
            if row['last_message_ts']:
                last = datetime.fromisoformat(row['last_message_ts'])
                if now - last < timedelta(seconds=60):
                    return
            
            coins = random.randint(1, 5)
            xp = random.randint(1, 3)
            
            c.execute("UPDATE users SET last_message_ts = ? WHERE user_id = ?", (now.isoformat(), user_id))
        
        result = UserService.add_xp_and_coins(user_id, xp, coins)
        
        if result['leveled_up']:
            try:
                user = UserService.get_user(user_id)
                await message.channel.send(
                    f"🎉 {message.author.mention} leveled up to **Level {result['new_level']}** ({user.cls})!"
                )
            except Exception as e:
                print(f"Error sending level up message: {e}")