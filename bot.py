import os
import sqlite3
import discord
from discord.ext import commands
from datetime import timedelta

conn = sqlite3.connect("/data/database.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS warns (
    user_id TEXT,
    reason TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS levels (
    user_id TEXT PRIMARY KEY,
    level INTEGER,
    messages INTEGER
)
""")

conn.commit()

afk_users = {}

ROLE_MESSAGE_ID = None

reaction_roles = {
    "❤️": "Red",
    "💛": "Yellow",
    "💙": "Blue",
    "💚": "Green",
    "💜": "Purple",
    "🖤": "Black",
    "🤍": "White",
    "🧡": "Orange",
    "🩷": "Pink"
}

WELCOME_CHANNEL_ID = 1494196869834870916

MSG_LOG_CHANNEL_ID = 1510789707590668389

intents = discord.Intents.default()

intents.members = True
intents.message_content = True
intents.reactions = True
intents.guilds = True

bot = commands.Bot(
    command_prefix=".",
    intents=intents
)

@bot.event
async def on_ready():

    print(f"Logged in as {bot.user}")

@bot.event
async def on_member_join(member):

    role = discord.utils.get(
        member.guild.roles,
        name="Follower"
    )

    if role is not None:
        await member.add_roles(role)

    channel = bot.get_channel(
        WELCOME_CHANNEL_ID
    )

    if channel is not None:

        embed = discord.Embed(
            title="Welcome!",
            description=(
                f"🎀 Welcome "
                f"{member.mention}!\n"
                f"Please read the <#1500746326651047946> and enjoy your stay~!"
            ),
            color=discord.Color(
                int("F594D7", 16)
            )
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        embed.set_footer(
            text=(
                f"Member "
                f"#{member.guild.member_count}"
            )
        )

        await channel.send(embed=embed)

@bot.command(name="setup_roles")
@commands.has_permissions(
    administrator=True
)
async def setup_roles(ctx):

    embed = discord.Embed(
        title="Choose Your Color Role",
        description=(
            "React below to get a role!\n\n"
            "❤️ = Red\n"
            "💛 = Yellow\n"
            "💙 = Blue\n"
            "💚 = Green\n"
            "💜 = Purple\n"
            "🖤 = Black\n"
            "🤍 = White\n"
            "🧡 = Orange\n"
            "🩷 = Pink"
        ),
        color=discord.Color(
            int("F594D7", 16)
        )
    )

    msg = await ctx.send(embed=embed)

    global ROLE_MESSAGE_ID

    ROLE_MESSAGE_ID = msg.id

    reactions = [
        "❤️",
        "💛",
        "💙",
        "💚",
        "💜",
        "🖤",
        "🤍",
        "🧡",
        "🩷"
    ]

    for reaction in reactions:

        await msg.add_reaction(reaction)

@bot.event
async def on_raw_reaction_add(payload):

    if payload.message_id != ROLE_MESSAGE_ID:
        return

    guild = bot.get_guild(
        payload.guild_id
    )

    if guild is None:
        return

    member = guild.get_member(
        payload.user_id
    )

    if member is None or member.bot:
        return

    emoji = str(payload.emoji)

    if emoji in reaction_roles:

        role_name = reaction_roles[emoji]

        role = discord.utils.get(
            guild.roles,
            name=role_name
        )

        if role is not None:

            await member.add_roles(role)

@bot.event
async def on_raw_reaction_remove(payload):

    if payload.message_id != ROLE_MESSAGE_ID:
        return

    guild = bot.get_guild(
        payload.guild_id
    )

    if guild is None:
        return

    member = guild.get_member(
        payload.user_id
    )

    if member is None:
        return

    emoji = str(payload.emoji)

    if emoji in reaction_roles:

        role_name = reaction_roles[emoji]

        role = discord.utils.get(
            guild.roles,
            name=role_name
        )

        if role is not None:

            await member.remove_roles(role)

@bot.command(name="afk")
async def afk(ctx, *, reason="AFK"):

    afk_users[ctx.author.id] = reason

    embed = discord.Embed(
        description=(
            f"💤 {ctx.author.mention} "
            f"is now AFK.\n"
            f"Reason: {reason}"
        ),
        color=discord.Color(
            int("F594D7", 16)
        )
    )

    await ctx.send(embed=embed)

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    user_id = str(message.author.id)

    cursor.execute(
        """
        SELECT level, messages
        FROM levels
        WHERE user_id = ?
        """,
        (user_id,)
    )

    data = cursor.fetchone()

    if data is None:

        level = 0
        messages = 0

        cursor.execute(
            """
            INSERT INTO levels
            VALUES (?, ?, ?)
            """,
            (user_id, level, messages)
        )

        conn.commit()

    else:

        level, messages = data

    messages += 1

    if messages >= 100:

        messages = 0
        level += 1

        embed = discord.Embed(
            description=(
                f"🎉 {message.author.mention} "
                f"leveled up!\n"
                f"New Level: {level}"
            ),
            color=discord.Color(
                int("F594D7", 16)
            )
        )

        await message.channel.send(
            embed=embed
        )

    cursor.execute(
        """
        UPDATE levels
        SET level = ?, messages = ?
        WHERE user_id = ?
        """,
        (level, messages, user_id)
    )

    conn.commit()

    if message.author.id in afk_users:

        del afk_users[
            message.author.id
        ]

        embed = discord.Embed(
            description=(
                f"✅ Welcome back "
                f"{message.author.mention}"
            ),
            color=discord.Color(
                int("F594D7", 16)
            )
        )

        await message.channel.send(
            embed=embed
        )

    for user in message.mentions:

        if user.id in afk_users:

            reason = afk_users[user.id]

            embed = discord.Embed(
                description=(
                    f"💤 {user.mention} "
                    f"is AFK.\n"
                    f"Reason: {reason}"
                ),
                color=discord.Color(
                    int("F594D7", 16)
                )
            )

            await message.channel.send(
                embed=embed
            )

    await bot.process_commands(
        message
    )

@bot.command(name="level")
async def level(
    ctx,
    member: discord.Member = None
):

    if member is None:
        member = ctx.author

    user_id = str(member.id)

    cursor.execute(
        """
        SELECT level, messages
        FROM levels
        WHERE user_id = ?
        """,
        (user_id,)
    )

    data = cursor.fetchone()

    if data is None:

        level_num = 0
        current_msgs = 0

    else:

        level_num, current_msgs = data

    embed = discord.Embed(
        title=f"{member}'s Level",
        description=(
            f"⭐ Level: {level_num}\n"
            f"💬 Messages: "
            f"{current_msgs}/100"
        ),
        color=discord.Color(
            int("F594D7", 16)
        )
    )

    await ctx.send(embed=embed)

@bot.command(name="warn")
@commands.has_permissions(
    moderate_members=True
)
async def warn(
    ctx,
    member: discord.Member,
    *,
    reason="No reason provided"
):

    user_id = str(member.id)

    cursor.execute(
        """
        INSERT INTO warns
        VALUES (?, ?)
        """,
        (user_id, reason)
    )

    conn.commit()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM warns
        WHERE user_id = ?
        """,
        (user_id,)
    )

    warn_count = cursor.fetchone()[0]

    embed = discord.Embed(
        description=(
            f"⚠️ Warned "
            f"{member.mention}\n"
            f"Warns: {warn_count}\n"
            f"Reason: {reason}"
        ),
        color=discord.Color(
            int("F594D7", 16)
        )
    )

    await ctx.send(embed=embed)

@bot.command(name="showwarns")
async def show_warns(
    ctx,
    member: discord.Member
):

    user_id = str(member.id)

    cursor.execute(
        """
        SELECT reason
        FROM warns
        WHERE user_id = ?
        """,
        (user_id,)
    )

    data = cursor.fetchall()

    if len(data) == 0:

        embed = discord.Embed(
            description=(
                f"{member.mention} "
                f"has no warns."
            ),
            color=discord.Color(
                int("F594D7", 16)
            )
        )

        await ctx.send(embed=embed)

        return

    warn_text = ""

    for i, warn in enumerate(
        data,
        start=1
    ):

        warn_text += (
            f"{i}. {warn[0]}\n"
        )

    embed = discord.Embed(
        title=f"Warns for {member}",
        description=warn_text,
        color=discord.Color(
            int("F594D7", 16)
        )
    )

    await ctx.send(embed=embed)

@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban(
    ctx,
    member: discord.Member,
    *,
    reason="No reason provided"
):

    dm_embed = discord.Embed(
        title="You were banned",
        description=(
            f"Server: {ctx.guild.name}\n"
            f"Reason: {reason}"
        ),
        color=discord.Color(int("F594D7", 16))
    )

    try:
        await member.send(embed=dm_embed)
    except discord.Forbidden:
        pass

    await member.ban(reason=reason)

    embed = discord.Embed(
        description=(
            f"🔨 Banned {member.mention}\n"
            f"Reason: {reason}"
        ),
        color=discord.Color(int("F594D7", 16))
    )

    await ctx.send(embed=embed)

@bot.command(name="unban")
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member_name):

    banned_users = [entry async for entry in ctx.guild.bans()]

    for ban_entry in banned_users:

        user = ban_entry.user

        if str(user) == member_name:

            await ctx.guild.unban(user)

            try:
                await user.send(
                    f"You have been unbanned from **{ctx.guild.name}**."
                )
            except:
                pass

            embed = discord.Embed(
                description=f"✅ Unbanned {user}",
                color=discord.Color(int("F594D7", 16))
            )

            await ctx.send(embed=embed)
            return

    await ctx.send("❌ User not found in ban list.")

@bot.command(name="to")
@commands.has_permissions(moderate_members=True)
async def timeout(
    ctx,
    member: discord.Member,
    duration: str,
    *,
    reason="No reason provided"
):

    try:

        unit = duration[-1]
        amount = int(duration[:-1])

        if unit == "s":
            delta = timedelta(seconds=amount)

        elif unit == "m":
            delta = timedelta(minutes=amount)

        elif unit == "h":
            delta = timedelta(hours=amount)

        elif unit == "d":
            delta = timedelta(days=amount)

        else:
            await ctx.send(
                "Use s, m, h, or d."
            )
            return

        await member.edit(
            timed_out_until=discord.utils.utcnow() + delta,
            reason=reason
        )

        embed = discord.Embed(
            description=(
                f"✅ Timed out {member.mention} "
                f"({member}) for {duration}.\n"
                f"Reason: {reason}"
            ),
            color=discord.Color(int("F594D7", 16))
        )

        await ctx.send(embed=embed)

    except:

        error_embed = discord.Embed(
            description=(
                "❌ Invalid format.\n"
                "Example: `.to @user 5h spamming`"
            ),
            color=discord.Color(int("FF4F7B", 16))
        )

        await ctx.send(embed=error_embed)

@bot.command(name="um")
@commands.has_permissions(moderate_members=True)
async def untimeout(ctx, member: discord.Member):

    await member.edit(
        timed_out_until=None
    )

    embed = discord.Embed(
        description=(
            f"✅ Removed timeout from "
            f"{member.mention} ({member})"
        ),
        color=discord.Color(int("F594D7", 16))
    )

    await ctx.send(embed=embed)

@bot.command(name="purge")
@commands.has_permissions(
    manage_messages=True
)
async def purge(
    ctx,
    amount: int
):

    await ctx.channel.purge(
        limit=amount + 1
    )

    embed = discord.Embed(
        description=(
            f"🧹 Deleted "
            f"{amount} messages."
        ),
        color=discord.Color(
            int("F594D7", 16)
        )
    )

    msg = await ctx.send(embed=embed)

    await msg.delete(delay=3)

@bot.command(name="add_role")
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, member: discord.Member, *, role: discord.Role):

    await member.add_roles(role)

    embed = discord.Embed(
        description=(
            f"✅ Gave {role.mention} to "
            f"{member.mention} ({member})"
        ),
        color=discord.Color(int("F594D7", 16))
    )

    await ctx.send(embed=embed)

@bot.command(name="remove_role")
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, member: discord.Member, *, role: discord.Role):

    await member.remove_roles(role)

    embed = discord.Embed(
        description=(
            f"✅ Removed {role.mention} from "
            f"{member.mention} ({member})"
        ),
        color=discord.Color(int("FF4F7B", 16))
    )

    await ctx.send(embed=embed)

@bot.event
async def on_message_delete(message):

    if message.author.bot:
        return

    channel = bot.get_channel(MSG_LOG_CHANNEL_ID)

    if channel is None:
        return

    content = message.content

    if not content:
        content = "*No text content (possibly an embed, attachment, or image)*"

    embed = discord.Embed(
        title="🗑️ Message Deleted",
        color=discord.Color(int("F594D7", 16))
    )

    embed.add_field(
        name="Author",
        value=f"{message.author.mention} ({message.author})",
        inline=False
    )

    embed.add_field(
        name="Channel",
        value=message.channel.mention,
        inline=False
    )

    embed.add_field(
        name="Content",
        value=content[:1024],
        inline=False
    )

    embed.set_thumbnail(
        url=message.author.display_avatar.url
    )

    await channel.send(embed=embed)

TOKEN = os.getenv("TOKEN")

bot.run(TOKEN)
