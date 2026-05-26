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

# TIMEOUT COMMAND
@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, minutes: int):

    duration = timedelta(minutes=minutes)

    await member.edit(
        timed_out_until=discord.utils.utcnow() + duration
    )

    await ctx.send(
        f"{member.mention} has been timed out for {minutes} minutes."
    )

# REMOVE TIMEOUT
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
