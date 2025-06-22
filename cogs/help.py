import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx: commands.Context):
        """Menampilkan menu bantuan (help)."""
        view = HelpMenuView(self.bot)
        embed = view.main_embed()
        await ctx.send(embed=embed, view=view)

class HelpMenuView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=180)
        self.bot = bot

        for cog_name, cog in bot.cogs.items():
            label = cog_name.capitalize()
            self.add_item(HelpButton(cog_name, label))

    def main_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title="📖 Help Menu",
            description="Pilih kategori di bawah untuk melihat daftar command.",
            color=discord.Color.blurple()
        )
        embed.set_footer(text="Gunakan tombol untuk menjelajahi command.")
        return embed


class HelpButton(discord.ui.Button):
    def __init__(self, cog_name: str, label: str):
        super().__init__(label=label, style=discord.ButtonStyle.secondary)
        self.cog_name = cog_name

    async def callback(self, interaction: discord.Interaction):
        bot = self.view.bot
        cog = bot.get_cog(self.cog_name)

        if not cog:
            await interaction.response.send_message("Cog tidak ditemukan.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"📂 {self.cog_name.capitalize()} Commands",
            color=discord.Color.teal()
        )

        for command in cog.get_commands():
            if not command.hidden:
                embed.add_field(
                    name=f"• `{command.name}`",
                    value=command.help or "Tidak ada deskripsi.",
                    inline=False
                )

        embed.set_footer(text="Ketik !<command> untuk menggunakan command.")
        await interaction.response.edit_message(embed=embed, view=self.view)


async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))
