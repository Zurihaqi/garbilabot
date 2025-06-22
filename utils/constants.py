import os, math, discord
from dotenv import load_dotenv

load_dotenv()

TOKEN          = os.getenv("DISCORD_BOT_TOKEN")
GIPHY_API_KEY  = os.getenv("GIPHY_API_KEY")
OWNER_ID       = os.getenv("OWNER_ID")
MC_SERVER_PATH = os.getenv("MC_SERVER_PATH")

LUCK_STATUSES = [
    ("🍀", "Main Character Energy - Lock in"),
    ("⭐", "Plot Armor Activated - RNGesus loves you"),
    ("🌟", "Mid Tier Luck - Bros on 50:50"),
    ("😐", "NPC Mode - Nothing special, just existing"),
    ("😞", "Cursed Build - L + Ratio + Skill Issue"),
    ("💀", "Delete This Day - Touch grass, it's over")
]

INTENTS = discord.Intents.default()
INTENTS.message_content = True

LOG_FORMAT = "[%(levelname)-5s] [%(asctime)s] %(name)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

ALLOWED_MATH = {name: obj for name, obj in math.__dict__.items()
                if not name.startswith("__")}
