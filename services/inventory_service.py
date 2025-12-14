from typing import List, Dict, Any
from database.db_manager import DatabaseManager

class InventoryService:
    """Handles inventory operations"""
    
    @staticmethod
    async def get_inventory(user_id: int) -> List[Dict]:
        """Get user's inventory"""
        conn = await DatabaseManager.get_connection()
        try:
            async with conn.execute("""
                SELECT i.item, i.quantity, i.equipped, s.item_type, s.stat_bonus, s.bonus_value
                FROM inventory i
                LEFT JOIN shop s ON i.item = s.item
                WHERE i.user_id = ?
                ORDER BY i.equipped DESC, s.item_type
            """, (user_id,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        finally:
            await conn.close()
    
    @staticmethod
    async def add_item(user_id: int, item_name: str, quantity: int = 1):
        """Add item to inventory"""
        conn = await DatabaseManager.get_connection()
        try:
            await conn.execute("""
                INSERT INTO inventory (user_id, item, quantity)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, item) DO UPDATE SET quantity = quantity + ?
            """, (user_id, item_name, quantity, quantity))
            await conn.commit()
        finally:
            await conn.close()
    
    @staticmethod
    async def remove_item(user_id: int, item_name: str, quantity: int = 1) -> bool:
        """Remove item from inventory"""
        conn = await DatabaseManager.get_connection()
        try:
            async with conn.execute("""
                SELECT quantity FROM inventory WHERE user_id = ? AND item = ?
            """, (user_id, item_name)) as cursor:
                row = await cursor.fetchone()
            
            if not row:
                return False
            
            if row['quantity'] <= quantity:
                await conn.execute("DELETE FROM inventory WHERE user_id = ? AND item = ?",
                                 (user_id, item_name))
            else:
                await conn.execute("""
                    UPDATE inventory SET quantity = quantity - ?
                    WHERE user_id = ? AND item = ?
                """, (quantity, user_id, item_name))
            
            await conn.commit()
            return True
        finally:
            await conn.close()
    
    @staticmethod
    async def equip_item(user_id: int, item_name: str) -> Dict[str, Any]:
        """Equip an item"""
        conn = await DatabaseManager.get_connection()
        try:
            # Get item info
            async with conn.execute("""
                SELECT i.equipped, s.item_type, s.stat_bonus, s.bonus_value
                FROM inventory i
                JOIN shop s ON i.item = s.item
                WHERE i.user_id = ? AND i.item = ?
            """, (user_id, item_name)) as cursor:
                item = await cursor.fetchone()
            
            if not item:
                return {'success': False, 'error': 'Item not found'}
            
            if item['equipped']:
                return {'success': False, 'error': 'Already equipped'}
            
            # Unequip old item of same type
            async with conn.execute("""
                SELECT i.item, s.stat_bonus, s.bonus_value
                FROM inventory i
                JOIN shop s ON i.item = s.item
                WHERE i.user_id = ? AND i.equipped = 1 AND s.item_type = ?
            """, (user_id, item['item_type'])) as cursor:
                old_item = await cursor.fetchone()
            
            if old_item:
                await conn.execute("UPDATE inventory SET equipped = 0 WHERE user_id = ? AND item = ?",
                                 (user_id, old_item['item']))
                
                # Remove old stats
                if old_item['stat_bonus'] == 'attack':
                    await conn.execute("UPDATE users SET attack = attack - ? WHERE user_id = ?",
                                     (old_item['bonus_value'], user_id))
                elif old_item['stat_bonus'] == 'defense':
                    await conn.execute("UPDATE users SET defense = defense - ? WHERE user_id = ?",
                                     (old_item['bonus_value'], user_id))
            
            # Equip new item
            await conn.execute("UPDATE inventory SET equipped = 1 WHERE user_id = ? AND item = ?",
                             (user_id, item_name))
            
            # Add new stats
            if item['stat_bonus'] == 'attack':
                await conn.execute("UPDATE users SET attack = attack + ? WHERE user_id = ?",
                                 (item['bonus_value'], user_id))
            elif item['stat_bonus'] == 'defense':
                await conn.execute("UPDATE users SET defense = defense + ? WHERE user_id = ?",
                                 (item['bonus_value'], user_id))
            
            await conn.commit()
            
            return {
                'success': True,
                'stat_bonus': item['stat_bonus'],
                'bonus_value': item['bonus_value']
            }
        finally:
            await conn.close()
    
    @staticmethod
    async def get_equipped_items(user_id: int) -> List[str]:
        """Get list of equipped item names"""
        conn = await DatabaseManager.get_connection()
        try:
            async with conn.execute("SELECT item FROM inventory WHERE user_id = ? AND equipped = 1", (user_id,)) as cursor:
                rows = await cursor.fetchall()
                return [row['item'] for row in rows]
        finally:
            await conn.close()