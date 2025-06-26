import subprocess
import asyncio
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
    async def restart(self, ctx):
        """Restart server."""
        global server_process

        if not is_owner():
            await ctx.send("⛔ Kamu tidak punya izin untuk menjalankan perintah ini.")
            return
        
        if not server_process or server_process.poll() is not None:
            await ctx.send("⚠️ Server tidak sedang berjalan.")
            return

        try:
            if server_process and server_process.poll() is None:
                server_process.stdin.write("stop\n")
                server_process.stdin.flush()
                await ctx.send("🔄 Menghentikan server...")
                await asyncio.get_event_loop().run_in_executor(None, lambda: server_process.wait(timeout=30))
                await ctx.send("✅ Server sudah berhenti. Memulai ulang...")

            server_process = subprocess.Popen(
                ["java", "-Xmx2G", "-Xms2G", "-jar", "paper-1.21.4.jar", "--nogui"],
                cwd=MC_SERVER_PATH,
                stdin=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )

            await ctx.send("🟢 Server Minecraft berhasil direstart!")
        except subprocess.TimeoutExpired:
            if server_process:
                server_process.kill()
            await ctx.send("⚠️ Server tidak respons saat dimatikan, dipaksa mati (kill). Memulai ulang...")
            try:
                server_process = subprocess.Popen(
                    ["java", "-Xmx2G", "-Xms2G", "-jar", "paper-1.21.4.jar", "--nogui"],
                    cwd=MC_SERVER_PATH,
                    stdin=subprocess.PIPE,
                    text=True,
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
                await ctx.send("🟢 Server Minecraft berhasil direstart!")
            except Exception as e:
                server_process = None
                await ctx.send(f"❌ Gagal menjalankan server: {e}")
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
    async def run(self, ctx, *, command: str):
        """Run a command on the server."""
        global server_process

        if not is_owner():
            await ctx.send("⛔ Kamu tidak punya izin untuk menjalankan perintah ini.")
            return

        if not server_process or server_process.poll() is not None:
            await ctx.send("⚠️ Server tidak sedang berjalan.")
            return

        try:
            server_process.stdin.write(f"{command}\n")
            server_process.stdin.flush()
            await ctx.send(f"▶️ Perintah `{command}` telah dikirim ke server.")
        except Exception as e:
            await ctx.send(f"❌ Gagal mengirim perintah: {e}")

async def setup(bot):
    await bot.add_cog(Server(bot))
