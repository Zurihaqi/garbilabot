import discord
from discord import app_commands, Embed, Color
from discord.ext import commands

from services.user_service import UserService
from services.inventory_service import InventoryService
from services.shop_service import ShopService
from utils.pagination import paginate_shop

class ShopCommands(commands.Cog):
    """Shop and inventory commands"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="shop", description="Browse/buy items")
    async def shop(self, interaction: discord.Interaction, item: str = None):
        if item:
            # Purchase item
            result = await ShopService.purchase_item(interaction.user.id, item)
            
            if not result['success']:
                await interaction.response.send_message(f"❌ {result['error']}", ephemeral=True)
                return
            
            item_data = result['item']
            embed = Embed(
                title="✅ Purchase Success!",
                description=f"Bought **{item}** for {item_data['price']:,} coins",
                color=Color.green()
            )
            embed.add_field(name="Info", value=item_data['description'])
            
            if item_data['item_type'] != 'consumable':
                embed.add_field(
                    name="Bonus",
                    value=f"+{item_data['bonus_value']} {item_data['stat_bonus']}"
                )
            
            await interaction.response.send_message(embed=embed)
        else:
            # List shop
            items = await ShopService.get_all_items()
            if not items:
                await interaction.response.send_message("🛒 Shop empty.", ephemeral=True)
                return

            await paginate_shop(interaction, items)
            
    @app_commands.command(name="inventory", description="View inventory")
    async def inventory(self, interaction: discord.Interaction):
        items = InventoryService.get_inventory(interaction.user.id)
        
        if not items:
            await interaction.response.send_message("🎒 Empty inventory!", ephemeral=True)
            return
        
        embed = Embed(title=f"🎒 {interaction.user.name}'s Inventory", color=Color.purple())
        equipped, other = [], []
        
        for item in items:
            eq_mark = "✅ " if item['equipped'] else ""
            qty = f"x{item['quantity']}" if item['quantity'] > 1 else ""
            bonus = f"(+{item['bonus_value']} {item['stat_bonus']})" if item['item_type'] != 'consumable' else ""
            line = f"{eq_mark}**{item['item']}** {qty} {bonus}\n"
            
            (equipped if item['equipped'] else other).append(line)
        
        if equipped:
            embed.add_field(name="✅ Equipped", value="".join(equipped), inline=False)
        if other:
            embed.add_field(name="📦 Items", value="".join(other), inline=False)
        
        embed.set_footer(text="/equip <item> or /use <item>")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="equip", description="Equip item")
    async def equip(self, interaction: discord.Interaction, item: str):
        result = InventoryService.equip_item(interaction.user.id, item)
        
        if not result['success']:
            await interaction.response.send_message(f"❌ {result['error']}", ephemeral=True)
            return
        
        await interaction.response.send_message(
            f"✅ Equipped **{item}**! (+{result['bonus_value']} {result['stat_bonus']})"
        )
    
    @app_commands.command(name="use", description="Use consumable")
    async def use_item(self, interaction: discord.Interaction, item: str):
        # Get item info
        shop_item = await ShopService.get_item(item)
        if not shop_item:
            await interaction.response.send_message("❌ Item not found.", ephemeral=True)
            return
        
        if shop_item['item_type'] != 'consumable':
            await interaction.response.send_message("❌ Use /equip instead.", ephemeral=True)
            return
        
        # Check if user has it
        inventory = InventoryService.get_inventory(interaction.user.id)
        has_item = any(i['item'] == item for i in inventory)
        
        if not has_item:
            await interaction.response.send_message("❌ Don't own this.", ephemeral=True)
            return
        
        # Get user HP
        user = UserService.get_user(interaction.user.id)
        
        if user.is_full_hp():
            await interaction.response.send_message("❌ Already full HP!", ephemeral=True)
            return
        
        # Use item
        heal = min(shop_item['bonus_value'], user.max_hp - user.hp)
        new_hp = user.hp + heal
        
        UserService.update_user_stats(interaction.user.id, hp=new_hp)
        InventoryService.remove_item(interaction.user.id, item, 1)
        
        embed = Embed(
            title="✨ Item Used!",
            description=f"Used **{item}** and restored **{heal} HP**!",
            color=Color.green()
        )
        embed.add_field(name="HP", value=f"{new_hp}/{user.max_hp}")
        await interaction.response.send_message(embed=embed)