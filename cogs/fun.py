import random
import aiohttp
import discord
import asyncio
from discord import app_commands
from discord.ext import commands

from utils.constants import GIPHY_API_KEY, LUCK_STATUSES


class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="luck",
        description="What is your luck for today?"
    )
    async def todays_luck(self, interaction: discord.Interaction):
        await interaction.response.defer()

        slots = ["❓", "❓", "❓"]
        spin_msg = await interaction.followup.send(
            f"| {' | '.join(slots)} |"
        )

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
                await spin_msg.edit(
                    content=f"| {' | '.join(slots)} |"
                )
            except discord.NotFound:
                return
            except discord.HTTPException:
                pass

            await asyncio.sleep(delay)
            delay = min(delay + 0.03, 0.5)

        final_emoji, final_text = final_results[1]

        embed = discord.Embed(
            title="🎉 Your luck result",
            description=f"\n**{final_emoji} {final_text}**",
            color=discord.Color.gold(),
        )

        try:
            await spin_msg.delete()
        except discord.NotFound:
            pass

        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="random",
        description="Get a random gif"
    )
    async def random_gif(self, interaction: discord.Interaction):
        await interaction.response.defer()

        url = (
            "https://api.giphy.com/v1/gifs/random"
            f"?api_key={GIPHY_API_KEY}&rating=R&tag=brainrot"
        )

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()

        gif_url = data["data"]["images"]["original"]["url"]
        await interaction.followup.send(gif_url)


async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))
