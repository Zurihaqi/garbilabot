from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    """User data model"""
    user_id: int
    username: str
    balance: int = 0
    level: int = 1
    xp: int = 0
    cls: str = 'Novice'
    hp: int = 100
    max_hp: int = 100
    attack: int = 10
    defense: int = 5
    adventure_count: int = 0
    pvp_wins: int = 0
    pvp_losses: int = 0
    boss_kills: int = 0
    
    @property
    def win_rate(self) -> float:
        total = self.pvp_wins + self.pvp_losses
        return (self.pvp_wins / total * 100) if total > 0 else 0
    
    def is_alive(self) -> bool:
        return self.hp > 0
    
    def is_full_hp(self) -> bool:
        return self.hp >= self.max_hp
