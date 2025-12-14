from dataclasses import dataclass

@dataclass
class Item:
    """Item data model"""
    name: str
    description: str
    price: int
    item_type: str
    stat_bonus: str
    bonus_value: int
    level_req: int
    
    def is_consumable(self) -> bool:
        return self.item_type == 'consumable'
    
    def is_equipment(self) -> bool:
        return self.item_type in ('weapon', 'armor')