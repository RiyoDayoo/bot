import os
import discord
from discord.ext import commands
from datetime import timedelta

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
            color=discord.Color.green()
        )

        channel = member.guild.system_channel

        if channel is not None:
            await channel.send(embed=embed)

@bot.command(name="add_role")
@commands.has_permissions(manage_roles=True)
async def giverole(ctx, member: discord.Member, *, role: discord.Role):

    await member.add_roles(role)

    embed = discord.Embed(
        description=(
            f"✅ Added {role.mention} to "
            f"{member.mention} ({member})"
        ),
        color=discord.Color.green()
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
        color=discord.Color.red()
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
            color=discord.Color.pink()
        )

        await ctx.send(embed=embed)

    except:

        error_embed = discord.Embed(
            description=(
                "❌ Invalid format.\n"
                "Example: `.to @user 5h spamming`"
            ),
            color=discord.Color.red()
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
        color=discord.Color.green()
    )

    await ctx.send(embed=embed)

TOKEN = os.getenv("TOKEN")

bot.run(TOKEN)
