import discord
import os
import random
import asyncio
import math
import aiohttp
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('DISCORD_BOT_TOKEN')
if not token:
    print("Error: DISCORD_BOT_TOKEN belum ada.")

GIPHY_API_KEY = os.getenv('GIPHY_API_KEY')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

bot.remove_command('help')  # Override default help command

wheel_options = ['🎉 Terraria', '🎉 Dota', '🎉 HOK', '🎉 Minecraft']

game_images = {
    '🎉 Terraria': 'images/terraria.jpeg',
    '🎉 Dota': 'images/dota.png',
    '🎉 HOK': 'images/hok.webp',
    '🎉 Minecraft': 'images/minecraft.jpeg'
}

allowed_names = {name: obj for name, obj in math.__dict__.items() if not name.startswith("__")}

@bot.event
async def on_ready():
    print(f'Masuk sebagai {bot.user}!')

@bot.command()
async def spin(ctx):
    spin_msg = await ctx.send(file=discord.File("gachabox.gif"))

    for _ in range(10):
        await spin_msg.edit(content="🎡 Main apa hari ini?...")
        await asyncio.sleep(0.3)

    final_result = random.choice(wheel_options)
    game_image_path = game_images[final_result]

    embed = discord.Embed(
        title="🎡 Hasil akhir!",
        description=f"Selamat hari ini kita main {final_result}",
        color=discord.Color.green()
    )

    embed.set_image(url=f"attachment://{os.path.basename(game_image_path)}")

    await spin_msg.delete()

    await ctx.send(file=discord.File(game_image_path), embed=embed)

@bot.command()
async def calc(ctx, *, expression: str):
    try:
        result = eval(expression, {"__builtins__": None}, allowed_names)
        await ctx.send(f"📊 Hasil dari `{expression}` adalah: **{result}**")
    except Exception as e:
        await ctx.send(f"❌ Terjadi kesalahan saat menghitung: {str(e)}")

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="Help",
        description="List command:",
        color=discord.Color.blue()
    )
    embed.add_field(name="!spin", value="Spin wheel untuk game yang akan dimainkan hari ini.", inline=False)
    embed.add_field(name="!calc", value="Kalkulator. Contoh penggunaan: `!calc 2 + 2 * (3 + 4)`", inline=False)
    embed.add_field(name="!random_gif", value="Mengirim GIF random dari Giphy.", inline=False)
    embed.add_field(name="!help", value="Menampilkan pesan ini.", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="random")  # Ubah nama karena conflict sama variabel random
async def random_gif(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.giphy.com/v1/gifs/random?api_key={GIPHY_API_KEY}&tag=&rating=g') as response:
            data = await response.json()
            gif_url = data['data']['images']['original']['url']
            await ctx.send(gif_url)

bot.run(token)
