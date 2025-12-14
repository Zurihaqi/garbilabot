import discord
from discord import Embed, Color
from discord.ui import View, Button
from utils.game_logic import GameLogic

class ProfileView(View):
    """Interactive profile view with navigation buttons"""
    
    def __init__(self, user_data, discord_user: discord.User, inventory_count: int, equipped: list):
        super().__init__(timeout=120)
        self.user_data = user_data
        self.discord_user = discord_user
        self.inventory_count = inventory_count
        self.equipped = equipped
        self.current_page = "stats"
    
    @discord.ui.button(label="📊 Stats", style=discord.ButtonStyle.primary, custom_id="stats")
    async def stats_button(self, interaction: discord.Interaction, button: Button):
        self.current_page = "stats"
        embed = self.create_stats_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="⚔️ Combat", style=discord.ButtonStyle.danger, custom_id="combat")
    async def combat_button(self, interaction: discord.Interaction, button: Button):
        self.current_page = "combat"
        embed = self.create_combat_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🎒 Inventory", style=discord.ButtonStyle.success, custom_id="inventory")
    async def inventory_button(self, interaction: discord.Interaction, button: Button):
        self.current_page = "inventory"
        embed = self.create_inventory_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🏆 Achievements", style=discord.ButtonStyle.secondary, custom_id="achievements")
    async def achievements_button(self, interaction: discord.Interaction, button: Button):
        self.current_page = "achievements"
        embed = self.create_achievements_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    def create_stats_embed(self) -> Embed:
        """Create stats page embed"""
        next_xp = GameLogic.calculate_level_xp(self.user_data.level)
        xp_bar = self.create_progress_bar(self.user_data.xp, next_xp)
        hp_bar = self.create_progress_bar(self.user_data.hp, self.user_data.max_hp)
        
        embed = Embed(
            title=f"⚔️ {self.user_data.username}'s Profile",
            description=f"**{self.user_data.cls}** • Level {self.user_data.level}",
            color=self.get_class_color()
        )
        
        # Main stats
        stats_text = (
            f"💰 **Coins:** {self.user_data.balance:,}\n"
            f"✨ **Level:** {self.user_data.level}\n"
            f"📊 **XP:** {xp_bar} `{self.user_data.xp}/{next_xp}`\n\n"
            f"❤️ **HP:** {hp_bar} `{self.user_data.hp}/{self.user_data.max_hp}`\n"
            f"⚔️ **Attack:** {self.user_data.attack}\n"
            f"🛡️ **Defense:** {self.user_data.defense}"
        )
        
        embed.add_field(name="📊 Character Stats", value=stats_text, inline=False)
        
        if self.discord_user.avatar:
            embed.set_thumbnail(url=self.discord_user.avatar.url)
        
        embed.set_footer(text="Use the buttons below to navigate • Profile expires in 2 minutes")
        embed.set_image(url="attachment://profile.png")
        
        return embed
    
    def create_combat_embed(self) -> Embed:
        """Create combat page embed"""
        embed = Embed(
            title=f"⚔️ {self.user_data.username}'s Combat Stats",
            description=f"**{self.user_data.cls}** • Level {self.user_data.level}",
            color=Color.red()
        )
        
        # PvP Stats
        total_battles = self.user_data.pvp_wins + self.user_data.pvp_losses
        win_rate = self.user_data.win_rate
        
        pvp_text = (
            f"🏆 **Wins:** {self.user_data.pvp_wins}\n"
            f"💀 **Losses:** {self.user_data.pvp_losses}\n"
            f"📊 **Total Battles:** {total_battles}\n"
            f"📈 **Win Rate:** {win_rate:.1f}%"
        )
        embed.add_field(name="⚔️ PvP Record", value=pvp_text, inline=True)
        
        # PvE Stats
        pve_text = (
            f"🗺️ **Adventures:** {self.user_data.adventure_count}\n"
            f"🐉 **Bosses Defeated:** {self.user_data.boss_kills}\n"
            f"⚔️ **Combat Power:** {self.user_data.attack + self.user_data.level * 5}"
        )
        embed.add_field(name="🗡️ PvE Record", value=pve_text, inline=True)
        
        # Combat ranking
        if win_rate >= 70:
            rank = "🌟 Elite Warrior"
        elif win_rate >= 50:
            rank = "⚔️ Skilled Fighter"
        elif win_rate >= 30:
            rank = "🗡️ Apprentice"
        else:
            rank = "🔰 Novice"
        
        embed.add_field(name="🏅 Combat Rank", value=rank, inline=False)
        
        if self.discord_user.avatar:
            embed.set_thumbnail(url=self.discord_user.avatar.url)
        
        embed.set_footer(text="Keep battling to improve your stats!")
        
        return embed
    
    def create_inventory_embed(self) -> Embed:
        """Create inventory page embed"""
        embed = Embed(
            title=f"🎒 {self.user_data.username}'s Inventory",
            description=f"**Total Items:** {self.inventory_count}",
            color=Color.purple()
        )
        
        # Equipped items
        if self.equipped:
            equipped_text = "\n".join([f"✅ {item}" for item in self.equipped])
        else:
            equipped_text = "No items equipped"
        
        embed.add_field(name="⚔️ Equipped", value=equipped_text, inline=False)
        
        # Quick stats
        embed.add_field(
            name="💼 Storage",
            value=f"📦 **Items:** {self.inventory_count}\n💰 **Worth:** ??? coins",
            inline=True
        )
        
        embed.add_field(
            name="🔧 Quick Actions",
            value="Use `/inventory` for full list\nUse `/equip <item>` to equip\nUse `/use <item>` for consumables",
            inline=True
        )
        
        if self.discord_user.avatar:
            embed.set_thumbnail(url=self.discord_user.avatar.url)
        
        embed.set_footer(text="Visit /shop to get more items!")
        
        return embed
    
    def create_achievements_embed(self) -> Embed:
        """Create achievements page embed"""
        embed = Embed(
            title=f"🏆 {self.user_data.username}'s Achievements",
            description="Your journey milestones",
            color=Color.gold()
        )
        
        # Calculate achievements
        achievements = []
        
        # Level milestones
        if self.user_data.level >= 50:
            achievements.append("👑 **Legendary Hero** - Reached level 50")
        elif self.user_data.level >= 30:
            achievements.append("🌟 **Master Adventurer** - Reached level 30")
        elif self.user_data.level >= 10:
            achievements.append("⚔️ **Seasoned Warrior** - Reached level 10")
        
        # Combat achievements
        if self.user_data.pvp_wins >= 50:
            achievements.append("🏆 **PvP Champion** - Won 50 battles")
        elif self.user_data.pvp_wins >= 10:
            achievements.append("⚔️ **Duelist** - Won 10 battles")
        
        if self.user_data.boss_kills >= 20:
            achievements.append("🐉 **Dragon Slayer** - Defeated 20 bosses")
        elif self.user_data.boss_kills >= 5:
            achievements.append("🗡️ **Boss Hunter** - Defeated 5 bosses")
        
        # Economy achievements
        if self.user_data.balance >= 10000:
            achievements.append("💎 **Wealthy Merchant** - 10,000+ coins")
        elif self.user_data.balance >= 1000:
            achievements.append("💰 **Coin Collector** - 1,000+ coins")
        
        # Adventure achievements
        if self.user_data.adventure_count >= 100:
            achievements.append("🗺️ **Master Explorer** - 100+ adventures")
        elif self.user_data.adventure_count >= 25:
            achievements.append("🧭 **Adventurer** - 25+ adventures")
        
        if achievements:
            embed.add_field(
                name="✨ Unlocked Achievements",
                value="\n".join(achievements),
                inline=False
            )
        else:
            embed.add_field(
                name="✨ Unlocked Achievements",
                value="No achievements yet. Start your journey!",
                inline=False
            )
        
        # Progress to next achievement
        next_goals = []
        if self.user_data.level < 10:
            next_goals.append(f"⚔️ Reach level 10 ({self.user_data.level}/10)")
        if self.user_data.pvp_wins < 10:
            next_goals.append(f"⚔️ Win 10 PvP battles ({self.user_data.pvp_wins}/10)")
        if self.user_data.boss_kills < 5:
            next_goals.append(f"🐉 Defeat 5 bosses ({self.user_data.boss_kills}/5)")
        
        if next_goals:
            embed.add_field(
                name="🎯 Next Goals",
                value="\n".join(next_goals[:3]),
                inline=False
            )
        
        if self.discord_user.avatar:
            embed.set_thumbnail(url=self.discord_user.avatar.url)
        
        embed.set_footer(text="Keep playing to unlock more achievements!")
        
        return embed
    
    def create_progress_bar(self, current: int, maximum: int, length: int = 10) -> str:
        """Create a visual progress bar"""
        if maximum == 0:
            percentage = 0
        else:
            percentage = current / maximum
        
        filled = int(length * percentage)
        empty = length - filled
        
        return f"{'█' * filled}{'░' * empty}"
    
    def get_class_color(self) -> Color:
        """Get color based on class"""
        class_colors = {
            'Novice': Color.from_rgb(139, 69, 19),
            'Adventurer': Color.from_rgb(34, 139, 34),
            'Warrior': Color.from_rgb(65, 105, 225),
            'Knight': Color.from_rgb(138, 43, 226),
            'Champion': Color.from_rgb(255, 215, 0),
            'Master': Color.from_rgb(255, 140, 0),
            'Dragon Slayer': Color.from_rgb(220, 20, 60),
            'Legendary Hero': Color.from_rgb(255, 0, 255)
        }
        return class_colors.get(self.user_data.cls, Color.gold())