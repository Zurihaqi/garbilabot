# import discord
# import importlib
import asyncio
from discord.ext import commands
from utils.constants import INTENTS, TOKEN

COGS = [
    "cogs.fun",
    "cogs.math",
    "cogs.server",
    "cogs.undercover",
    "cogs.help"
]

bot = commands.Bot(command_prefix="!", intents=INTENTS)
bot.remove_command("help")

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

async def main():
    async with bot:
        for cog in COGS:
            try:
                await bot.load_extension(cog)
                print(f"🔧 Loaded {cog}")
            except Exception as e:
                print(f"❌ Failed to load {cog}: {e}")
        if not TOKEN:
            raise SystemExit("Environment variable DISCORD_BOT_TOKEN missing.")
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
