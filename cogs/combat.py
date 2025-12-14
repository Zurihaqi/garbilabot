import random
from datetime import datetime

import discord
from discord import app_commands, Embed, Color
from discord.ext import commands

from utils.cooldown_manager import CooldownManager
from utils.game_logic import GameLogic
from database.db_manager import DatabaseManager
from services.user_service import UserService
from models.user import User
from utils.game_logic import GameLogic

class CombatCommands(commands.Cog):
    """Combat and adventure commands"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cooldown_manager = CooldownManager()
    
    @app_commands.command(name="adventure", description="Go on adventure")
    async def adventure(self, interaction: discord.Interaction):
        cd = self.cooldown_manager.check_cooldown(interaction.user.id, "adventure", 300)
        if cd:
            await interaction.response.send_message(f"⏳ Cooldown: {cd}s", ephemeral=True)
            return
        
        UserService.ensure_user_exists(interaction.user.id, interaction.user.name)
        user = UserService.get_user(interaction.user.id)
        
        if not user.is_alive():
            await interaction.response.send_message("💀 Too injured!", ephemeral=True)
            return
        
        # Boss encounter (10% at lv10+)
        if user.level >= 10 and random.random() < 0.1:
            result = self._boss_encounter(user, interaction.user.id)
            await interaction.response.send_message(embed=result)
            return
        
        # Regular adventure
        result = self._regular_adventure(user, interaction.user.id)
        await interaction.response.send_message(embed=result)
    
    def _boss_encounter(self, user: User, user_id: int) -> Embed:
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
            
            with DatabaseManager.get_connection() as conn:
                c = conn.cursor()
                c.execute("""
                    UPDATE users
                    SET balance = balance + ?, xp = xp + ?, hp = ?,
                        adventure_count = adventure_count + 1, boss_kills = boss_kills + 1
                    WHERE user_id = ?
                """, (reward_coins, reward_xp, new_hp, user_id))
            
            embed = Embed(title="🐉 BOSS DEFEATED!", description="Mighty boss slain!", color=Color.red())
            embed.add_field(name="Rewards", value=f"💰 {reward_coins} coins\n✨ {reward_xp} XP")
            embed.add_field(name="Damage", value=f"💔 -{dmg} HP")
            return embed
        else:
            # Defeat
            new_hp = max(0, user.hp - dmg * 2)
            UserService.update_user_stats(user_id, hp=new_hp, adventure_count=user.adventure_count + 1)
            
            embed = Embed(title="💀 Boss Victory", description=f"You were defeated! Lost {dmg*2} HP.", color=Color.dark_red())
            return embed
    
    def _regular_adventure(self, user: User, user_id: int) -> Embed:
        """Handle regular adventure"""
        outcomes = [
            {"desc": "🗡️ Defeated a goblin", "c": (15, 30), "x": (10, 20), "h": (-5, 0)},
            {"desc": "💎 Found treasure", "c": (40, 80), "x": (5, 15), "h": (0, 0)},
            {"desc": "🕳️ Fell in trap", "c": (-20, 0), "x": (2, 5), "h": (-20, -10)},
            {"desc": "🧙 Helped wizard", "c": (25, 50), "x": (15, 30), "h": (0, 10)},
            {"desc": "⚔️ Fought bandit", "c": (20, 40), "x": (12, 25), "h": (-10, 0)},
        ]
        
        outcome = random.choice(outcomes)
        coins = random.randint(*outcome['c'])
        xp = random.randint(*outcome['x'])
        hp_change = random.randint(*outcome['h'])
        
        new_hp = max(0, min(user.hp + hp_change, user.max_hp))
        
        # Update with XP/level handling
        result = UserService.add_xp_and_coins(user_id, xp, coins)
        UserService.update_user_stats(
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
    
    @app_commands.command(name="pvp", description="Challenge player")
    async def pvp(self, interaction: discord.Interaction, target: discord.User):
        if target.bot:
            await interaction.response.send_message("❌ Can't fight bots!", ephemeral=True)
            return
        
        if target.id == interaction.user.id:
            await interaction.response.send_message("❌ Can't fight yourself!", ephemeral=True)
            return
        
        cd = self.cooldown_manager.check_cooldown(interaction.user.id, "pvp", 600)
        if cd:
            await interaction.response.send_message(f"⏳ PvP cooldown: {cd}s", ephemeral=True)
            return
        
        UserService.ensure_user_exists(interaction.user.id, interaction.user.name)
        UserService.ensure_user_exists(target.id, target.name)
        
        attacker = UserService.get_user(interaction.user.id)
        defender = UserService.get_user(target.id)
        
        if not attacker.is_alive():
            await interaction.response.send_message("💀 You're too injured!", ephemeral=True)
            return
        
        if not defender.is_alive():
            await interaction.response.send_message("💀 Target is too injured!", ephemeral=True)
            return
        
        # Calculate battle
        a_power = GameLogic.calculate_battle_power(attacker.attack, attacker.level)
        d_power = GameLogic.calculate_battle_power(defender.attack, defender.level)
        
        winner_id = interaction.user.id if a_power >= d_power else target.id
        loser_id = target.id if winner_id == interaction.user.id else interaction.user.id
        
        dmg = abs(a_power - d_power) // 10
        loser_hp = max(0, (attacker.hp if loser_id == interaction.user.id else defender.hp) - dmg)
        
        # Update database
        with DatabaseManager.get_connection() as conn:
            c = conn.cursor()
            c.execute("UPDATE users SET hp = ? WHERE user_id = ?", (loser_hp, loser_id))
            c.execute("UPDATE users SET pvp_wins = pvp_wins + 1 WHERE user_id = ?", (winner_id,))
            c.execute("UPDATE users SET pvp_losses = pvp_losses + 1 WHERE user_id = ?", (loser_id,))
            c.execute("""
                INSERT INTO pvp (attacker_id, defender_id, winner_id, timestamp, attacker_power, defender_power)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (interaction.user.id, target.id, winner_id, datetime.now().isoformat(), a_power, d_power))
        
        winner = interaction.user if winner_id == interaction.user.id else target
        
        embed = Embed(title="⚔️ PvP Battle!", color=Color.red())
        embed.add_field(name="Combatants", value=f"{interaction.user.mention} vs {target.mention}", inline=False)
        embed.add_field(name="Powers", value=f"{interaction.user.name}: {a_power}\n{target.name}: {d_power}")
        embed.add_field(name="Result", value=f"🏆 Winner: {winner.mention}\n💔 Damage: {dmg} HP")
        
        await interaction.response.send_message(embed=embed)