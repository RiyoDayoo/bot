import os
import discord
from discord.ext import commands
from datetime import timedelta

warns = {}

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

        embed = discord.Embed(
            description=(
                f"✅ Gave Follower role to "
                f"{member.mention} ({member})"
            ),
            color=discord.Color(int("F594D7", 16))
        )

        channel = member.guild.system_channel

        if channel is not None:
            await channel.send(embed=embed)

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
                f"({member}) until in {duration}.\n"
                f"|| Reason: {reason}"
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

    embed = discord.Embed(
        description=(
            f"⚠️ Warned {member.mention} ({member})\n"
            f"Warns: {warn_count}\n"
            f"Reason: {reason}"
        ),
        color=discord.Color(int("F594D7", 16))
    )

    await ctx.send(embed=embed)

@bot.command(name="showwarns")
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
