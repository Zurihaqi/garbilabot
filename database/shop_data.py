class ShopData:
    """Unique shop items for RPG"""

    ITEMS = [
        # Consumables
        ("Minor Health Potion", "Restores 25 HP", 25, "consumable", "hp", 25, 1),
        ("Health Potion", "Restores 50 HP", 50, "consumable", "hp", 50, 2),
        ("Greater Health Potion", "Restores 100 HP", 100, "consumable", "hp", 100, 4),
        ("Mana Potion", "Restores 30 MP", 30, "consumable", "mp", 30, 1),
        ("Greater Mana Potion", "Restores 70 MP", 70, "consumable", "mp", 70, 3),
        ("Stamina Drink", "Restores 50 Stamina", 40, "consumable", "stamina", 50, 2),
        ("Energy Elixir", "Fully restores HP & MP", 200, "consumable", "hp", 999, 6),
        ("Antidote", "Cures poison", 35, "consumable", "hp", 0, 1),
        ("Revive Scroll", "Revives a fallen ally", 300, "consumable", "hp", 100, 5),
        ("Strength Tonic", "Boosts attack for 1 hour", 150, "consumable", "attack", 10, 4),

        # Weapons
        ("Iron Sword", "Basic sword for beginners", 100, "weapon", "attack", 5, 1),
        ("Steel Sword", "Stronger than iron", 250, "weapon", "attack", 10, 3),
        ("Silver Saber", "Lightweight and sharp", 350, "weapon", "attack", 12, 4),
        ("Golden Blade", "Shiny legendary sword", 600, "weapon", "attack", 20, 6),
        ("Dragon Slayer", "Massive damage to dragons", 1200, "weapon", "attack", 35, 10),
        ("Crystal Dagger", "Fast and precise", 200, "weapon", "attack", 8, 2),
        ("Obsidian Axe", "Heavy and brutal", 500, "weapon", "attack", 18, 5),
        ("Thunder Hammer", "Strikes with thunder", 800, "weapon", "attack", 25, 7),
        ("Flame Katana", "Burns enemies with fire", 750, "weapon", "attack", 22, 6),
        ("Ice Spear", "Slows enemies", 700, "weapon", "attack", 20, 6),

        # Armor
        ("Leather Armor", "Basic protection", 150, "armor", "defense", 3, 1),
        ("Chain Mail", "Medium protection", 350, "armor", "defense", 8, 3),
        ("Steel Plate", "Heavy protection", 600, "armor", "defense", 12, 5),
        ("Dragon Scale Armor", "Legendary protection", 1500, "armor", "defense", 25, 10),
        ("Mystic Robe", "Boosts magic defense", 500, "armor", "defense", 10, 4),
        ("Shadow Cloak", "Increases evasion", 400, "armor", "defense", 8, 3),
        ("Golden Helm", "Protects the head", 250, "armor", "defense", 5, 2),
        ("Silver Shield", "Blocks attacks", 300, "armor", "defense", 7, 3),
        ("Titanium Gauntlets", "Increases attack slightly", 350, "armor", "attack", 5, 4),
        ("Phoenix Feather Cape", "Revives once per day", 1200, "armor", "hp", 50, 8),

        # Additional Consumables
        ("Elixir of Vitality", "Restore 200 HP", 180, "consumable", "hp", 200, 5),
        ("Potion of Agility", "Boosts speed temporarily", 120, "consumable", "speed", 5, 3),
        ("Potion of Fortitude", "Boosts defense temporarily", 130, "consumable", "defense", 5, 3),
        ("Potion of Wisdom", "Boosts XP gain for 1 hour", 150, "consumable", "xp_bonus", 10, 4),
        ("Mega Health Potion", "Restores 500 HP", 500, "consumable", "hp", 500, 8),
        ("Mega Mana Potion", "Restores 500 MP", 500, "consumable", "mp", 500, 8),
        ("Potion of Luck", "Increases drop rates temporarily", 250, "consumable", "luck", 5, 5),
        ("Potion of Courage", "Boosts attack and defense", 300, "consumable", "attack", 10, 5),
        ("Potion of Precision", "Boosts critical chance", 200, "consumable", "crit", 5, 4),
        ("Potion of Recovery", "Gradually restores HP over time", 220, "consumable", "hp", 150, 4),

        # Additional Weapons (unique)
        ("Bone Club", "Primitive weapon", 50, "weapon", "attack", 3, 1),
        ("Elven Longbow", "Long range attacks", 400, "weapon", "attack", 15, 5),
        ("Dwarven Warhammer", "Heavy and devastating", 600, "weapon", "attack", 22, 6),
        ("Vampire Fang Blade", "Leeches health", 900, "weapon", "attack", 28, 8),
        ("Thunder Staff", "Casts lightning spells", 700, "weapon", "attack", 20, 7),
        ("Ice Wand", "Casts frost spells", 650, "weapon", "attack", 18, 6),
        ("Fire Staff", "Casts fire spells", 650, "weapon", "attack", 18, 6),
        ("Shadow Blade", "Deals extra damage at night", 850, "weapon", "attack", 25, 8),
        ("Sun Sword", "Effective against undead", 900, "weapon", "attack", 27, 9),
        ("Cursed Dagger", "High risk, high reward", 500, "weapon", "attack", 20, 5),

        # Additional Armor (unique)
        ("Iron Helm", "Basic head protection", 100, "armor", "defense", 4, 1),
        ("Steel Boots", "Protects feet", 150, "armor", "defense", 5, 2),
        ("Chain Gloves", "Protects hands", 120, "armor", "defense", 4, 2),
        ("Dragon Helm", "Protects from fire", 800, "armor", "defense", 18, 8),
        ("Titanium Chestplate", "Heavy and strong", 900, "armor", "defense", 20, 9),
        ("Shadow Greaves", "Increase evasion", 600, "armor", "defense", 12, 6),
        ("Golden Armor", "Shiny and protective", 1200, "armor", "defense", 25, 10),
        ("Crystal Shield", "Blocks magical attacks", 700, "armor", "defense", 15, 7),
        ("Mystic Helmet", "Increases magic power", 500, "armor", "defense", 10, 5),
        ("Phantom Cloak", "Evade physical attacks", 650, "armor", "defense", 12, 6),

        # More consumables
        ("Potion of Vigor", "Boosts HP regen", 180, "consumable", "hp_regen", 5, 4),
        ("Potion of Clarity", "Boosts mana regen", 180, "consumable", "mp_regen", 5, 4),
        ("Potion of Giants", "Increases max HP", 300, "consumable", "max_hp", 50, 6),
        ("Potion of Titans", "Greatly increases max HP", 500, "consumable", "max_hp", 100, 8),
        ("Potion of Shadows", "Boosts stealth", 250, "consumable", "stealth", 5, 5),
        ("Potion of Light", "Boosts defense temporarily", 220, "consumable", "defense", 5, 5),
        ("Potion of Speed", "Boosts movement speed", 200, "consumable", "speed", 5, 4),
        ("Potion of Fire Resistance", "Reduces fire damage", 180, "consumable", "fire_resist", 5, 4),
        ("Potion of Ice Resistance", "Reduces ice damage", 180, "consumable", "ice_resist", 5, 4),
        ("Potion of Thunder Resistance", "Reduces lightning damage", 180, "consumable", "lightning_resist", 5, 4),

        # Finish with more weapons and armor to reach 100
        ("Sapphire Blade", "Magical sword", 1000, "weapon", "attack", 30, 10),
        ("Emerald Staff", "Magic staff of power", 950, "weapon", "attack", 28, 9),
        ("Ruby Shield", "Blocks physical attacks", 800, "armor", "defense", 20, 8),
        ("Onyx Armor", "Dark and durable", 900, "armor", "defense", 22, 9),
        ("Topaz Dagger", "Fast and deadly", 600, "weapon", "attack", 18, 6),
        ("Pearl Necklace", "Increases magic defense", 500, "armor", "defense", 12, 5),
        ("Amethyst Helm", "Protects the head", 450, "armor", "defense", 10, 4),
        ("Diamond Sword", "Legendary weapon", 2000, "weapon", "attack", 40, 12),
        ("Obsidian Armor", "Legendary armor", 1800, "armor", "defense", 35, 12),
    ]

    @staticmethod
    async def initialize_shop(conn):
        """Add missing items to the shop without wiping the table"""
        await conn.executemany(
            """
            INSERT OR IGNORE INTO shop (item, description, price, item_type, stat_bonus, bonus_value, level_req)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            ShopData.ITEMS
        )
