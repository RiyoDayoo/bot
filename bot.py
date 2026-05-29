import os
import json
import discord
from discord.ext import commands
from datetime import timedelta

def load_data(filename):

    try:
        with open(filename, "r") as f:
            return json.load(f)

    except:
        return {}

def save_data(filename, data):

    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

warns = load_data("warns.json")

afk_users = {}

user_messages = load_data("messages.json")

user_levels = load_data("levels.json")

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
                f"🎀 Welcome {member.mention}!\n"
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

    if user_id not in user_messages:

        user_messages[user_id] = 0
        user_levels[user_id] = 0

    user_messages[user_id] += 1

    save_data(
        "messages.json",
        user_messages
    )

    if user_messages[user_id] >= 100:

        user_messages[user_id] = 0

        user_levels[user_id] += 1

        save_data(
            "levels.json",
            user_levels
        )

        level = user_levels[user_id]

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

    if user_id not in user_levels:

        user_levels[user_id] = 0
        user_messages[user_id] = 0

    level_num = user_levels[user_id]

    current_msgs = user_messages[user_id]

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

    if user_id not in warns:
        warns[user_id] = []

    warns[user_id].append(reason)

    save_data(
        "warns.json",
        warns
    )

    warn_count = len(warns[user_id])

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

    if user_id not in warns:

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

    for i, reason in enumerate(
        warns[user_id],
        start=1
    ):

        warn_text += (
            f"{i}. {reason}\n"
        )

    embed = discord.Embed(
        title=f"Warns for {member}",
        description=warn_text,
        color=discord.Color(
            int("F594D7", 16)
        )
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

TOKEN = os.getenv("TOKEN")

bot.run(TOKEN)
