import asyncio
import logging
from aiohttp import web
import discord
from discord.ext import commands
from discord import app_commands

from utils.constants import INTENTS, TOKEN, LOG_FORMAT, DATE_FORMAT

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt=DATE_FORMAT,
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("bot")

COGS = [
    "cogs.fun",
    "cogs.math",
    "cogs.undercover",
    "cogs.help",
    "cogs.control",
    "cogs.reaction_roles",
]

bot = commands.Bot(
    command_prefix=commands.when_mentioned,
    intents=INTENTS,
)

@bot.event
async def on_ready():
    await bot.tree.sync()
    logger.info("✅ Logged in as %s (%s)", bot.user, bot.user.id)
    logger.info("🔁 Slash commands synced")

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type is discord.InteractionType.application_command:
        logger.info(
            "➡️ Slash command attempt '/%s' by %s (%s)",
            interaction.data.get("name", "unknown"),
            interaction.user,
            interaction.user.id,
        )

@bot.event
async def on_app_command_completion(interaction: discord.Interaction, command: app_commands.Command):
    logger.info(
        "📥 Slash command '/%s' executed by %s (%s) in %s",
        command.qualified_name,
        interaction.user,
        interaction.user.id,
        interaction.guild.name if interaction.guild else "DM",
    )

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    logger.error(
        "❌ Slash command error: /%s by %s (%s)",
        interaction.command.name if interaction.command else "unknown",
        interaction.user,
        interaction.user.id,
        exc_info=True,
    )

    message = "❌ An error occurred while executing this command."
    if interaction.response.is_done():
        await interaction.followup.send(message, ephemeral=True)
    else:
        await interaction.response.send_message(message, ephemeral=True)

def healthcheck(request):
    return web.Response(text="OK")

async def start_healthcheck_server():
    app = web.Application()
    app.add_routes([web.get("/kaithhealthcheck", healthcheck)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    logger.info("🌐 Health check running on http://0.0.0.0:8080/kaithheathcheck")

async def main():
    task = asyncio.create_task(start_healthcheck_server())

    await task

    # Load cogs
    async with bot:
        for cog in COGS:
            try:
                await bot.load_extension(cog)
                logger.info("🔧 Loaded %s", cog)
            except Exception:
                logger.exception("❌ Failed to load %s", cog)

    while True:
        try:
            await bot.start(TOKEN)
        except KeyboardInterrupt:
            logger.warning("Shutdown requested by user (Ctrl+C).")
            break
        except Exception:
            logger.exception("❌ Bot crashed, restarting in 5 seconds...")
            await asyncio.sleep(5)
