from .profile import ProfileCommands
from .economy import EconomyCommands
from .shop import ShopCommands
from .combat import CombatCommands
from .event_listener import EventListener
from .tasks import BackgroundTasks
from database.db_manager import DatabaseManager

async def setup(bot):
    """Setup function to load all RPG-related cogs"""
    await DatabaseManager.init_db()

    await bot.add_cog(ProfileCommands(bot))
    await bot.add_cog(EconomyCommands(bot))
    await bot.add_cog(ShopCommands(bot))
    await bot.add_cog(CombatCommands(bot))
    await bot.add_cog(EventListener(bot))
    await bot.add_cog(BackgroundTasks(bot))

    print("✅ RPG system loaded successfully!")
