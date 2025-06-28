import asyncio
import logging
import os
import sys
from discord.ext import commands

from utils.permissions import is_owner

log = logging.getLogger("bot")

class Control(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.server_process = None

    @commands.command(name="reload", help="Reload bot.")
    async def reload(self, ctx):
        if not is_owner():
            await ctx.send("⛔ Kamu tidak punya izin untuk menjalankan perintah ini.")
            return

        await ctx.send("♻️ Reloading bot...")

        if self.server_process and self.server_process.poll() is None:
            try:
                self.server_process.stdin.write("stop\n")
                self.server_process.stdin.flush()
                await asyncio.get_event_loop().run_in_executor(
                    None, lambda: self.server_process.wait(timeout=15)
                )
            except Exception:
                self.server_process.kill()
            finally:
                self.server_process = None

        log.warning("Reload requested by owner (%s). Re-exec self.", ctx.author)
        await self.bot.close()
        os.execv(sys.executable, [sys.executable] + sys.argv)

    @commands.command(name="kys", help="Matikan bot.")
    async def kys(self, ctx):
        if not is_owner():
            await ctx.send("⛔ Kamu tidak punya izin untuk menjalankan perintah ini.")
            return

        await ctx.send("🔌 Bot akan dimatikan... Sampai jumpa!")

        async def shutdown():
            await asyncio.sleep(1)
            await self.bot.close()

        asyncio.create_task(shutdown())


async def setup(bot):
    await bot.add_cog(Control(bot))