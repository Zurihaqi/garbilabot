class ShopData:
    """Shop initialization data"""
    
    ITEMS = [
        ("Health Potion", "Restores 50 HP", 25, "consumable", "hp", 50, 1),
        ("Iron Sword", "Basic sword", 100, "weapon", "attack", 5, 1),
        ("Leather Armor", "Basic armor", 150, "armor", "defense", 3, 1),
        ("Steel Sword", "Strong sword", 300, "weapon", "attack", 10, 5),
        ("Chain Mail", "Medium armor", 400, "armor", "defense", 8, 5),
        ("Excalibur", "Legendary sword", 1000, "weapon", "attack", 25, 10),
        ("Dragon Scale", "Ultimate armor", 1500, "armor", "defense", 20, 15),
        ("Elixir", "Full HP restore", 100, "consumable", "hp", 999, 3),
    ]
    
    @staticmethod
    def initialize_shop(cursor):
        cursor.executemany(
            "INSERT OR IGNORE INTO shop VALUES (?, ?, ?, ?, ?, ?, ?)",
            ShopData.ITEMS
        )
