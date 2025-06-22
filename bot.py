import asyncio
import logging
from discord.ext import commands

from utils.constants import INTENTS, TOKEN, LOG_FORMAT, DATE_FORMAT

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt=DATE_FORMAT,
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ],
)

logger = logging.getLogger("bot")

COGS = [
    "cogs.fun",
    "cogs.math",
    "cogs.server",
    "cogs.undercover",
    "cogs.help",
    "cogs.control"
]

bot = commands.Bot(command_prefix="!", intents=INTENTS)
bot.remove_command("help")

@bot.event
async def on_ready():
    logger.info("✅ Logged in as %s (%s)", bot.user, bot.user.id)

@bot.event
async def on_command(ctx: commands.Context):
    logger.info(
        "📥 Command '%s' invoked by %s (%s) in %s/%s",
        ctx.command,
        ctx.author,
        ctx.author.id,
        ctx.guild or "DM",
        ctx.channel,
    )

@bot.event
async def on_command_completion(ctx: commands.Context):
    logger.info("📤 Command '%s' finished for %s", ctx.command, ctx.author)

@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    if hasattr(ctx.command, "on_error"):
        return
    logger.error("❌ Error in command '%s': %s", ctx.command, error, exc_info=True)

async def main():
    async with bot:
        for cog in COGS:
            try:
                await bot.load_extension(cog)
                logger.info(f"🔧 Loaded {cog}")
            except Exception as exc:
                logger.exception(f"❌ Failed to load {cog}: {exc}")

        if not TOKEN:
            logger.critical("Environment variable DISCORD_BOT_TOKEN missing.")
            raise SystemExit("Environment variable DISCORD_BOT_TOKEN missing.")

        await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("Shutdown requested by user (Ctrl-C).")
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.critical(f"❌ Fatal error: {e}")
        input("Press Enter to exit...")

    logger.info("🛑 Shutting down...")