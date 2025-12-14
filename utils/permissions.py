import discord
from discord import app_commands
from .constants import OWNER_ID, ALLOWED_MATH

def is_owner_slash():
    def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.id == OWNER_ID
    return app_commands.check(predicate)

def safe_eval(expression: str):
    """
    Safely evaluate a math expression using a restricted namespace.

    Allowed symbols are defined in ALLOWED_MATH.
    """
    return eval(
        expression,
        {"__builtins__": None},
        ALLOWED_MATH
    )
