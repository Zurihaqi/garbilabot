import sqlite3
from contextlib import contextmanager
from database.shop_data import ShopData

DB_PATH = "rpg.db"

class DatabaseManager:
    """Handles all database operations with connection management"""
    
    @staticmethod
    @contextmanager
    def get_connection():
        """Context manager for database connections"""
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    @staticmethod
    def init_db():
        """Initialize database schema"""
        with DatabaseManager.get_connection() as conn:
            c = conn.cursor()
            
            # Users table
            c.execute("""
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
            c.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                user_id INTEGER,
                item TEXT,
                quantity INTEGER DEFAULT 1,
                equipped INTEGER DEFAULT 0,
                PRIMARY KEY(user_id, item)
            )
            """)
            
            # Shop table
            c.execute("""
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
            c.execute("""
            CREATE TABLE IF NOT EXISTS quests (
                quest_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                description TEXT,
                reward_coins INTEGER,
                reward_xp INTEGER,
                requirement_level INTEGER DEFAULT 1
            )
            """)
            
            # User quests
            c.execute("""
            CREATE TABLE IF NOT EXISTS user_quests (
                user_id INTEGER,
                quest_id INTEGER,
                status TEXT DEFAULT 'active',
                PRIMARY KEY(user_id, quest_id)
            )
            """)
            
            # PvP history
            c.execute("""
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
            
            # Initialize shop if empty
            c.execute("SELECT COUNT(*) FROM shop")
            if c.fetchone()[0] == 0:
                ShopData.initialize_shop(c)