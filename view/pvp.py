from typing import Optional

import discord
from discord.ui import View, Button


class PvPChallengeView(View):
    """View for accepting/declining PvP challenges"""
    
    def __init__(self, challenger: discord.User, target: discord.User, timeout: int = 60):
        super().__init__(timeout=timeout)
        self.challenger = challenger
        self.target = target
        self.accepted = None
        self.message: Optional[discord.Message] = None
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Only the target can interact"""
        if interaction.user.id != self.target.id:
            await interaction.response.send_message(
                "❌ This challenge isn't for you!",
                ephemeral=True
            )
            return False
        return True
    
    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green, emoji="⚔️")
    async def accept_button(self, interaction: discord.Interaction, button: Button):
        self.accepted = True
        self.stop()
        await interaction.response.edit_message(
            content=f"✅ {self.target.mention} accepted the challenge!",
            view=None
        )
    
    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red, emoji="❌")
    async def decline_button(self, interaction: discord.Interaction, button: Button):
        self.accepted = False
        self.stop()
        await interaction.response.edit_message(
            content=f"❌ {self.target.mention} declined the challenge.",
            view=None
        )
    
    async def on_timeout(self):
        """Called when view times out"""
        if self.message and not self.accepted:
            try:
                await self.message.edit(
                    content=f"⏱️ Challenge timed out. {self.target.mention} didn't respond.",
                    view=None
                )
            except:
                pass