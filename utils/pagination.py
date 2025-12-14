import discord
from discord import Embed, Color, Interaction
from discord.ui import View, Button

class ShopPaginator(View):
    def __init__(self, pages):
        super().__init__(timeout=120)
        self.pages = pages
        self.index = 0
        self.message = None

        # Disable buttons if only 1 page
        self.prev.disabled = len(pages) <= 1
        self.next.disabled = len(pages) <= 1

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.secondary)
    async def prev(self, interaction: Interaction, button: Button):
        self.index = (self.index - 1) % len(self.pages)
        await interaction.response.edit_message(embed=self.pages[self.index])

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: Interaction, button: Button):
        self.index = (self.index + 1) % len(self.pages)
        await interaction.response.edit_message(embed=self.pages[self.index])


async def paginate_shop(interaction: Interaction, items):
    """Send paginated shop embed"""
    # Group items into embeds
    weapons, armor, consumables = [], [], []
    for item_data in items:
        bonus = f"+{item_data['bonus_value']} {item_data['stat_bonus']}" if item_data['item_type'] != 'consumable' else ""
        txt = f"**{item_data['item']}** - {item_data['price']:,} coins (Lv{item_data['level_req']})\n*{item_data['description']}* {bonus}\n"
        if item_data['item_type'] == 'weapon':
            weapons.append(txt)
        elif item_data['item_type'] == 'armor':
            armor.append(txt)
        else:
            consumables.append(txt)

    # Break long lists into pages (~5-10 items per page for readability)
    def chunk(lst, n=5):
        for i in range(0, len(lst), n):
            yield lst[i:i+n]

    pages = []
    for w_chunk in chunk(weapons):
        embed = Embed(title="🛒 Shop - Weapons", description="".join(w_chunk), color=Color.blue())
        pages.append(embed)
    for a_chunk in chunk(armor):
        embed = Embed(title="🛒 Shop - Armor", description="".join(a_chunk), color=Color.blue())
        pages.append(embed)
    for c_chunk in chunk(consumables):
        embed = Embed(title="🛒 Shop - Consumables", description="".join(c_chunk), color=Color.blue())
        pages.append(embed)

    paginator = ShopPaginator(pages)
    await interaction.response.send_message(embed=pages[0], view=paginator)
