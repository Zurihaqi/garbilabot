import subprocess
import asyncio
import os
import sys
from discord.ext import commands
from utils.constants import MC_SERVER_PATH
from dotenv import load_dotenv
from utils.permissions import is_owner

load_dotenv()
server_process: subprocess.Popen | None = None

class Server(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def start(self, ctx):
        """Start server minecraft."""
        global server_process

        if not is_owner():
            await ctx.send("⛔ Kamu tidak punya izin untuk menjalankan perintah ini.")
            return

        if server_process and server_process.poll() is None:
            await ctx.send("⚠️ Server sudah berjalan.")
            return

        try:
            server_process = subprocess.Popen(
                ["java", "-Xmx2G", "-Xms2G", "-jar", "paper-1.21.4.jar", "--nogui"],
                cwd=MC_SERVER_PATH,
                stdin=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            await ctx.send("🟢 Server Minecraft sedang dijalankan!")
        except Exception as e:
            server_process = None
            await ctx.send(f"❌ Gagal menjalankan server: {e}")

    @commands.command()
    async def stop(self, ctx):
        """Stop server minecraft."""
        global server_process

        if not is_owner():
            await ctx.send("⛔ Kamu tidak punya izin untuk menjalankan perintah ini.")
            return

        if not server_process or server_process.poll() is not None:
            await ctx.send("⚠️ Server tidak sedang berjalan.")
            return

        try:
            server_process.stdin.write("stop\n")
            server_process.stdin.flush()

            await ctx.send("🛑 Perintah `stop` dikirim. Menunggu server mematikan diri...")
            await asyncio.get_event_loop().run_in_executor(None, lambda: server_process.wait(timeout=30))
            await ctx.send("✅ Server sudah berhenti.")
        except subprocess.TimeoutExpired:
            server_process.kill()
            await ctx.send("⚠️ Server tidak respons, dipaksa mati (kill).")
        except Exception as e:
            await ctx.send(f"❌ Gagal menghentikan server: {e}")
        finally:
            server_process = None

    @commands.command()
    async def reload(self, ctx):
        """Reload bot."""
        global server_process

        if not is_owner():
            await ctx.send("⛔ Kamu tidak punya izin untuk menjalankan perintah ini.")
            return

        await ctx.send("♻️ Reloading bot...")

        if server_process and server_process.poll() is None:
            try:
                server_process.stdin.write("stop\n")
                server_process.stdin.flush()
                await asyncio.get_event_loop().run_in_executor(None, lambda: server_process.wait(timeout=15))
            except Exception:
                server_process.kill()
            finally:
                server_process = None

        await self.bot.close()
        os.execv(sys.executable, [sys.executable] + sys.argv)

    @commands.command()
    async def kys(self, ctx):
        """Menutup bot."""
        if not is_owner():
            await ctx.send("⛔ Kamu tidak punya izin untuk menjalankan perintah ini.")
            return

        await ctx.send("🔌 Bot akan dimatikan... Sampai jumpa!")
        await self.bot.close()

async def setup(bot):
    await bot.add_cog(Server(bot))
