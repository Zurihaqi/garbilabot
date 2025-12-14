import discord
from discord import app_commands
from .constants import ALLOWED_MATH, ROLE_ID

def has_role_slash():
    """Check if the user has a specific role (by ID)"""
    def predicate(interaction: discord.Interaction) -> bool:
        # Make sure the interaction user is a Member (not a User)
        if isinstance(interaction.user, discord.Member):
            return any(role.id == ROLE_ID for role in interaction.user.roles)
        return False
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
