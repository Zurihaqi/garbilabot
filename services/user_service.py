from database.db_manager import DatabaseManager
from models.user import User
from typing import Optional, Dict, Any, List

class UserService:
    """Handles user-related database operations"""
    
    @staticmethod
    def ensure_user_exists(user_id: int, username: str):
        """Create user if doesn't exist"""
        with DatabaseManager.get_connection() as conn:
            c = conn.cursor()
            c.execute(
                "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
                (user_id, username)
            )
    
    @staticmethod
    def get_user(user_id: int) -> Optional[User]:
        """Get user by ID"""
        with DatabaseManager.get_connection() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT user_id, username, balance, level, xp, class, hp, max_hp,
                       attack, defense, adventure_count, pvp_wins, pvp_losses, boss_kills
                FROM users WHERE user_id = ?
            """, (user_id,))
            row = c.fetchone()
            
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
    
    @staticmethod
    def update_user_stats(user_id: int, **kwargs):
        """Update user stats"""
        if not kwargs:
            return
        
        set_clause = ", ".join(f"{k}=?" for k in kwargs.keys())
        values = list(kwargs.values()) + [user_id]
        
        with DatabaseManager.get_connection() as conn:
            c = conn.cursor()
            c.execute(f"UPDATE users SET {set_clause} WHERE user_id=?", values)
    
    @staticmethod
    def add_xp_and_coins(user_id: int, xp: int, coins: int) -> Dict[str, Any]:
        """Add XP and coins, handle level ups"""
        from utils.game_logic import GameLogic
        
        with DatabaseManager.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT level, xp, balance FROM users WHERE user_id=?", (user_id,))
            row = c.fetchone()
            
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
                c.execute("""
                    UPDATE users SET level=?, xp=?, balance=?, class=?,
                                   max_hp=?, hp=?, attack=?, defense=?
                    WHERE user_id=?
                """, (new_level, new_xp, new_balance, stats['class'],
                      stats['max_hp'], stats['max_hp'], stats['attack'],
                      stats['defense'], user_id))
            else:
                c.execute("""
                    UPDATE users SET xp=?, balance=? WHERE user_id=?
                """, (new_xp, new_balance, user_id))
            
            return {
                'leveled_up': leveled_up,
                'new_level': new_level,
                'new_xp': new_xp,
                'new_balance': new_balance
            }
    
    @staticmethod
    def get_leaderboard(category: str, limit: int = 10) -> List[Dict]:
        """Get leaderboard by category"""
        with DatabaseManager.get_connection() as conn:
            c = conn.cursor()
            
            if category == "level":
                c.execute("SELECT username, level, xp FROM users ORDER BY level DESC, xp DESC LIMIT ?", (limit,))
            elif category == "coins":
                c.execute("SELECT username, balance FROM users ORDER BY balance DESC LIMIT ?", (limit,))
            elif category == "pvp":
                c.execute("SELECT username, pvp_wins, pvp_losses FROM users ORDER BY pvp_wins DESC LIMIT ?", (limit,))
            else:  # bosses
                c.execute("SELECT username, boss_kills FROM users ORDER BY boss_kills DESC LIMIT ?", (limit,))
            
            return [dict(row) for row in c.fetchall()]