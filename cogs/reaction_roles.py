import discord
import aiosqlite
from discord import app_commands
from discord.ext import commands
from utils.permissions import is_owner_slash

DB_PATH = "reaction_roles.db"


def normalize_emoji(emoji: discord.PartialEmoji | str) -> str:
    """Normalize emoji to a consistent string format"""
    if isinstance(emoji, discord.PartialEmoji):
        # For custom emojis, use the ID; for unicode, use the name
        if emoji.id:
            return str(emoji.id)
        return emoji.name or str(emoji)
    # For string emojis (unicode), return as-is
    return str(emoji)


class ReactionRoles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: aiosqlite.Connection | None = None

    # -------------------------------------------------
    # LIFECYCLE
    # -------------------------------------------------

    async def cog_load(self):
        self.db = await aiosqlite.connect(DB_PATH)

        # Table for reaction roles (emoji → role mapping per message)
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS reaction_roles (
                guild_id   INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                message_id INTEGER NOT NULL,
                emoji      TEXT    NOT NULL,
                role_id    INTEGER NOT NULL,
                UNIQUE(message_id, emoji)
            )
            """
        )

        # Table to track which messages are reaction role menus
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS reaction_role_messages (
                guild_id   INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                message_id INTEGER NOT NULL,
                UNIQUE(message_id)
            )
            """
        )

        await self.db.commit()

    async def cog_unload(self):
        if self.db:
            await self.db.close()

    # -------------------------------------------------
    # ADD
    # -------------------------------------------------

    @app_commands.command(name="reactionrole_add", description="Add a reaction role")
    @is_owner_slash()
    async def add(
        self,
        interaction: discord.Interaction,
        emoji: str,
        role: discord.Role,
        channel: discord.TextChannel | None = None,
    ):
        guild = interaction.guild
        if not guild:
            return await interaction.response.send_message(
                "❌ This command can only be used in a server.", ephemeral=True
            )

        bot_member = guild.me or guild.get_member(self.bot.user.id)
        if role.managed or role >= bot_member.top_role:
            return await interaction.response.send_message(
                "❌ I cannot assign that role.", ephemeral=True
            )

        # Store the emoji as-is (unicode emojis will be stored as unicode)
        emoji_key = emoji.strip()

        # Store with message_id = 0 initially (will be updated when /roles is called)
        await self.db.execute(
            """
            INSERT OR REPLACE INTO reaction_roles (guild_id, channel_id, message_id, emoji, role_id)
            VALUES (?, ?, 0, ?, ?)
            """,
            (guild.id, channel.id if channel else 0, emoji_key, role.id),
        )
        await self.db.commit()

        await interaction.response.send_message(
            f"✅ {emoji} → {role.name} has been added to the list", ephemeral=True
        )

    # -------------------------------------------------
    # LIST (ADMIN)
    # -------------------------------------------------

    @app_commands.command(name="reactionrole_list", description="List all reaction roles")
    @is_owner_slash()
    async def list_roles(self, interaction: discord.Interaction):
        cursor = await self.db.execute(
            """
            SELECT channel_id, message_id, emoji, role_id
            FROM reaction_roles
            WHERE guild_id = ?
            ORDER BY channel_id
            """,
            (interaction.guild.id,),
        )
        rows = await cursor.fetchall()

        if not rows:
            return await interaction.response.send_message(
                "ℹ️ No reaction roles configured.", ephemeral=True
            )

        lines = []
        for channel_id, msg_id, emoji, role_id in rows:
            role = interaction.guild.get_role(role_id)
            channel = interaction.guild.get_channel(channel_id)
            lines.append(
                f"{emoji} → {role.mention if role else role_id} "
                f"(#{channel.name if channel else channel_id}, msg `{msg_id}`)"
            )

        embed = discord.Embed(
            title="📋 Reaction Roles",
            description="\n".join(lines),
            color=discord.Color.teal(),
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # -------------------------------------------------
    # USER VIEW
    # -------------------------------------------------

    @app_commands.command(name="roles", description="Choose your roles")
    async def roles(self, interaction: discord.Interaction):
        try:
            # Defer immediately to prevent timeout
            print(f"[DEBUG] Starting /roles command for guild {interaction.guild_id}")
            await interaction.response.defer()
            print(f"[DEBUG] Deferred successfully")
            
            guild = interaction.guild
            channel = interaction.channel

            if not guild or not isinstance(channel, discord.TextChannel):
                await interaction.followup.send(
                    "❌ This command can only be used in a server channel.",
                    ephemeral=True,
                )
                return

            print(f"[DEBUG] Fetching roles from database...")
            cursor = await self.db.execute(
                """
                SELECT DISTINCT emoji, role_id
                FROM reaction_roles
                WHERE guild_id = ?
                ORDER BY role_id
                """,
                (guild.id,),
            )
            rows = await cursor.fetchall()
            print(f"[DEBUG] Found {len(rows)} reaction roles")

            if not rows:
                await interaction.followup.send(
                    "❌ No self-assignable roles available.",
                    ephemeral=True,
                )
                return

            lines = []
            emojis = []

            for emoji, role_id in rows:
                role = guild.get_role(role_id)
                if role:
                    lines.append(f"{emoji} → {role.mention}")
                    emojis.append(emoji)

            if not lines:
                await interaction.followup.send(
                    "❌ No valid roles found.",
                    ephemeral=True,
                )
                return

            embed = discord.Embed(
                title="🎭 Choose Your Roles",
                description="\n".join(lines),
                color=discord.Color.blurple(),
            )

            print(f"[DEBUG] Sending embed with {len(emojis)} emojis...")
            message = await interaction.followup.send(embed=embed, wait=True)
            print(f"[DEBUG] Message sent with ID: {message.id}")

            # Add reactions
            for emoji in emojis:
                try:
                    await message.add_reaction(emoji)
                    print(f"[DEBUG] Added reaction: {emoji}")
                except discord.HTTPException as e:
                    print(f"[ERROR] Failed to add reaction {emoji}: {e}")

            # Update all reaction_roles entries to link to this message
            for emoji in emojis:
                await self.db.execute(
                    """
                    UPDATE reaction_roles
                    SET message_id = ?, channel_id = ?
                    WHERE guild_id = ? AND emoji = ? AND message_id = 0
                    """,
                    (message.id, channel.id, guild.id, emoji),
                )

            # Track this message
            await self.db.execute(
                """
                INSERT OR IGNORE INTO reaction_role_messages (guild_id, channel_id, message_id)
                VALUES (?, ?, ?)
                """,
                (guild.id, channel.id, message.id),
            )
            await self.db.commit()
            print(f"[DEBUG] Database updated successfully")
            
        except Exception as e:
            print(f"[ERROR] Exception in /roles command: {e}")
            import traceback
            traceback.print_exc()
            raise

    # -------------------------------------------------
    # REMOVE
    # -------------------------------------------------

    @app_commands.command(name="reactionrole_debug", description="Debug reaction roles")
    @is_owner_slash()
    async def debug(self, interaction: discord.Interaction):
        """Debug command to see what's in the database"""
        cursor = await self.db.execute(
            """
            SELECT message_id, emoji, role_id
            FROM reaction_roles
            WHERE guild_id = ?
            """,
            (interaction.guild.id,),
        )
        rows = await cursor.fetchall()
        
        cursor2 = await self.db.execute(
            """
            SELECT message_id
            FROM reaction_role_messages
            WHERE guild_id = ?
            """,
            (interaction.guild.id,),
        )
        tracked = await cursor2.fetchall()
        
        lines = ["**Reaction Roles:**"]
        for msg_id, emoji, role_id in rows:
            role = interaction.guild.get_role(role_id)
            lines.append(f"Msg: `{msg_id}` | Emoji: `{repr(emoji)}` | Role: {role.mention if role else role_id}")
        
        lines.append("\n**Tracked Messages:**")
        for (msg_id,) in tracked:
            lines.append(f"`{msg_id}`")
        
        await interaction.response.send_message("\n".join(lines), ephemeral=True)

    @app_commands.command(name="reactionrole_remove", description="Remove a reaction role")
    @is_owner_slash()
    async def remove(self, interaction: discord.Interaction, message_id: str, emoji: str):
        emoji_key = normalize_emoji(discord.PartialEmoji.from_str(emoji))

        await self.db.execute(
            """
            DELETE FROM reaction_roles
            WHERE message_id = ? AND emoji = ?
            """,
            (int(message_id), emoji_key),
        )
        await self.db.commit()

        await interaction.response.send_message(
            "🗑️ Reaction role removed.", ephemeral=True
        )

    # -------------------------------------------------
    # EDIT
    # -------------------------------------------------

    @app_commands.command(name="reactionrole_edit", description="Edit a reaction role")
    @is_owner_slash()
    async def edit(
        self,
        interaction: discord.Interaction,
        message_id: str,
        emoji: str,
        new_role: discord.Role,
    ):
        emoji_key = normalize_emoji(discord.PartialEmoji.from_str(emoji))

        await self.db.execute(
            """
            UPDATE reaction_roles
            SET role_id = ?
            WHERE message_id = ? AND emoji = ?
            """,
            (new_role.id, int(message_id), emoji_key),
        )
        await self.db.commit()

        await interaction.response.send_message(
            f"✏️ Updated {emoji} → {new_role.mention}", ephemeral=True
        )

    # -------------------------------------------------
    # REACTION EVENTS
    # -------------------------------------------------

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        await self.handle_reaction(payload, add=True)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        await self.handle_reaction(payload, add=False)

    async def handle_reaction(self, payload: discord.RawReactionActionEvent, add: bool):
        print(f"[DEBUG REACTION] Received reaction event: add={add}, user={payload.user_id}, emoji={payload.emoji}")
        
        # Ignore bot's own reactions
        if not self.db or payload.user_id == self.bot.user.id:
            print(f"[DEBUG REACTION] Ignoring - bot's own reaction or no db")
            return
        
        # Check if this message is tracked as a reaction role message
        cursor = await self.db.execute(
            """
            SELECT 1 FROM reaction_role_messages
            WHERE message_id = ?
            """,
            (payload.message_id,),
        )
        is_tracked = await cursor.fetchone()
        print(f"[DEBUG REACTION] Message tracked: {is_tracked is not None}")
        if not is_tracked:
            return
        
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            print(f"[DEBUG REACTION] Guild not found")
            return
        
        member = guild.get_member(payload.user_id)
        if not member:
            print(f"[DEBUG REACTION] Member not found")
            return
        
        # Normalize the emoji from the reaction
        emoji_key = normalize_emoji(payload.emoji)
        print(f"[DEBUG REACTION] Normalized emoji: {emoji_key}")
        
        # Look up role for this emoji and message
        cursor = await self.db.execute(
            """
            SELECT role_id
            FROM reaction_roles
            WHERE message_id = ? AND emoji = ?
            """,
            (payload.message_id, emoji_key),
        )
        role_row = await cursor.fetchone()
        print(f"[DEBUG REACTION] Role found in DB: {role_row}")
        
        if not role_row:
            return
        
        role = guild.get_role(role_row[0])
        if not role:
            print(f"[DEBUG REACTION] Role {role_row[0]} not found in guild")
            return
        
        print(f"[DEBUG REACTION] Attempting to {'add' if add else 'remove'} role {role.name} to/from {member.name}")
        try:
            if add:
                await member.add_roles(role, reason="Reaction role assigned")
                print(f"[DEBUG REACTION] ✅ Successfully added role {role.name}")
            else:
                await member.remove_roles(role, reason="Reaction role removed")
                print(f"[DEBUG REACTION] ✅ Successfully removed role {role.name}")
        except discord.Forbidden as e:
            print(f"[DEBUG REACTION] ❌ Permission denied: {e}")
        except discord.HTTPException as e:
            print(f"[DEBUG REACTION] ❌ HTTP error: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(ReactionRoles(bot))