from typing import Dict

from database.db_manager import DatabaseManager

class QuestService:
    """Handles quest-related operations"""
    
    @staticmethod
    async def get_available_quests(user_level: int) -> list[Dict]:
        """Get quests available for user's level"""
        conn = await DatabaseManager.get_connection()
        try:
            async with conn.execute("""
                SELECT quest_id, name, description, reward_coins, reward_xp, requirement_level
                FROM quests
                WHERE requirement_level <= ?
                ORDER BY requirement_level, quest_id
            """, (user_level,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        finally:
            await conn.close()
    
    @staticmethod
    async def get_active_quests(user_id: int) -> list[Dict]:
        """Get user's active quests with progress"""
        conn = await DatabaseManager.get_connection()
        try:
            async with conn.execute("""
                SELECT q.quest_id, q.name, q.description, q.reward_coins, q.reward_xp,
                       uq.status, uq.progress
                FROM user_quests uq
                JOIN quests q ON uq.quest_id = q.quest_id
                WHERE uq.user_id = ? AND uq.status = 'active'
            """, (user_id,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        finally:
            await conn.close()
    
    @staticmethod
    async def accept_quest(user_id: int, quest_id: int) -> Dict[str, any]:
        """Accept a quest"""
        conn = await DatabaseManager.get_connection()
        try:
            # Check if already accepted
            async with conn.execute("""
                SELECT status FROM user_quests WHERE user_id = ? AND quest_id = ?
            """, (user_id, quest_id)) as cursor:
                existing = await cursor.fetchone()
            
            if existing:
                if existing['status'] == 'active':
                    return {'success': False, 'error': 'Quest already active'}
                elif existing['status'] == 'completed':
                    return {'success': False, 'error': 'Quest already completed'}
            
            # Accept quest
            await conn.execute("""
                INSERT INTO user_quests (user_id, quest_id, status, progress)
                VALUES (?, ?, 'active', 0)
            """, (user_id, quest_id))
            await conn.commit()
            
            # Get quest details
            async with conn.execute("""
                SELECT name, description, reward_coins, reward_xp
                FROM quests WHERE quest_id = ?
            """, (quest_id,)) as cursor:
                quest = await cursor.fetchone()
            
            return {'success': True, 'quest': dict(quest)}
        finally:
            await conn.close()
    
    @staticmethod
    async def update_quest_progress(user_id: int, quest_type: str, amount: int = 1):
        """Update progress for quests of a certain type"""
        conn = await DatabaseManager.get_connection()
        try:
            # Map quest types to progress tracking
            type_mapping = {
                'adventure': 'adventure_count',
                'pvp': 'pvp_wins',
                'boss': 'boss_kills',
                'coins': 'balance'
            }
            
            if quest_type not in type_mapping:
                return
            
            stat_column = type_mapping[quest_type]
            
            # Get user's current stat
            async with conn.execute(f"""
                SELECT {stat_column} FROM users WHERE user_id = ?
            """, (user_id,)) as cursor:
                user_row = await cursor.fetchone()
            
            current_value = user_row[stat_column]
            
            # Update quest progress based on user's stats
            await conn.execute("""
                UPDATE user_quests
                SET progress = ?
                WHERE user_id = ? AND status = 'active'
                AND quest_id IN (
                    SELECT quest_id FROM quests WHERE quest_type = ?
                )
            """, (current_value, user_id, quest_type))
            await conn.commit()
            
            # Check for completion
            return await QuestService.check_quest_completion(user_id)
        finally:
            await conn.close()
    
    @staticmethod
    async def check_quest_completion(user_id: int) -> list[Dict]:
        """Check and return completed quests"""
        conn = await DatabaseManager.get_connection()
        try:
            # Find completed quests based on quest type requirements
            completed = []
            
            async with conn.execute("""
                SELECT uq.quest_id, q.name, q.reward_coins, q.reward_xp, q.quest_type,
                       uq.progress, u.adventure_count, u.pvp_wins, u.boss_kills, u.balance
                FROM user_quests uq
                JOIN quests q ON uq.quest_id = q.quest_id
                JOIN users u ON uq.user_id = u.user_id
                WHERE uq.user_id = ? AND uq.status = 'active'
            """, (user_id,)) as cursor:
                quests = await cursor.fetchall()
            
            for quest in quests:
                # Check if quest requirement is met
                requirement_met = False
                
                if 'adventure' in quest['name'].lower() or quest['quest_type'] == 'adventure':
                    # Extract number from description (e.g., "Complete 5 adventures")
                    import re
                    match = re.search(r'(\d+)', quest['name'])
                    if match:
                        required = int(match.group(1))
                        if quest['adventure_count'] >= required:
                            requirement_met = True
                
                elif 'pvp' in quest['name'].lower() or quest['quest_type'] == 'pvp':
                    match = re.search(r'(\d+)', quest['name'])
                    if match:
                        required = int(match.group(1))
                        if quest['pvp_wins'] >= required:
                            requirement_met = True
                
                elif 'boss' in quest['name'].lower() or quest['quest_type'] == 'boss':
                    match = re.search(r'(\d+)', quest['name'])
                    if match:
                        required = int(match.group(1))
                        if quest['boss_kills'] >= required:
                            requirement_met = True
                
                elif 'coin' in quest['name'].lower() or quest['quest_type'] == 'coins':
                    match = re.search(r'(\d+)', quest['name'])
                    if match:
                        required = int(match.group(1))
                        if quest['balance'] >= required:
                            requirement_met = True
                
                if requirement_met:
                    # Mark as completed
                    await conn.execute("""
                        UPDATE user_quests SET status = 'completed'
                        WHERE user_id = ? AND quest_id = ?
                    """, (user_id, quest['quest_id']))
                    
                    # Award rewards
                    await conn.execute("""
                        UPDATE users
                        SET balance = balance + ?, xp = xp + ?
                        WHERE user_id = ?
                    """, (quest['reward_coins'], quest['reward_xp'], user_id))
                    
                    completed.append({
                        'name': quest['name'],
                        'reward_coins': quest['reward_coins'],
                        'reward_xp': quest['reward_xp']
                    })
            
            await conn.commit()
            return completed
        finally:
            await conn.close()