import random
from typing import Dict, Any

class GameLogic:
    """Game logic and calculations"""
    
    @staticmethod
    def calculate_level_xp(level: int) -> int:
        """Calculate XP needed for next level"""
        return int(100 * (1.5 ** (level - 1)))
    
    @staticmethod
    def get_class_for_level(level: int) -> str:
        """Get class name for level"""
        if level >= 50: return "Legendary Hero"
        if level >= 40: return "Dragon Slayer"
        if level >= 30: return "Master"
        if level >= 20: return "Champion"
        if level >= 15: return "Knight"
        if level >= 10: return "Warrior"
        if level >= 5: return "Adventurer"
        return "Novice"
    
    @staticmethod
    def get_level_stats(level: int) -> Dict[str, Any]:
        """Get stats for a level"""
        return {
            'class': GameLogic.get_class_for_level(level),
            'max_hp': 100 + (level - 1) * 10,
            'attack': 10 + (level - 1) * 2,
            'defense': 5 + (level - 1)
        }
    
    @staticmethod
    def calculate_battle_power(attack: int, level: int) -> int:
        """Calculate battle power"""
        return attack * random.randint(8, 12) + level * 5
    
    @staticmethod
    def calculate_heal_cost(level: int) -> int:
        """Calculate healing cost"""
        return 50 + level * 5
