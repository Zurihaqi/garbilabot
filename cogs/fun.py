import random
import sqlite3
from datetime import date, datetime, timedelta
import asyncio
import aiohttp
import discord
from discord import app_commands, Embed, Color
from discord.ext import commands, tasks

from utils.constants import GIPHY_API_KEY, LUCK_STATUSES

DB_PATH = "fun.db"

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
# Luck table
c.execute("""
CREATE TABLE IF NOT EXISTS user_luck (
    user_id INTEGER PRIMARY KEY,
    last_date TEXT
)
""")
# Reminders table
c.execute("""
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    channel_id INTEGER,
    message TEXT,
    remind_at TEXT
)
""")
conn.commit()

class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.check_reminders.start()

    @app_commands.command(
        name="luck",
        description="What is your luck for today?"
    )
    async def todays_luck(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        today_str = date.today().isoformat()

        c.execute("SELECT last_date FROM user_luck WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        if row and row[0] == today_str:
            await interaction.response.send_message(
                "⚠️ You have already checked your luck today. Try again tomorrow!",
                ephemeral=True
            )
            return

        final_results = [random.choice(LUCK_STATUSES) for _ in range(3)]
        final_emoji, final_text = final_results[1]

        embed = Embed(
            title="You are feeling...",
            description=f"\n**{final_emoji} {final_text}** today!\n",
            color=Color.gold(),
        )

        c.execute(
            "INSERT INTO user_luck (user_id, last_date) VALUES (?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET last_date = ?",
            (user_id, today_str, today_str)
        )
        conn.commit()
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="random",
        description="Get a random gif"
    )
    async def random_gif(self, interaction: discord.Interaction):
        await interaction.response.defer()
        url = (
            f"https://api.giphy.com/v1/gifs/random"
            f"?api_key={GIPHY_API_KEY}&rating=R&tag=brainrot"
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
        gif_url = data["data"]["images"]["original"]["url"]
        await interaction.followup.send(gif_url)

    @app_commands.command(
        name="8ball",
        description="Ask the magic 8-ball a question"
    )
    async def eight_ball(self, interaction: discord.Interaction, question: str):
        responses = [
            "It is certain", "It is decidedly so", "Without a doubt", "Yes – definitely",
            "You may rely on it", "As I see it, yes", "Most likely", "Outlook good",
            "Yes", "Signs point to yes", "Reply hazy, try again", "Ask again later",
            "Better not tell you now", "Cannot predict now", "Concentrate and ask again",
            "Don't count on it", "My reply is no", "My sources say no", "Outlook not so good",
            "Very doubtful"
        ]
        answer = random.choice(responses)
        embed = Embed(
            title="🎱 Magic 8-Ball",
            description=f"**Question:** {question}\n**Answer:** {answer}",
            color=Color.purple()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="remind",
        description="Set a reminder"
    )
    async def remind(self, interaction: discord.Interaction, time: str, *, message: str):
        """
        time: format like '10m', '2h', '1d'
        """
        unit = time[-1]
        try:
            amount = int(time[:-1])
        except ValueError:
            await interaction.response.send_message("⚠️ Invalid time format.", ephemeral=True)
            return

        if unit == "m":
            delta = timedelta(minutes=amount)
        elif unit == "h":
            delta = timedelta(hours=amount)
        elif unit == "d":
            delta = timedelta(days=amount)
        else:
            await interaction.response.send_message("⚠️ Invalid time unit. Use m, h, or d.", ephemeral=True)
            return

        remind_at = datetime.now() + delta
        c.execute(
            "INSERT INTO reminders (user_id, channel_id, message, remind_at) VALUES (?, ?, ?, ?)",
            (interaction.user.id, interaction.channel.id, message, remind_at.isoformat())
        )
        conn.commit()
        await interaction.response.send_message(f"⏰ Reminder set for {time} from now!", ephemeral=True)

    @tasks.loop(seconds=60)
    async def check_reminders(self):
        now = datetime.now()
        c.execute("SELECT id, user_id, channel_id, message FROM reminders WHERE remind_at <= ?", (now.isoformat(),))
        rows = c.fetchall()
        for r_id, user_id, channel_id, message in rows:
            channel = self.bot.get_channel(channel_id)
            user = self.bot.get_user(user_id)
            if channel and user:
                await channel.send(f"⏰ {user.mention}, reminder: {message}")
            c.execute("DELETE FROM reminders WHERE id = ?", (r_id,))
            conn.commit()

    @check_reminders.before_loop
    async def before_reminders(self):
        await self.bot.wait_until_ready()


    @app_commands.command(
        name="giveaway",
        description="Start a giveaway with optional duration and multiple prizes"
    )
    @app_commands.describe(
        duration="Duration (e.g., 1m, 2h, 1d)",
        prizes="Comma-separated prizes (e.g., Prize1:50,Prize2:30,Prize3:20)",
        winners="Number of winners (default 1)"
    )
    async def giveaway(
        self,
        interaction: discord.Interaction,
        duration: str,
        prizes: str,
        winners: int = 1
    ):
        unit = duration[-1]
        try:
            amount = int(duration[:-1])
        except ValueError:
            await interaction.response.send_message("⚠️ Invalid duration format.", ephemeral=True)
            return

        if unit == "m":
            delta_seconds = amount * 60
        elif unit == "h":
            delta_seconds = amount * 3600
        elif unit == "d":
            delta_seconds = amount * 86400
        else:
            await interaction.response.send_message("⚠️ Invalid duration unit. Use m, h, or d.", ephemeral=True)
            return

        # Parse prizes: "Prize1:50,Prize2:30,Prize3:20"
        prize_list = []
        total_chance = 0
        try:
            for item in prizes.split(","):
                name, chance = item.split(":")
                chance = int(chance)
                total_chance += chance
                prize_list.append((name.strip(), chance))
        except Exception:
            await interaction.response.send_message("⚠️ Invalid prizes format. Example: Prize1:50,Prize2:30", ephemeral=True)
            return

        if total_chance <= 0:
            await interaction.response.send_message("⚠️ Total chance must be greater than 0.", ephemeral=True)
            return

        embed = Embed(
            title="🎉 Giveaway Started!",
            description=(
                f"React with 🎉 to enter!\n"
                f"Duration: {duration}\n"
                f"Winners: {winners}\n"
                f"Prizes: {', '.join([p[0] for p in prize_list])}\n\n"
            ),
            color=Color.green()
        )
        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        await message.add_reaction("🎉")

        for remaining in range(delta_seconds, 0, -10):
            try:
                minutes, seconds = divmod(remaining, 60)
                hours, minutes = divmod(minutes, 60)
                time_str = f"{hours}h {minutes}m {seconds}s"

                if hours:
                    time_str = f"{hours}h {minutes}m {seconds}s"
                elif minutes:
                    time_str = f"{minutes}m {seconds}s"
                else:
                    time_str = f"{seconds}s"

                embed.set_footer(text=f"⏳ Time left: {time_str}")
                await message.edit(embed=embed)
                await asyncio.sleep(min(10, remaining))
            except discord.NotFound:
                break 

        message = await interaction.channel.fetch_message(message.id)
        reaction = discord.utils.get(message.reactions, emoji="🎉")
        if not reaction:
            await interaction.followup.send("No participants, giveaway cancelled.")
            return

        users = [u async for u in reaction.users() if not u.bot]
        if not users:
            await interaction.followup.send("No participants, giveaway cancelled.")
            return

        winners_results = []
        for prize_name, chance in prize_list:
            eligible_users = users.copy()
            if not eligible_users:
                break
            for _ in range(winners):
                winner = random.choices(
                    population=eligible_users,
                    weights=[chance]*len(eligible_users),
                    k=1
                )[0]
                winners_results.append((winner, prize_name))
                eligible_users.remove(winner)

        result_text = "\n".join(f"🎁 {winner.mention} won **{prize}**!" for winner, prize in winners_results)
        await interaction.followup.send(result_text)

async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))
