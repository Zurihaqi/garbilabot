import os, math, discord
from dotenv import load_dotenv

load_dotenv()

TOKEN          = os.getenv("DISCORD_BOT_TOKEN")
GIPHY_API_KEY  = os.getenv("GIPHY_API_KEY")
OWNER_ID       = os.getenv("OWNER_ID")
MC_SERVER_PATH = os.getenv("MC_SERVER_PATH")

INTENTS = discord.Intents.default()
INTENTS.message_content = True

ALLOWED_MATH = {name: obj for name, obj in math.__dict__.items()
                if not name.startswith("__")}
