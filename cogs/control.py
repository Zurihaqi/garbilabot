import asyncio
import logging
import os
import sys
import discord
from discord import app_commands
from discord.ext import commands

log = logging.getLogger("bot")

from utils.permissions import has_role_slash

class Control(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="reload", description="Reload bot")
    @has_role_slash()
    async def reload(self, interaction: discord.Interaction):
        await interaction.response.send_message("♻️ Reloading bot...")
        await self.bot.close()
        os.execv(sys.executable, [sys.executable] + sys.argv)

    @app_commands.command(name="shutdown", description="Shutdown bot")
    @has_role_slash()
    async def shutdown(self, interaction: discord.Interaction):
        await interaction.response.send_message("🔌 Bot shutting down...")
        await asyncio.sleep(1)
        await self.bot.close()
        if not self.is_owner_interaction(interaction):
            await interaction.response.send_message(
                "⛔ You don't have permission to use this command.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "🔌 Bot will shutdown soon..."
        )

        await asyncio.sleep(1)
        await self.bot.close()

async def setup(bot: commands.Bot):
    await bot.add_cog(Control(bot))
