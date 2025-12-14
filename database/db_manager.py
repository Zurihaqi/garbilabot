import aiosqlite
from database.shop_data import ShopData
from database.quest_data import QuestData

DB_PATH = "rpg.db"

class DatabaseManager:
    """Handles all database operations asynchronously"""

    @staticmethod
    async def init_db():
        """Initialize database schema asynchronously"""
        async with aiosqlite.connect(DB_PATH) as conn:
            conn.row_factory = aiosqlite.Row
            await conn.execute("PRAGMA journal_mode=WAL")

            # Users table
            await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                balance INTEGER DEFAULT 0,
                last_daily TEXT,
                last_message_ts TEXT,
                level INTEGER DEFAULT 1,
                xp INTEGER DEFAULT 0,
                class TEXT DEFAULT 'Novice',
                hp INTEGER DEFAULT 100,
                max_hp INTEGER DEFAULT 100,
                attack INTEGER DEFAULT 10,
                defense INTEGER DEFAULT 5,
                last_adventure TEXT,
                adventure_count INTEGER DEFAULT 0,
                pvp_wins INTEGER DEFAULT 0,
                pvp_losses INTEGER DEFAULT 0,
                boss_kills INTEGER DEFAULT 0
            )
            """)

            # Inventory table
            await conn.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                user_id INTEGER,
                item TEXT,
                quantity INTEGER DEFAULT 1,
                equipped INTEGER DEFAULT 0,
                PRIMARY KEY(user_id, item)
            )
            """)

            # Shop table
            await conn.execute("""
            CREATE TABLE IF NOT EXISTS shop (
                item TEXT PRIMARY KEY,
                description TEXT,
                price INTEGER,
                item_type TEXT,
                stat_bonus TEXT,
                bonus_value INTEGER DEFAULT 0,
                level_req INTEGER DEFAULT 1
            )
            """)

            # Quests table
            await conn.execute("""
            CREATE TABLE IF NOT EXISTS quests (
                quest_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                description TEXT,
                reward_coins INTEGER,
                reward_xp INTEGER,
                requirement_level INTEGER DEFAULT 1,
                quest_type TEXT DEFAULT 'adventure'
            )
            """)

            # User quests
            await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_quests (
                user_id INTEGER,
                quest_id INTEGER,
                status TEXT DEFAULT 'active',
                progress INTEGER DEFAULT 0,
                PRIMARY KEY(user_id, quest_id)
            )
            """)

            # PvP history
            await conn.execute("""
            CREATE TABLE IF NOT EXISTS pvp (
                battle_id INTEGER PRIMARY KEY AUTOINCREMENT,
                attacker_id INTEGER,
                defender_id INTEGER,
                winner_id INTEGER,
                timestamp TEXT,
                attacker_power INTEGER,
                defender_power INTEGER
            )
            """)

            # Initialize quests if empty
            async with conn.execute("SELECT COUNT(*) FROM quests") as cursor:
                row = await cursor.fetchone()
                if row[0] == 0:
                    await QuestData.initialize_quests(conn)

            # Initialize shop if empty
            async with conn.execute("SELECT COUNT(*) FROM shop") as cursor:
                row = await cursor.fetchone()
                if row[0] == 0:
                    await ShopData.initialize_shop(conn)

            await conn.commit()

    @staticmethod
    async def get_connection():
        """Return a database connection"""
        conn = await aiosqlite.connect(DB_PATH)
        conn.row_factory = aiosqlite.Row
        await conn.execute("PRAGMA journal_mode=WAL")
        return conn