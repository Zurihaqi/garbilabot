import discord
from discord import app_commands
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="help",
        description="Show the help menu"
    )
    async def help_command(self, interaction: discord.Interaction):
        """Display the help menu."""
        view = HelpMenuView(self.bot)
        embed = view.main_embed()
        await interaction.response.send_message(
            embed=embed,
            view=view,
            ephemeral=True
        )

class HelpMenuView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=180)
        self.bot = bot

        options = [
            discord.SelectOption(
                label=cog_name.capitalize(),
                value=cog_name,
                description=f"View commands for {cog_name.capitalize()}"
            )
            for cog_name in bot.cogs.keys()
        ]

        self.add_item(HelpSelect(bot, options))

    def main_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title="📖 Help Menu",
            description="Select a category from the dropdown below to view commands.",
            color=discord.Color.blurple()
        )
        embed.set_footer(
            text="Use the dropdown to browse commands."
        )
        return embed

class HelpSelect(discord.ui.Select):
    def __init__(self, bot: commands.Bot, options: list):
        super().__init__(placeholder="Choose a category...", options=options)
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        cog_name = self.values[0]
        cog = self.bot.get_cog(cog_name)

        if not cog:
            await interaction.response.send_message(
                "Cog not found.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"📂 {cog_name.capitalize()} Commands",
            color=discord.Color.teal()
        )

        for command in cog.get_app_commands():
            embed.add_field(
                name=f"• `/{command.name}`",
                value=command.description or "No description available.",
                inline=False
            )

        embed.set_footer(
            text="Use /<command> to run a command."
        )

        await interaction.response.edit_message(embed=embed, view=self.view)

async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))
