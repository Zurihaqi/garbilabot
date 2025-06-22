import random, aiohttp, discord, asyncio
from discord.ext import commands
from utils.constants import GIPHY_API_KEY

LUCK_STATUSES = [
    ("🍀", "Main Character Energy - Lock in"),
    ("⭐", "Plot Armor Activated - RNGesus loves you"),
    ("🌟", "Mid Tier Luck - Bros on 50:50"),
    ("😐", "NPC Mode - Nothing special, just existing"),
    ("😞", "Cursed Build - L + Ratio + Skill Issue"),
    ("💀", "Delete This Day - Touch grass, it's over")
]

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="luck")
    async def todays_luck(self, ctx: commands.Context):
        """Seberapa beruntung hari ini?"""

        slots = ["❓", "❓", "❓"] 
        spin_msg = await ctx.send(f"| {' | '.join(slots)} |")

        spin_count = 15
        delay = 0.1

        final_results = [random.choice(LUCK_STATUSES) for _ in range(3)]

        for i in range(spin_count):
            for slot_index in range(3):
                stop_time = spin_count - (3 - slot_index) * 3
                
                if i < stop_time:
                    slots[slot_index] = random.choice(LUCK_STATUSES)[0]
                else:
                    slots[slot_index] = final_results[slot_index][0]

            try:
                await spin_msg.edit(content=f"| {' | '.join(slots)} |")
            except discord.NotFound:
                return
            except discord.HTTPException:
                pass

            await asyncio.sleep(delay)
            
            delay = min(delay + 0.03, 0.5)

        final_emoji, final_text = final_results[1]
        
        embed = discord.Embed(
            title="🎉 Keberuntungan Hari Ini!",
            description=f"Hasil keberuntunganmu: **{final_emoji} {final_text}**",
            color=discord.Color.gold(),
        )

        try:
            await spin_msg.delete()
        except discord.NotFound:
            pass
        
        await ctx.send(embed=embed)

    @commands.command(name="random")
    async def random_gif(self, ctx: commands.Context):
        """Ambil gif random dari giphy."""
        url = f"https://api.giphy.com/v1/gifs/random?api_key={GIPHY_API_KEY}&rating=R"
        async with aiohttp.ClientSession() as session, session.get(url) as resp:
            data = await resp.json()
            await ctx.send(data["data"]["images"]["original"]["url"])

async def setup(bot):
    await bot.add_cog(Fun(bot))
