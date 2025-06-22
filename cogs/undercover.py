from __future__ import annotations
import random
import discord
from discord.ext import commands
from data.word_pairs import WORD_PAIRS

class JoinView(discord.ui.View):
    """Lobby view: Join / Leave / Start buttons."""
    def __init__(self, cog: "Undercover"):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(label="Join", style=discord.ButtonStyle.success, emoji="➕")
    async def join(self, interaction: discord.Interaction, _button: discord.ui.Button):
        await self.cog.add_player(interaction)

    @discord.ui.button(label="Leave", style=discord.ButtonStyle.secondary, emoji="➖")
    async def leave(self, interaction: discord.Interaction, _button: discord.ui.Button):
        await self.cog.remove_player(interaction)

    @discord.ui.button(label="Start Game", style=discord.ButtonStyle.primary, emoji="🎲")
    async def start(self, interaction: discord.Interaction, _button: discord.ui.Button):
        await self.cog.try_start_game(interaction)


class VoteView(discord.ui.View):
    """One button per remaining player. Disappears after vote."""
    def __init__(self, cog: "Undercover", voter: discord.Member):
        super().__init__(timeout=120)
        self.cog = cog
        self.voter = voter

        for p in cog.game["players"]:
            self.add_item(VoteButton(p))

    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True
        if self.message:
            await self.message.edit(view=self)

class VoteButton(discord.ui.Button):
    def __init__(self, target: discord.Member):
        super().__init__(label=target.display_name,
                         style=discord.ButtonStyle.secondary)
        self.target = target

    async def callback(self, interaction: discord.Interaction):
        view: VoteView = self.view
        cog = view.cog
        voter = view.voter

        if voter in cog.game["votes"]:
            await interaction.response.send_message(
                "Kamu sudah vote di ronde ini!", ephemeral=True)
            return

        cog.game["votes"][voter] = self.target
        await interaction.response.send_message(
            f"Vote kamu untuk **{self.target.display_name}** tercatat ✅", ephemeral=True)

        for item in view.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        await view.message.edit(view=view)

        if len(cog.game["votes"]) == len(cog.game["players"]):
            await cog.tally_votes(view.message.channel)

class Undercover(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.game: dict[str, object] = {
            "players": set(),
            "started": False,
            "undercover": None,
            "votes": {},
        }

    @commands.command(name="undercover")
    async def undercover_entry(self, ctx: commands.Context):
        """Menampilkan lobby permainan undercover."""
        embed = self.lobby_embed()
        view  = JoinView(self)
        await ctx.send(embed=embed, view=view)

    async def add_player(self, interaction: discord.Interaction):
        if self.game["started"]:
            await interaction.response.send_message(
                "Game sudah dimulai.", ephemeral=True); return
        self.game["players"].add(interaction.user)
        await interaction.response.edit_message(embed=self.lobby_embed())

    async def remove_player(self, interaction: discord.Interaction):
        if self.game["started"]:
            await interaction.response.send_message(
                "Game sudah dimulai.", ephemeral=True); return
        self.game["players"].discard(interaction.user)
        await interaction.response.edit_message(embed=self.lobby_embed())

    async def try_start_game(self, interaction: discord.Interaction):
        if self.game["started"]:
            await interaction.response.send_message(
                "Game sudah berjalan.", ephemeral=True); return
        if len(self.game["players"]) < 3:
            await interaction.response.send_message(
                "Butuh minimal 3 pemain.", ephemeral=True); return

        self.game["started"] = True
        self.game["votes"].clear()
        players = list(self.game["players"])
        self.game["undercover"] = random.choice(players)
        normal, under = random.choice(WORD_PAIRS)

        for p in players:
            try:
                if p == self.game["undercover"]:
                    await p.send(f"🕵️ Kamu **UNDERCOVER**! Kata: **{under}**")
                else:
                    await p.send(f"✅ Kamu warga biasa. Kata: **{normal}**")
            except discord.Forbidden:
                await interaction.channel.send(
                    f"⚠️ Tidak bisa kirim DM ke {p.display_name}.")

        await interaction.response.edit_message(
            embed=self.round_embed(), view=None)
        await self.send_vote_panels(interaction.channel)

    async def send_vote_panels(self, channel: discord.abc.Messageable):
        """Send one ephemeral voting panel per player."""
        for p in self.game["players"]:
            try:
                view = VoteView(self, voter=p)
                msg = await p.send("Siapa undercover? Pilih satu:", view=view)
                view.message = msg   # save for later editing
            except discord.Forbidden:
                await channel.send(
                    f"⚠️ {p.display_name} menutup DM, tidak bisa voting.")

    async def tally_votes(self, public_channel: discord.abc.Messageable):
        counts: dict[discord.Member, int] = {}
        for v in self.game["votes"].values():
            counts[v] = counts.get(v, 0) + 1

        highest = max(counts.values())
        out_players = [p for p, n in counts.items() if n == highest]
        eliminated = random.choice(out_players)

        outcome = [f"🔎 {eliminated.display_name} tersingkir!"]
        if eliminated == self.game["undercover"]:
            outcome.append("🎉 Undercover ketahuan! Warga menang!")
            await public_channel.send("\n".join(outcome))
            return self.reset()
        else:
            outcome.append("❌ Bukan undercover. Game lanjut.")
            self.game["players"].remove(eliminated)

            if len(self.game["players"]) < 3:
                outcome.append("🤫 Pemain < 3. Undercover menang!")
                await public_channel.send("\n".join(outcome))
                return self.reset()

            self.game["votes"].clear()
            await public_channel.send("\n".join(outcome))
            await public_channel.send(embed=self.round_embed())
            await self.send_vote_panels(public_channel)

    def lobby_embed(self) -> discord.Embed:
        names = ", ".join(p.display_name for p in self.game["players"]) or "—"
        return (discord.Embed(title="Undercover Lobby", colour=0x5865F2)
                .add_field(name="Pemain", value=names, inline=False)
                .set_footer(text="Klik Join / Leave. Host klik Start Game ketika siap."))

    def round_embed(self) -> discord.Embed:
        return (discord.Embed(title="🗳️ Voting Dimulai!",
                              description="Periksa DM kamu → Pilih 1 pemain yang dicurigai.",
                              colour=discord.Color.orange())
                .add_field(name="Pemain Aktif",
                           value=", ".join(p.display_name
                                           for p in self.game["players"]),
                           inline=False))

    def reset(self):
        self.game.update(players=set(), started=False,
                         undercover=None, votes={})

async def setup(bot: commands.Bot):
    await bot.add_cog(Undercover(bot))
