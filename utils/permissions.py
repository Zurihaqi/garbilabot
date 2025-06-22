from discord.ext import commands
from .constants import OWNER_ID, ALLOWED_MATH

def is_owner():
    async def predicate(ctx):
        return ctx.author.id == OWNER_ID
    return commands.check(predicate)

def safe_eval(expr: str):
    return eval(expr, {"__builtins__": None}, ALLOWED_MATH)
