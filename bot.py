import os
import discord
from discord.ext import commands
from datetime import timedelta

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command(name="give_role")
@bot.command()
@commands.has_permissions(manage_roles=True)
async def giverole(ctx, member: discord.Member, *, role: discord.Role):

    await member.add_roles(role)

    await ctx.send(
        f"Gave {role} to {member.mention}"
    )

@bot.command(name="remove_role")
@bot.command()
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, member: discord.Member, *, role: discord.Role):

    await member.remove_roles(role)

    await ctx.send(
        f"Removed {role} from {member.mention}"
    )

@bot.command(name="to")
@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, duration: str):

    try:
        unit = duration[-1]
        amount = int(duration[:-1])

        if unit == "s":
            delta = timedelta(seconds=amount)

        elif unit == "m":
            delta = timedelta(minutes=amount)

        elif unit == "d":
            delta = timedelta(days=amount)

        else:
            await ctx.send(
                "Use s (seconds), m (minutes), or d (days)."
            )
            return

        await member.edit(
            timed_out_until=discord.utils.utcnow() + delta
        )

        await ctx.send(
            f"{member.mention} has been timed out for {duration}."
        )

    except:
        await ctx.send(
            "Invalid format. Example: !timeout @user 10m"
        )

@bot.command(name="um")
@bot.command()
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
