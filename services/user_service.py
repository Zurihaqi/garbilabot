from typing import Optional, Dict, List, Any
from database.db_manager import DatabaseManager
from models.user import User
from utils.game_logic import GameLogic

class UserService:
    """Handles user-related database operations"""
    
    @staticmethod
    async def ensure_user_exists(user_id: int, username: str):
        """Create user if doesn't exist"""
        conn = await DatabaseManager.get_connection()
        try:
            await conn.execute(
                "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
                (user_id, username)
            )
            await conn.commit()
        finally:
            await conn.close()
    
    @staticmethod
    async def get_user(user_id: int) -> Optional[User]:
        """Get user by ID"""
        conn = await DatabaseManager.get_connection()
        try:
            async with conn.execute("""
                SELECT user_id, username, balance, level, xp, class, hp, max_hp,
                       attack, defense, adventure_count, pvp_wins, pvp_losses, boss_kills
                FROM users WHERE user_id = ?
            """, (user_id,)) as cursor:
                row = await cursor.fetchone()
                
                if not row:
                    return None
                
                return User(
                    user_id=row['user_id'],
                    username=row['username'],
                    balance=row['balance'],
                    level=row['level'],
                    xp=row['xp'],
                    cls=row['class'],
                    hp=row['hp'],
                    max_hp=row['max_hp'],
                    attack=row['attack'],
                    defense=row['defense'],
                    adventure_count=row['adventure_count'],
                    pvp_wins=row['pvp_wins'],
                    pvp_losses=row['pvp_losses'],
                    boss_kills=row['boss_kills']
                )
        finally:
            await conn.close()
    
    @staticmethod
    async def update_user_stats(user_id: int, **kwargs):
        """Update user stats"""
        if not kwargs:
            return
        
        set_clause = ", ".join(f"{k}=?" for k in kwargs.keys())
        values = list(kwargs.values()) + [user_id]
        
        conn = await DatabaseManager.get_connection()
        try:
            await conn.execute(f"UPDATE users SET {set_clause} WHERE user_id=?", values)
            await conn.commit()
        finally:
            await conn.close()
    
    @staticmethod
    async def add_xp_and_coins(user_id: int, xp: int, coins: int) -> Dict[str, Any]:
        """Add XP and coins, handle level ups"""
        conn = await DatabaseManager.get_connection()
        try:
            async with conn.execute("SELECT level, xp, balance FROM users WHERE user_id=?", (user_id,)) as cursor:
                row = await cursor.fetchone()
            
            new_xp = row['xp'] + xp
            new_balance = max(0, row['balance'] + coins)
            new_level = row['level']
            
            leveled_up = False
            needed = GameLogic.calculate_level_xp(new_level)
            
            while new_xp >= needed:
                new_xp -= needed
                new_level += 1
                leveled_up = True
                needed = GameLogic.calculate_level_xp(new_level)
            
            if leveled_up:
                stats = GameLogic.get_level_stats(new_level)
                await conn.execute("""
                    UPDATE users SET level=?, xp=?, balance=?, class=?,
                                   max_hp=?, hp=?, attack=?, defense=?
                    WHERE user_id=?
                """, (new_level, new_xp, new_balance, stats['class'],
                      stats['max_hp'], stats['max_hp'], stats['attack'],
                      stats['defense'], user_id))
            else:
                await conn.execute("""
                    UPDATE users SET xp=?, balance=? WHERE user_id=?
                """, (new_xp, new_balance, user_id))
            
            await conn.commit()
            
            return {
                'leveled_up': leveled_up,
                'new_level': new_level,
                'new_xp': new_xp,
                'new_balance': new_balance
            }
        finally:
            await conn.close()
    
    @staticmethod
    async def get_leaderboard(category: str, limit: int = 10) -> List[Dict]:
        """Get leaderboard by category"""
        conn = await DatabaseManager.get_connection()
        try:
            if category == "level":
                query = "SELECT username, level, xp FROM users ORDER BY level DESC, xp DESC LIMIT ?"
            elif category == "coins":
                query = "SELECT username, balance FROM users ORDER BY balance DESC LIMIT ?"
            elif category == "pvp":
                query = "SELECT username, pvp_wins, pvp_losses FROM users ORDER BY pvp_wins DESC LIMIT ?"
            else:  # bosses
                query = "SELECT username, boss_kills FROM users ORDER BY boss_kills DESC LIMIT ?"
            
            async with conn.execute(query, (limit,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        finally:
            await conn.close()