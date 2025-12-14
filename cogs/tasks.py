from discord.ext import tasks, commands
from database.db_manager import DatabaseManager

class BackgroundTasks(commands.Cog):
    """Background tasks"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.hp_regen.start()

    def cog_unload(self):
        self.hp_regen.cancel()

    @tasks.loop(minutes=5)
    async def hp_regen(self):
        """Regenerate HP for all users asynchronously"""
        conn = await DatabaseManager.get_connection()
        try:
            await conn.execute("UPDATE users SET hp = MIN(hp + 10, max_hp) WHERE hp < max_hp")
            await conn.commit()
        finally:
            await conn.close()