from datetime import datetime, timedelta
from typing import Optional

class CooldownManager:
    """Manages command cooldowns"""
    
    def __init__(self):
        self.cooldowns = {}
    
    def check_cooldown(self, user_id: int, command: str, cooldown_seconds: int) -> Optional[int]:
        """Check if user is on cooldown. Returns seconds remaining or None"""
        key = f"{user_id}_{command}"
        if key in self.cooldowns:
            elapsed = (datetime.now() - self.cooldowns[key]).total_seconds()
            if elapsed < cooldown_seconds:
                return int(cooldown_seconds - elapsed)
        self.cooldowns[key] = datetime.now()
        return None
    
    def reset_cooldown(self, user_id: int, command: str):
        """Reset a specific cooldown"""
        key = f"{user_id}_{command}"
        if key in self.cooldowns:
            del self.cooldowns[key]