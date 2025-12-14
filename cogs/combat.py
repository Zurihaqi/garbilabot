import random
from datetime import datetime
from typing import Dict

import discord
from discord import app_commands, Embed, Color
from discord.ext import commands

from utils.cooldown_manager import CooldownManager
from utils.game_logic import GameLogic
from database.db_manager import DatabaseManager
from services.user_service import UserService
from models.user import User
from utils.game_logic import GameLogic
from services.quest_service import QuestService
from view.pvp import PvPChallengeView
from database.adventure_data import ADVENTURE_OUTCOMES

class CombatCommands(commands.Cog):
    """Combat and adventure commands"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cooldown_manager = CooldownManager()
        self.active_pvp_challenges: Dict[int, PvPChallengeView] = {}
    
    @app_commands.command(name="adventure", description="Go on adventure")
    async def adventure(self, interaction: discord.Interaction):
        cd = self.cooldown_manager.check_cooldown(interaction.user.id, "adventure", 300)
        if cd:
            await interaction.response.send_message(f"⏳ Cooldown: {cd}s", ephemeral=True)
            return
        
        await UserService.ensure_user_exists(interaction.user.id, interaction.user.name)
        user = await UserService.get_user(interaction.user.id)
        
        if not user.is_alive():
            await interaction.response.send_message("💀 Too injured!", ephemeral=True)
            return
        
        # Boss encounter (10% at lv10+)
        if user.level >= 10 and random.random() < 0.1:
            result = await self._boss_encounter(user, interaction.user.id)
            await interaction.response.send_message(embed=result)
        else:
            # Regular adventure
            result = await self._regular_adventure(user, interaction.user.id)
            await interaction.response.send_message(embed=result)
        
        # Update quest progress
        await QuestService.update_quest_progress(interaction.user.id, 'adventure')
        
        # Check for completed quests
        completed = await QuestService.check_quest_completion(interaction.user.id)
        if completed:
            quest_text = "\n".join([
                f"✅ **{q['name']}** - {q['reward_coins']} coins, {q['reward_xp']} XP"
                for q in completed
            ])
            await interaction.followup.send(
                f"🎊 **Quest Completed!**\n{quest_text}",
                ephemeral=False
            )
    
    async def _boss_encounter(self, user: User, user_id: int) -> Embed:
        """Handle boss encounter"""
        boss_hp = 50 + user.level * 5
        player_power = user.attack + random.randint(5, 15)
        boss_power = 10 + user.level * 2 + random.randint(0, 10)
        dmg = max(0, boss_power - user.defense)
        
        if player_power >= boss_hp:
            # Victory
            reward_coins = 100 + user.level * 20
            reward_xp = 50 + user.level * 10
            new_hp = max(0, user.hp - dmg)
            
            conn = await DatabaseManager.get_connection()
            try:
                await conn.execute("""
                    UPDATE users
                    SET balance = balance + ?, xp = xp + ?, hp = ?,
                        adventure_count = adventure_count + 1, boss_kills = boss_kills + 1
                    WHERE user_id = ?
                """, (reward_coins, reward_xp, new_hp, user_id))
                await conn.commit()
            finally:
                await conn.close()
            
            # Update boss quest progress
            await QuestService.update_quest_progress(user_id, 'boss')
            
            embed = Embed(title="🐉 BOSS DEFEATED!", description="Mighty boss slain!", color=Color.red())
            embed.add_field(name="Rewards", value=f"💰 {reward_coins} coins\n✨ {reward_xp} XP")
            embed.add_field(name="Damage", value=f"💔 -{dmg} HP")
            return embed
        else:
            # Defeat
            new_hp = max(0, user.hp - dmg * 2)
            await UserService.update_user_stats(user_id, hp=new_hp, adventure_count=user.adventure_count + 1)
            
            embed = Embed(title="💀 Boss Victory", description=f"You were defeated! Lost {dmg*2} HP.", color=Color.dark_red())
            return embed
    
    async def _regular_adventure(self, user: User, user_id: int) -> Embed:
        """Handle regular adventure"""

        outcome = random.choice(ADVENTURE_OUTCOMES)
        coins = random.randint(*outcome['c'])
        xp = random.randint(*outcome['x'])
        hp_change = random.randint(*outcome['h'])
        
        new_hp = max(0, min(user.hp + hp_change, user.max_hp))
        
        # Update with XP/level handling
        result = await UserService.add_xp_and_coins(user_id, xp, coins)
        await UserService.update_user_stats(
            user_id,
            hp=new_hp,
            adventure_count=user.adventure_count + 1
        )
        
        embed = Embed(title="🗺️ Adventure", description=outcome['desc'], color=Color.orange())
        embed.add_field(name="Rewards", value=f"💰 {coins} coins\n✨ {xp} XP")
        embed.add_field(name="HP", value=f"❤️ {hp_change:+d}")
        
        if result['leveled_up']:
            embed.add_field(name="🎉 LEVEL UP!", value=f"Now level {result['new_level']}!", inline=False)
        
        return embed
    
    @app_commands.command(name="pvp", description="Challenge player to PvP")
    async def pvp(self, interaction: discord.Interaction, target: discord.User):
        if target.bot:
            await interaction.response.send_message("❌ Can't fight bots!", ephemeral=True)
            return
        
        if target.id == interaction.user.id:
            await interaction.response.send_message("❌ Can't fight yourself!", ephemeral=True)
            return
        
        # Check if target already has pending challenge
        if target.id in self.active_pvp_challenges:
            await interaction.response.send_message(
                f"❌ {target.mention} already has a pending challenge!",
                ephemeral=True
            )
            return
        
        cd = self.cooldown_manager.check_cooldown(interaction.user.id, "pvp", 600)
        if cd:
            await interaction.response.send_message(f"⏳ PvP cooldown: {cd}s", ephemeral=True)
            return
        
        await UserService.ensure_user_exists(interaction.user.id, interaction.user.name)
        await UserService.ensure_user_exists(target.id, target.name)
        
        attacker = await UserService.get_user(interaction.user.id)
        defender = await UserService.get_user(target.id)
        
        if not attacker.is_alive():
            await interaction.response.send_message("💀 You're too injured!", ephemeral=True)
            return
        
        if not defender.is_alive():
            await interaction.response.send_message("💀 Target is too injured!", ephemeral=True)
            return
        
        # Create challenge view
        view = PvPChallengeView(interaction.user, target, timeout=60)
        self.active_pvp_challenges[target.id] = view
        
        # Send challenge
        embed = Embed(
            title="⚔️ PvP Challenge!",
            description=f"{interaction.user.mention} challenges {target.mention} to battle!",
            color=Color.orange()
        )
        embed.add_field(name=f"{interaction.user.name}", value=f"Level {attacker.level}\nHP: {attacker.hp}/{attacker.max_hp}\nAttack: {attacker.attack}", inline=True)
        embed.add_field(name=f"{target.name}", value=f"Level {defender.level}\nHP: {defender.hp}/{defender.max_hp}\nAttack: {defender.attack}", inline=True)
        embed.set_footer(text=f"{target.name} has 60 seconds to respond")
        
        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_response()
        
        # Wait for response
        await view.wait()
        
        # Remove from active challenges
        if target.id in self.active_pvp_challenges:
            del self.active_pvp_challenges[target.id]
        
        # If declined or timed out
        if not view.accepted:
            return
        
        # Proceed with battle
        await self._execute_pvp_battle(interaction, attacker, defender, target)
    
    async def _execute_pvp_battle(
        self,
        interaction: discord.Interaction,
        attacker: User,
        defender: User,
        target: discord.User
    ):
        """Execute the actual PvP battle"""
        # Calculate battle
        a_power = GameLogic.calculate_battle_power(attacker.attack, attacker.level)
        d_power = GameLogic.calculate_battle_power(defender.attack, defender.level)
        
        winner_id = interaction.user.id if a_power >= d_power else target.id
        loser_id = target.id if winner_id == interaction.user.id else interaction.user.id
        
        dmg = abs(a_power - d_power) // 10
        loser_hp = max(0, (attacker.hp if loser_id == interaction.user.id else defender.hp) - dmg)
        
        # Update database
        conn = await DatabaseManager.get_connection()
        try:
            await conn.execute("UPDATE users SET hp = ? WHERE user_id = ?", (loser_hp, loser_id))
            await conn.execute("UPDATE users SET pvp_wins = pvp_wins + 1 WHERE user_id = ?", (winner_id,))
            await conn.execute("UPDATE users SET pvp_losses = pvp_losses + 1 WHERE user_id = ?", (loser_id,))
            await conn.execute("""
                INSERT INTO pvp (attacker_id, defender_id, winner_id, timestamp, attacker_power, defender_power)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (interaction.user.id, target.id, winner_id, datetime.now().isoformat(), a_power, d_power))
            await conn.commit()
        finally:
            await conn.close()
        
        # Update quest progress
        await QuestService.update_quest_progress(winner_id, 'pvp')
        
        winner = interaction.user if winner_id == interaction.user.id else target
        
        embed = Embed(title="⚔️ PvP Battle Results!", color=Color.red())
        embed.add_field(name="Combatants", value=f"{interaction.user.mention} vs {target.mention}", inline=False)
        embed.add_field(name="Powers", value=f"{interaction.user.name}: {a_power}\n{target.name}: {d_power}")
        embed.add_field(name="Result", value=f"🏆 Winner: {winner.mention}\n💔 Damage: {dmg} HP")
        
        await interaction.followup.send(embed=embed)
        
        # Check for quest completion
        completed = await QuestService.check_quest_completion(winner_id)
        if completed:
            quest_text = "\n".join([
                f"✅ **{q['name']}** - {q['reward_coins']} coins, {q['reward_xp']} XP"
                for q in completed
            ])
            await interaction.followup.send(
                f"🎊 **{winner.mention} completed a quest!**\n{quest_text}",
                ephemeral=False
            )
    
    @app_commands.command(name="quests", description="View and manage quests")
    async def quests(self, interaction: discord.Interaction):
        await UserService.ensure_user_exists(interaction.user.id, interaction.user.name)
        await UserService.get_user(interaction.user.id)
        
        # Get active quests
        active = await QuestService.get_active_quests(interaction.user.id)
        
        embed = Embed(title="📜 Your Quests", color=Color.blue())
        
        if active:
            active_text = "\n".join([
                f"**{q['name']}**\n{q['description']}\n💰 {q['reward_coins']} coins | ✨ {q['reward_xp']} XP\n"
                for q in active
            ])
            embed.add_field(name="🔄 Active Quests", value=active_text, inline=False)
        else:
            embed.add_field(name="🔄 Active Quests", value="No active quests", inline=False)
        
        embed.set_footer(text="Use /questboard to see available quests")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="questboard", description="View available quests")
    async def questboard(self, interaction: discord.Interaction):
        await UserService.ensure_user_exists(interaction.user.id, interaction.user.name)
        user = await UserService.get_user(interaction.user.id)
        
        # Get available quests
        available = await QuestService.get_available_quests(user.level)
        
        # Get user's active/completed quests
        conn = await DatabaseManager.get_connection()
        try:
            async with conn.execute("""
                SELECT quest_id, status FROM user_quests WHERE user_id = ?
            """, (interaction.user.id,)) as cursor:
                user_quests = {row['quest_id']: row['status'] for row in await cursor.fetchall()}
        finally:
            await conn.close()
        
        embed = Embed(
            title="📋 Quest Board",
            description="Available quests for your level",
            color=Color.gold()
        )
        
        for quest in available:
            status = user_quests.get(quest['quest_id'])
            
            if status == 'completed':
                status_emoji = "✅"
            elif status == 'active':
                status_emoji = "🔄"
            else:
                status_emoji = "📜"
            
            quest_text = (
                f"{status_emoji} **{quest['name']}** (Level {quest['requirement_level']}+)\n"
                f"{quest['description']}\n"
                f"💰 Reward: {quest['reward_coins']} coins | ✨ {quest['reward_xp']} XP"
            )
            
            embed.add_field(name=f"Quest #{quest['quest_id']}", value=quest_text, inline=False)
        
        embed.set_footer(text="Use /acceptquest <id> to accept a quest")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="acceptquest", description="Accept a quest")
    async def acceptquest(self, interaction: discord.Interaction, quest_id: int):
        await UserService.ensure_user_exists(interaction.user.id, interaction.user.name)
        user = await UserService.get_user(interaction.user.id)
        
        # Check quest requirements
        conn = await DatabaseManager.get_connection()
        try:
            async with conn.execute("""
                SELECT requirement_level FROM quests WHERE quest_id = ?
            """, (quest_id,)) as cursor:
                quest = await cursor.fetchone()
        finally:
            await conn.close()
        
        if not quest:
            await interaction.response.send_message("❌ Quest not found!", ephemeral=True)
            return
        
        if user.level < quest['requirement_level']:
            await interaction.response.send_message(
                f"❌ You need level {quest['requirement_level']} to accept this quest!",
                ephemeral=True
            )
            return
        
        # Accept quest
        result = await QuestService.accept_quest(interaction.user.id, quest_id)
        
        if not result['success']:
            await interaction.response.send_message(f"❌ {result['error']}", ephemeral=True)
            return
        
        quest_info = result['quest']
        embed = Embed(
            title="✅ Quest Accepted!",
            description=f"**{quest_info['name']}**\n{quest_info['description']}",
            color=Color.green()
        )
        embed.add_field(name="Rewards", value=f"💰 {quest_info['reward_coins']} coins\n✨ {quest_info['reward_xp']} XP")
        
        await interaction.response.send_message(embed=embed)