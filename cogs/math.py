from discord.ext import commands
from utils.permissions import safe_eval

class Maths(commands.Cog):
    @commands.command()
    async def calc(self, ctx, *, expression: str):
        """Kalkulator."""
        try:
            result = safe_eval(expression)
            await ctx.send(f"📊 `{expression}` = **{result}**")
        except Exception as err:
            await ctx.send(f"❌ Error: {err}")

async def setup(bot):
    await bot.add_cog(Maths())
