from database.db_manager import DatabaseManager
from typing import List, Dict, Any

class InventoryService:
    """Handles inventory operations"""
    
    @staticmethod
    def get_inventory(user_id: int) -> List[Dict]:
        """Get user's inventory"""
        with DatabaseManager.get_connection() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT i.item, i.quantity, i.equipped, s.item_type, s.stat_bonus, s.bonus_value
                FROM inventory i
                LEFT JOIN shop s ON i.item = s.item
                WHERE i.user_id = ?
                ORDER BY i.equipped DESC, s.item_type
            """, (user_id,))
            return [dict(row) for row in c.fetchall()]
    
    @staticmethod
    def add_item(user_id: int, item_name: str, quantity: int = 1):
        """Add item to inventory"""
        with DatabaseManager.get_connection() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO inventory (user_id, item, quantity)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, item) DO UPDATE SET quantity = quantity + ?
            """, (user_id, item_name, quantity, quantity))
    
    @staticmethod
    def remove_item(user_id: int, item_name: str, quantity: int = 1):
        """Remove item from inventory"""
        with DatabaseManager.get_connection() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT quantity FROM inventory WHERE user_id = ? AND item = ?
            """, (user_id, item_name))
            row = c.fetchone()
            
            if not row:
                return False
            
            if row['quantity'] <= quantity:
                c.execute("DELETE FROM inventory WHERE user_id = ? AND item = ?",
                         (user_id, item_name))
            else:
                c.execute("""
                    UPDATE inventory SET quantity = quantity - ?
                    WHERE user_id = ? AND item = ?
                """, (quantity, user_id, item_name))
            
            return True
    
    @staticmethod
    def equip_item(user_id: int, item_name: str) -> Dict[str, Any]:
        """Equip an item"""
        with DatabaseManager.get_connection() as conn:
            c = conn.cursor()
            
            # Get item info
            c.execute("""
                SELECT i.equipped, s.item_type, s.stat_bonus, s.bonus_value
                FROM inventory i
                JOIN shop s ON i.item = s.item
                WHERE i.user_id = ? AND i.item = ?
            """, (user_id, item_name))
            item = c.fetchone()
            
            if not item:
                return {'success': False, 'error': 'Item not found'}
            
            if item['equipped']:
                return {'success': False, 'error': 'Already equipped'}
            
            # Unequip old item of same type
            c.execute("""
                SELECT i.item, s.stat_bonus, s.bonus_value
                FROM inventory i
                JOIN shop s ON i.item = s.item
                WHERE i.user_id = ? AND i.equipped = 1 AND s.item_type = ?
            """, (user_id, item['item_type']))
            old_item = c.fetchone()
            
            if old_item:
                c.execute("UPDATE inventory SET equipped = 0 WHERE user_id = ? AND item = ?",
                         (user_id, old_item['item']))
                
                # Remove old stats
                if old_item['stat_bonus'] == 'attack':
                    c.execute("UPDATE users SET attack = attack - ? WHERE user_id = ?",
                             (old_item['bonus_value'], user_id))
                elif old_item['stat_bonus'] == 'defense':
                    c.execute("UPDATE users SET defense = defense - ? WHERE user_id = ?",
                             (old_item['bonus_value'], user_id))
            
            # Equip new item
            c.execute("UPDATE inventory SET equipped = 1 WHERE user_id = ? AND item = ?",
                     (user_id, item_name))
            
            # Add new stats
            if item['stat_bonus'] == 'attack':
                c.execute("UPDATE users SET attack = attack + ? WHERE user_id = ?",
                         (item['bonus_value'], user_id))
            elif item['stat_bonus'] == 'defense':
                c.execute("UPDATE users SET defense = defense + ? WHERE user_id = ?",
                         (item['bonus_value'], user_id))
            
            return {
                'success': True,
                'stat_bonus': item['stat_bonus'],
                'bonus_value': item['bonus_value']
            }
    
    @staticmethod
    def get_equipped_items(user_id: int) -> List[str]:
        """Get list of equipped item names"""
        with DatabaseManager.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT item FROM inventory WHERE user_id = ? AND equipped = 1", (user_id,))
            return [row['item'] for row in c.fetchall()]