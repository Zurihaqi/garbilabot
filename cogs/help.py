import discord
from discord import app_commands
from discord.ext import commands

RPG_COGS = ["ProfileCommands", "EconomyCommands", "ShopCommands", "CombatCommands", "BackgroundTasks"]

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

        # Group RPG cogs under "RPG", exclude EventListener
        options = []
        for cog_name in bot.cogs.keys():
            if cog_name in RPG_COGS:
                if not any(opt.label == "RPG" for opt in options):
                    options.append(discord.SelectOption(label="RPG", value="RPG", description="View all RPG commands"))
            elif cog_name != "EventListener":
                options.append(discord.SelectOption(label=cog_name.capitalize(), value=cog_name, description=f"View commands for {cog_name.capitalize()}"))

        self.add_item(HelpSelect(bot, options))

    def main_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title="📖 Help Menu",
            description="Select a category from the dropdown below to view commands.",
            color=discord.Color.blurple()
        )
        embed.set_footer(text="Use the dropdown to browse commands.")
        return embed

class HelpSelect(discord.ui.Select):
    def __init__(self, bot: commands.Bot, options: list):
        super().__init__(placeholder="Choose a category...", options=options)
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        cog_name = self.values[0]

        embed = discord.Embed(title=f"📂 {cog_name} Commands", color=discord.Color.teal())

        if cog_name == "RPG":
            # Aggregate all RPG cog commands, exclude EventListener
            for name in RPG_COGS:
                cog = self.bot.get_cog(name)
                if not cog:
                    continue
                for cmd in cog.get_app_commands():
                    embed.add_field(name=f"• `/{cmd.name}`", value=cmd.description or "No description", inline=False)
        else:
            cog = self.bot.get_cog(cog_name)
            if not cog or cog_name == "EventListener":
                await interaction.response.send_message("Cog not found.", ephemeral=True)
                return
            for cmd in cog.get_app_commands():
                embed.add_field(name=f"• `/{cmd.name}`", value=cmd.description or "No description", inline=False)

        embed.set_footer(text="Use /<command> to run a command.")
        await interaction.response.edit_message(embed=embed, view=self.view)

async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))
