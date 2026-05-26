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

@bot.command(name="give_role")
@commands.has_permissions(manage_roles=True)
async def giverole(ctx, member: discord.Member, *, role: discord.Role):

    await member.add_roles(role)

    await ctx.send(
        f"Gave {role} to {member.mention}"
    )

@bot.command(name="remove_role")
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, member: discord.Member, *, role: discord.Role):

    await member.remove_roles(role)

    await ctx.send(
        f"Removed {role} from {member.mention}"
    )

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
                "Use s (seconds), m (minutes), h (hours), or d (days)."
            )
            return

        await member.edit(
            timed_out_until=discord.utils.utcnow() + delta,
            reason=reason
        )

        await ctx.send(
            f"{member.mention} has been timed out for {duration}.\n"
            f"Reason: {reason}"
        )

    except:
        await ctx.send(
            "Invalid format. Example: .to @user 5h spamming"
        )

@bot.command(name="um")
@commands.has_permissions(moderate_members=True)
async def untimeout(ctx, member: discord.Member):

    await member.edit(
        timed_out_until=None
    )

    await ctx.send(
        f"Removed timeout from {member.mention}"
    )

TOKEN = os.getenv("TOKEN")

bot.run(TOKEN)
