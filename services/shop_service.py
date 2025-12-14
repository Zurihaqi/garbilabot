from typing import Optional, Dict, Any
from database.db_manager import DatabaseManager

class ShopService:
    """Handles shop operations"""
    
    @staticmethod
    async def get_all_items() -> list[Dict]:
        """Get all shop items"""
        conn = await DatabaseManager.get_connection()
        try:
            async with conn.execute("""
                SELECT item, description, price, item_type, bonus_value, stat_bonus, level_req
                FROM shop ORDER BY level_req, price
            """) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        finally:
            await conn.close()
    
    @staticmethod
    async def get_item(item_name: str) -> Optional[Dict]:
        """Get specific item"""
        conn = await DatabaseManager.get_connection()
        try:
            async with conn.execute("""
                SELECT item, description, price, item_type, stat_bonus, bonus_value, level_req
                FROM shop WHERE item = ?
            """, (item_name,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
        finally:
            await conn.close()
    
    @staticmethod
    async def purchase_item(user_id: int, item_name: str) -> Dict[str, Any]:
        """Purchase an item"""
        conn = await DatabaseManager.get_connection()
        try:
            # Get item
            item = await ShopService.get_item(item_name)
            if not item:
                return {'success': False, 'error': 'Item not found'}
            
            # Get user
            async with conn.execute("SELECT balance, level FROM users WHERE user_id = ?", (user_id,)) as cursor:
                user = await cursor.fetchone()
            
            # Validate
            if user['level'] < item['level_req']:
                return {'success': False, 'error': f"Need level {item['level_req']}"}
            
            if user['balance'] < item['price']:
                return {'success': False, 'error': f"Need {item['price']:,} coins"}
            
            # Purchase
            await conn.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?",
                             (item['price'], user_id))
            
            # Add to inventory
            await conn.execute("""
                INSERT INTO inventory (user_id, item, quantity)
                VALUES (?, ?, 1)
                ON CONFLICT(user_id, item) DO UPDATE SET quantity = quantity + 1
            """, (user_id, item_name))
            
            await conn.commit()
            return {'success': True, 'item': item}
        finally:
            await conn.close()