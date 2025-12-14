from __future__ import annotations
import random
import discord
from discord import app_commands
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
    """One button per remaining player. Disables after voting."""
    def __init__(self, cog: "Undercover", voter: discord.Member):
        super().__init__(timeout=120)
        self.cog = cog
        self.voter = voter

        for player in cog.game["players"]:
            self.add_item(VoteButton(player))

    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True
        if self.message:
            await self.message.edit(view=self)

class VoteButton(discord.ui.Button):
    def __init__(self, target: discord.Member):
        super().__init__(
            label=target.display_name,
            style=discord.ButtonStyle.secondary
        )
        self.target = target

    async def callback(self, interaction: discord.Interaction):
        view: VoteView = self.view
        cog = view.cog
        voter = view.voter

        if voter in cog.game["votes"]:
            await interaction.response.send_message(
                "You have already voted this round!",
                ephemeral=True
            )
            return

        cog.game["votes"][voter] = self.target
        await interaction.response.send_message(
            f"Your vote for **{self.target.display_name}** has been recorded ✅",
            ephemeral=True
        )

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

    @app_commands.command(
        name="undercover",
        description="Start an Undercover game lobby"
    )
    async def undercover_entry(self, interaction: discord.Interaction):
        """Show the Undercover game lobby."""
        embed = self.lobby_embed()
        view = JoinView(self)

        await interaction.response.send_message(
            embed=embed,
            view=view
        )

    async def add_player(self, interaction: discord.Interaction):
        if self.game["started"]:
            await interaction.response.send_message(
                "The game has already started.",
                ephemeral=True
            )
            return

        self.game["players"].add(interaction.user)
        await interaction.response.edit_message(
            embed=self.lobby_embed()
        )

    async def remove_player(self, interaction: discord.Interaction):
        if self.game["started"]:
            await interaction.response.send_message(
                "The game has already started.",
                ephemeral=True
            )
            return

        self.game["players"].discard(interaction.user)
        await interaction.response.edit_message(
            embed=self.lobby_embed()
        )

    async def try_start_game(self, interaction: discord.Interaction):
        if self.game["started"]:
            await interaction.response.send_message(
                "The game is already running.",
                ephemeral=True
            )
            return

        if len(self.game["players"]) < 3:
            await interaction.response.send_message(
                "At least 3 players are required to start.",
                ephemeral=True
            )
            return

        self.game["started"] = True
        self.game["votes"].clear()

        players = list(self.game["players"])
        self.game["undercover"] = random.choice(players)
        normal_word, undercover_word = random.choice(WORD_PAIRS)

        for player in players:
            try:
                if player == self.game["undercover"]:
                    await player.send(
                        f"🕵️ You are **UNDERCOVER**!\nYour word: **{undercover_word}**"
                    )
                else:
                    await player.send(
                        f"✅ You are a normal player.\nYour word: **{normal_word}**"
                    )
            except discord.Forbidden:
                await interaction.channel.send(
                    f"⚠️ Cannot send DM to {player.display_name}."
                )

        await interaction.response.edit_message(
            embed=self.round_embed(),
            view=None
        )

        await self.send_vote_panels(interaction.channel)

    async def send_vote_panels(self, channel: discord.abc.Messageable):
        """Send one private voting panel per player."""
        for player in self.game["players"]:
            try:
                view = VoteView(self, voter=player)
                msg = await player.send(
                    "Who do you think is the undercover? Choose one:",
                    view=view
                )
                view.message = msg
            except discord.Forbidden:
                await channel.send(
                    f"⚠️ {player.display_name} has DMs disabled and cannot vote."
                )

    async def tally_votes(self, public_channel: discord.abc.Messageable):
        counts: dict[discord.Member, int] = {}
        for vote in self.game["votes"].values():
            counts[vote] = counts.get(vote, 0) + 1

        highest = max(counts.values())
        tied_players = [p for p, n in counts.items() if n == highest]
        eliminated = random.choice(tied_players)

        messages = [f"🔎 **{eliminated.display_name}** has been eliminated!"]

        if eliminated == self.game["undercover"]:
            messages.append("🎉 The undercover has been caught! Civilians win!")
            await public_channel.send("\n".join(messages))
            return self.reset()

        messages.append("❌ They were not the undercover. The game continues.")
        self.game["players"].remove(eliminated)

        if len(self.game["players"]) < 3:
            messages.append("🤫 Fewer than 3 players left. Undercover wins!")
            await public_channel.send("\n".join(messages))
            return self.reset()

        self.game["votes"].clear()
        await public_channel.send("\n".join(messages))
        await public_channel.send(embed=self.round_embed())
        await self.send_vote_panels(public_channel)

    def lobby_embed(self) -> discord.Embed:
        player_names = ", ".join(p.display_name for p in self.game["players"]) or "—"
        return (
            discord.Embed(
                title="Undercover Lobby",
                color=0x5865F2
            )
            .add_field(name="Players", value=player_names, inline=False)
            .set_footer(
                text="Click Join / Leave. The host clicks Start Game when ready."
            )
        )

    def round_embed(self) -> discord.Embed:
        return (
            discord.Embed(
                title="🗳️ Voting Started!",
                description="Check your DMs and vote for one suspicious player.",
                color=discord.Color.orange()
            )
            .add_field(
                name="Active Players",
                value=", ".join(p.display_name for p in self.game["players"]),
                inline=False
            )
        )

    def reset(self):
        self.game.update(
            players=set(),
            started=False,
            undercover=None,
            votes={}
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Undercover(bot))
