from database.db_manager import DatabaseManager
from database.shop_data import ShopData
from database.quest_data import QuestData
import asyncio

async def reseed():
    conn = await DatabaseManager.get_connection()
    try:
        await ShopData.initialize_shop(conn)
        await QuestData.initialize_quests(conn)
        await conn.commit()
    finally:
        await conn.close()

asyncio.run(reseed())
