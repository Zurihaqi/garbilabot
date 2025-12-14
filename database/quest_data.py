class QuestData:
    """Quest initialization data"""

    QUESTS = [
        # Adventure Quests
        ("Novice Explorer", "Complete 5 adventures", 100, 50, 1, "adventure"),
        ("Adventurer", "Complete 20 adventures", 500, 200, 5, "adventure"),
        ("Veteran Adventurer", "Complete 50 adventures", 1500, 600, 10, "adventure"),
        ("Master Explorer", "Complete 100 adventures", 3000, 1200, 15, "adventure"),
        ("Legendary Explorer", "Complete 200 adventures", 7000, 2500, 20, "adventure"),
        ("Dungeon Crawler", "Clear 5 dungeons", 400, 200, 3, "adventure"),
        ("Dungeon Master", "Clear 20 dungeons", 1500, 800, 10, "adventure"),
        ("Ancient Ruins", "Explore 5 ancient ruins", 600, 300, 5, "adventure"),
        ("Mystic Wanderer", "Explore 20 mystic locations", 2000, 1000, 12, "adventure"),
        ("World Traveler", "Visit 50 unique locations", 5000, 2500, 20, "adventure"),

        # PvP Quests
        ("Warrior Initiate", "Win 5 PvP battles", 300, 150, 3, "pvp"),
        ("Champion", "Win 20 PvP battles", 1000, 500, 10, "pvp"),
        ("PvP Master", "Win 50 PvP battles", 3000, 1500, 15, "pvp"),
        ("Gladiator", "Win 100 PvP battles", 7000, 3500, 20, "pvp"),
        ("Arena Legend", "Win 200 PvP battles", 15000, 7000, 25, "pvp"),
        ("Duelist", "Win 10 duels", 500, 250, 5, "pvp"),
        ("Elite Duelist", "Win 50 duels", 2000, 1000, 12, "pvp"),
        ("PvP Conqueror", "Win 150 duels", 8000, 4000, 20, "pvp"),
        ("Champion of the Arena", "Reach PvP rank 10", 5000, 2500, 15, "pvp"),
        ("PvP Legend", "Reach PvP rank 20", 12000, 6000, 25, "pvp"),

        # Coins / Wealth Quests
        ("Treasure Hunter", "Collect 1000 coins", 200, 100, 1, "coins"),
        ("Wealthy Merchant", "Collect 5000 coins", 800, 400, 8, "coins"),
        ("Coin Collector", "Collect 10000 coins", 2000, 1000, 12, "coins"),
        ("Rich Trader", "Collect 50000 coins", 8000, 4000, 18, "coins"),
        ("Tycoon", "Collect 100000 coins", 20000, 10000, 25, "coins"),
        ("Hoarder", "Collect 250000 coins", 50000, 25000, 30, "coins"),
        ("Banker", "Collect 500000 coins", 100000, 50000, 35, "coins"),
        ("Magnate", "Collect 1,000,000 coins", 250000, 125000, 40, "coins"),
        ("Legendary Collector", "Collect 2,500,000 coins", 500000, 250000, 45, "coins"),
        ("Ultimate Wealth", "Collect 5,000,000 coins", 1000000, 500000, 50, "coins"),

        # Boss Quests
        ("Dragon Apprentice", "Defeat 5 bosses", 600, 300, 10, "boss"),
        ("Boss Slayer", "Defeat 20 bosses", 2000, 1000, 15, "boss"),
        ("Legendary Hunter", "Defeat 50 bosses", 5000, 2500, 20, "boss"),
        ("Elite Boss Slayer", "Defeat 100 bosses", 12000, 6000, 25, "boss"),
        ("Mythic Conqueror", "Defeat 200 bosses", 25000, 12500, 30, "boss"),
        ("Titan Vanquisher", "Defeat 300 bosses", 50000, 25000, 35, "boss"),
        ("Ultimate Boss Hunter", "Defeat 500 bosses", 100000, 50000, 40, "boss"),
        ("Champion of the Titans", "Defeat 750 bosses", 200000, 100000, 45, "boss"),
        ("Legend of Legends", "Defeat 1000 bosses", 500000, 250000, 50, "boss"),
        ("Godslayer", "Defeat 2000 bosses", 1000000, 500000, 55, "boss"),

        # Collection / Crafting Quests
        ("Herbalist", "Collect 10 herbs", 100, 50, 1, "collection"),
        ("Potion Brewer", "Collect 50 herbs", 500, 200, 5, "collection"),
        ("Master Alchemist", "Collect 100 rare herbs", 1500, 600, 10, "collection"),
        ("Weapon Collector", "Collect 10 unique weapons", 800, 400, 5, "collection"),
        ("Armor Collector", "Collect 10 unique armors", 800, 400, 5, "collection"),
        ("Rare Collector", "Collect 50 rare items", 2000, 1000, 10, "collection"),
        ("Legendary Collector", "Collect 100 legendary items", 5000, 2500, 15, "collection"),
        ("Artifact Hunter", "Collect 5 ancient artifacts", 2500, 1250, 12, "collection"),
        ("Treasure Collector", "Collect 50 treasures", 4000, 2000, 18, "collection"),
        ("Ultimate Collector", "Collect 100 unique items", 10000, 5000, 25, "collection"),

        # Exploration Quests
        ("Forest Explorer", "Explore 5 forests", 200, 100, 1, "exploration"),
        ("Mountain Explorer", "Explore 5 mountains", 200, 100, 2, "exploration"),
        ("Cave Explorer", "Explore 5 caves", 250, 150, 3, "exploration"),
        ("Desert Explorer", "Explore 5 deserts", 300, 150, 4, "exploration"),
        ("Swamp Explorer", "Explore 5 swamps", 300, 150, 4, "exploration"),
        ("Volcano Explorer", "Explore 3 volcanoes", 400, 200, 6, "exploration"),
        ("Ocean Explorer", "Explore 5 oceans", 500, 250, 7, "exploration"),
        ("Sky Explorer", "Explore 3 sky islands", 600, 300, 8, "exploration"),
        ("Mystic Explorer", "Explore 5 mystical places", 800, 400, 10, "exploration"),
        ("Legendary Explorer", "Explore 10 legendary places", 1500, 800, 12, "exploration"),

        # Miscellaneous Quests
        ("Craftsman", "Craft 5 items", 300, 150, 2, "crafting"),
        ("Master Craftsman", "Craft 20 items", 1200, 600, 8, "crafting"),
        ("Grand Master Craftsman", "Craft 50 items", 3500, 1500, 15, "crafting"),
        ("Treasure Finder", "Open 10 chests", 400, 200, 3, "misc"),
        ("Grand Treasure Finder", "Open 50 chests", 2000, 1000, 10, "misc"),
        ("Dungeon Conqueror", "Complete 5 dungeons", 500, 250, 5, "misc"),
        ("Dungeon Master", "Complete 20 dungeons", 2000, 1000, 12, "misc"),
        ("Puzzle Solver", "Solve 5 puzzles", 300, 150, 3, "misc"),
        ("Legendary Solver", "Solve 20 puzzles", 1500, 750, 10, "misc"),
        ("Ultimate Challenger", "Complete 50 random challenges", 5000, 2500, 20, "misc"),

        # Repeat for variety to reach 100 quests
        ("Explorer of the Unknown", "Explore 50 unknown locations", 3000, 1500, 15, "exploration"),
        ("Hero of the Village", "Help villagers 10 times", 800, 400, 5, "misc"),
        ("Champion of the Arena", "Win 50 arena matches", 3000, 1500, 15, "pvp"),
        ("Conqueror of the Sea", "Defeat 10 sea bosses", 4000, 2000, 18, "boss"),
        ("Guardian of the Forest", "Protect 5 forests from monsters", 1500, 750, 10, "misc"),
        ("Slayer of Shadows", "Defeat 20 shadow enemies", 2500, 1250, 12, "misc"),
        ("Collector of Rare Coins", "Collect 500 rare coins", 2000, 1000, 12, "coins"),
        ("Champion of Crafting", "Craft 100 items", 5000, 2500, 18, "crafting"),
        ("Master of PvP", "Win 200 PvP battles", 10000, 5000, 20, "pvp"),
        ("Legendary Adventurer", "Complete 500 adventures", 20000, 10000, 25, "adventure"),
        ("Boss Conqueror", "Defeat 1000 bosses", 50000, 25000, 30, "boss"),
        ("Ultimate Explorer", "Explore all locations", 100000, 50000, 35, "exploration"),
        ("Hero of Legends", "Complete 200 legendary quests", 250000, 125000, 40, "misc"),
        ("PvP God", "Win 500 PvP battles", 500000, 250000, 45, "pvp"),
        ("Collector of the Ages", "Collect 10000 items", 1000000, 500000, 50, "collection"),
        ("Champion of Treasure", "Open 1000 chests", 2000000, 1000000, 50, "misc"),
        ("Dragon Master", "Defeat all dragons", 3000000, 1500000, 55, "boss"),
        ("Ultimate Hero", "Reach level 100", 5000000, 2500000, 60, "level"),
        ("Legend of the Realm", "Complete all main quests", 10000000, 5000000, 60, "story")
    ]

    @staticmethod
    async def initialize_quests(conn):
        """Add missing quests without deleting existing ones"""
        await conn.executemany(
            """
            INSERT OR IGNORE INTO quests (name, description, reward_coins, reward_xp, requirement_level, quest_type)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            QuestData.QUESTS
        )
