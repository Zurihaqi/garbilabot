import discord
from discord import app_commands
from discord.ext import commands
from utils.permissions import safe_eval

class CalculatorView(discord.ui.View):
    CALCULATOR_TITLE = "🧮 Calculator"

    def __init__(self, author: discord.User):
        super().__init__(timeout=180)
        self.author = author
        self.expression = ""

    def display(self) -> str:
        return self.expression or "0"

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message(
                "❌ This calculator is not yours.",
                ephemeral=True,
            )
            return False
        return True

    async def update(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=self.CALCULATOR_TITLE,
            description=f"```{self.display()}```",
            color=discord.Color.blurple(),
        )
        await interaction.response.edit_message(embed=embed, view=self)

    def append(self, value: str):
        self.expression += value

    # ───────── row 0 ─────────
    @discord.ui.button(label="7", row=0, style=discord.ButtonStyle.secondary)
    async def seven(self, i, _): self.append("7"); await self.update(i)

    @discord.ui.button(label="8", row=0, style=discord.ButtonStyle.secondary)
    async def eight(self, i, _): self.append("8"); await self.update(i)

    @discord.ui.button(label="9", row=0, style=discord.ButtonStyle.secondary)
    async def nine(self, i, _): self.append("9"); await self.update(i)

    @discord.ui.button(label="÷", row=0, style=discord.ButtonStyle.primary)
    async def divide(self, i, _): self.append("/"); await self.update(i)

    @discord.ui.button(label="C", row=0, style=discord.ButtonStyle.danger)
    async def clear(self, i, _):
        self.expression = ""
        await self.update(i)

    # ───────── row 1 ─────────
    @discord.ui.button(label="4", row=1, style=discord.ButtonStyle.secondary)
    async def four(self, i, _): self.append("4"); await self.update(i)

    @discord.ui.button(label="5", row=1, style=discord.ButtonStyle.secondary)
    async def five(self, i, _): self.append("5"); await self.update(i)

    @discord.ui.button(label="6", row=1, style=discord.ButtonStyle.secondary)
    async def six(self, i, _): self.append("6"); await self.update(i)

    @discord.ui.button(label="×", row=1, style=discord.ButtonStyle.primary)
    async def multiply(self, i, _): self.append("*"); await self.update(i)

    @discord.ui.button(label="⌫", row=1, style=discord.ButtonStyle.danger)
    async def backspace(self, i, _):
        self.expression = self.expression[:-1]
        await self.update(i)

    # ───────── row 2 ─────────
    @discord.ui.button(label="1", row=2, style=discord.ButtonStyle.secondary)
    async def one(self, i, _): self.append("1"); await self.update(i)

    @discord.ui.button(label="2", row=2, style=discord.ButtonStyle.secondary)
    async def two(self, i, _): self.append("2"); await self.update(i)

    @discord.ui.button(label="3", row=2, style=discord.ButtonStyle.secondary)
    async def three(self, i, _): self.append("3"); await self.update(i)

    @discord.ui.button(label="−", row=2, style=discord.ButtonStyle.primary)
    async def minus(self, i, _): self.append("-"); await self.update(i)

    @discord.ui.button(label="=", row=2, style=discord.ButtonStyle.success)
    async def equals(self, i, _):
        try:
            self.expression = str(safe_eval(self.expression))
        except Exception:
            self.expression = "Error"
        await self.update(i)

    # ───────── row 3 ─────────
    @discord.ui.button(label="0", row=3, style=discord.ButtonStyle.secondary)
    async def zero(self, i, _): self.append("0"); await self.update(i)

    @discord.ui.button(label=".", row=3, style=discord.ButtonStyle.secondary)
    async def dot(self, i, _): self.append("."); await self.update(i)

    @discord.ui.button(label="+", row=3, style=discord.ButtonStyle.primary)
    async def plus(self, i, _): self.append("+"); await self.update(i)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        if hasattr(self, "message"):
            await self.message.edit(view=self)

class Maths(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="calc",
        description="Open an interactive calculator"
    )
    async def calc(self, interaction: discord.Interaction):
        view = CalculatorView(interaction.user)
        embed = discord.Embed(
            title=CalculatorView.CALCULATOR_TITLE,
            description="```0```",
            color=discord.Color.blurple()
        )

        await interaction.response.send_message(
            embed=embed,
            view=view,
            ephemeral=True
        )

        view.message = await interaction.original_response()

async def setup(bot: commands.Bot):
    await bot.add_cog(Maths(bot))
