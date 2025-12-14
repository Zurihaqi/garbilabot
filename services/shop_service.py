from typing import List, Dict, Any, Optional
from services.inventory_service import InventoryService
from database.db_manager import DatabaseManager

class ShopService:
    """Handles shop operations"""
    
    @staticmethod
    def get_all_items() -> List[Dict]:
        """Get all shop items"""
        with DatabaseManager.get_connection() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT item, description, price, item_type, bonus_value, stat_bonus, level_req
                FROM shop ORDER BY level_req, price
            """)
            return [dict(row) for row in c.fetchall()]
    
    @staticmethod
    def get_item(item_name: str) -> Optional[Dict]:
        """Get specific item"""
        with DatabaseManager.get_connection() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT item, description, price, item_type, stat_bonus, bonus_value, level_req
                FROM shop WHERE item = ?
            """, (item_name,))
            row = c.fetchone()
            return dict(row) if row else None
    
    @staticmethod
    def purchase_item(user_id: int, item_name: str) -> Dict[str, Any]:
        """Purchase an item"""
        with DatabaseManager.get_connection() as conn:
            c = conn.cursor()
            
            # Get item
            item = ShopService.get_item(item_name)
            if not item:
                return {'success': False, 'error': 'Item not found'}
            
            # Get user
            c.execute("SELECT balance, level FROM users WHERE user_id = ?", (user_id,))
            user = c.fetchone()
            
            # Validate
            if user['level'] < item['level_req']:
                return {'success': False, 'error': f"Need level {item['level_req']}"}
            
            if user['balance'] < item['price']:
                return {'success': False, 'error': f"Need {item['price']:,} coins"}
            
            # Purchase
            c.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?",
                     (item['price'], user_id))
            InventoryService.add_item(user_id, item_name, 1)
            
            return {'success': True, 'item': item}