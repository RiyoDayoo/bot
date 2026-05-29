import os
import discord
from discord.ext import commands
from datetime import timedelta

warns = {}

afk_users = {}

user_messages = {}
user_levels = {}

WELCOME_CHANNEL_ID = 1494196869834870916

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents)

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

    channel = bot.get_channel(WELCOME_CHANNEL_ID)

    if channel is not None:

        embed = discord.Embed(
            title="Welcome!",
            description=(
                f"🎀 Welcome to the server, "
                f"{member.mention}!\n\n"
                f"Please read the <#1500746326651047946> and enjoy your stay~!"
            ),
            color=discord.Color(int("F594D7", 16))
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        embed.set_footer(
            text=f"Member #{member.guild.member_count}"
        )

        await channel.send(embed=embed)

@bot.command(name="afk")
async def afk(ctx, *, reason="AFK"):

    afk_users[ctx.author.id] = reason

    embed = discord.Embed(
        description=(
            f"💤 {ctx.author.mention} is now AFK.\n"
            f"Reason: {reason}"
        ),
        color=discord.Color(int("F594D7", 16))
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

    if user_messages[user_id] >= 100:

        user_messages[user_id] = 0
        user_levels[user_id] += 1

        level = user_levels[user_id]

        embed = discord.Embed(
            description=(
                f"🎉 {message.author.mention} "
                f"leveled up!\n"
                f"New Level: {level}"
            ),
            color=discord.Color(int("F594D7", 16))
        )

        await message.channel.send(embed=embed)

    if message.author.id in afk_users:

        del afk_users[message.author.id]

        embed = discord.Embed(
            description=(
                f"✅ Welcome back {message.author.mention}, "
                f"your AFK status was removed."
            ),
            color=discord.Color(int("F594D7", 16))
        )

        await message.channel.send(embed=embed)

    for user in message.mentions:

        if user.id in afk_users:

            reason = afk_users[user.id]

            embed = discord.Embed(
                description=(
                    f"💤 {user.mention} is AFK.\n"
                    f"Reason: {reason}"
                ),
                color=discord.Color(int("F594D7", 16))
            )

            await message.channel.send(embed=embed)

    await bot.process_commands(message)

@bot.command(name="level")
async def level(ctx, member: discord.Member = None):

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
            f"💬 Messages: {current_msgs}/100"
        ),
        color=discord.Color(int("F594D7", 16))
    )

    await ctx.send(embed=embed)

@bot.command(name="purge")
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):

    await ctx.channel.purge(limit=amount + 1)

    embed = discord.Embed(
        description=(
            f"🧹 Deleted {amount} messages."
        ),
        color=discord.Color(int("F594D7", 16))
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

@bot.command(name="nick")
@commands.has_permissions(manage_nicknames=True)
async def nickname(
    ctx,
    member: discord.Member,
    *,
    new_nick
):

    old_nick = member.display_name

    if new_nick.lower() == "reset":

        await member.edit(nick=None)

        embed = discord.Embed(
            description=(
                f"✅ Reset nickname for "
                f"{member.mention}\n"
                f"Old Nickname: {old_nick}"
            ),
            color=discord.Color(int("F594D7", 16))
        )

        await ctx.send(embed=embed)
        return

    await member.edit(nick=new_nick)

    embed = discord.Embed(
        description=(
            f"✅ Changed nickname for "
            f"{member.mention}\n"
            f"Old Nickname: {old_nick}\n"
            f"New Nickname: {new_nick}"
        ),
        color=discord.Color(int("F594D7", 16))
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
        color=discord.Color(int("FF4F7B", 16))
    )

    try:
        await member.send(embed=dm_embed)
    except:
        pass

    await member.ban(reason=reason)

    embed = discord.Embed(
        description=(
            f"🔨 Banned {member.mention} ({member})\n"
            f"Reason: {reason}"
        ),
        color=discord.Color(int("FF4F7B", 16))
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

            embed = discord.Embed(
                description=(
                    f"✅ Unbanned {user}"
                ),
                color=discord.Color(int("F594D7", 16))
            )

            await ctx.send(embed=embed)
            return

    error_embed = discord.Embed(
        description=(
            "❌ User not found in ban list."
        ),
        color=discord.Color(int("FF4F7B", 16))
    )

    await ctx.send(embed=error_embed)

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

        dm_embed = discord.Embed(
            title="You were timed out",
            description=(
                f"Server: {ctx.guild.name}\n"
                f"Duration: {duration}\n"
                f"Reason: {reason}"
            ),
            color=discord.Color(int("F594D7", 16))
        )

        try:
            await member.send(embed=dm_embed)
        except:
            pass

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

@bot.command(name="warn")
@commands.has_permissions(moderate_members=True)
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

    warn_count = len(warns[user_id])

    dm_embed = discord.Embed(
        title="You were warned",
        description=(
            f"Server: {ctx.guild.name}\n"
            f"Reason: {reason}"
        ),
        color=discord.Color(int("F594D7", 16))
    )

    try:
        await member.send(embed=dm_embed)
    except:
        pass

    embed = discord.Embed(
        description=(
            f"⚠️ Warned {member.mention} ({member})\n"
            f"Warns: {warn_count}\n"
            f"Reason: {reason}"
        ),
        color=discord.Color(int("F594D7", 16))
    )

    await ctx.send(embed=embed)

@bot.command(name="warns")
async def show_warns(ctx, member: discord.Member):

    user_id = str(member.id)

    if user_id not in warns or len(warns[user_id]) == 0:

        embed = discord.Embed(
            description=(
                f"✅ {member.mention} has no warns."
            ),
            color=discord.Color(int("F594D7", 16))
        )

        await ctx.send(embed=embed)
        return

    warn_list = ""

    for i, reason in enumerate(warns[user_id], start=1):
        warn_list += f"{i}. {reason}\n"

    embed = discord.Embed(
        title=f"Warns for {member}",
        description=warn_list,
        color=discord.Color(int("F594D7", 16))
    )

    await ctx.send(embed=embed)

TOKEN = os.getenv("TOKEN")

bot.run(TOKEN)
