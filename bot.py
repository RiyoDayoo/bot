import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# Give role command
@bot.command()
@commands.has_permissions(manage_roles=True)
async def giverole(ctx, member: discord.Member, *, role: discord.Role):
    await member.add_roles(role)
    await ctx.send(f"Gave {role} to {member.mention}")

# Remove role command
@bot.command()
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, member: discord.Member, *, role: discord.Role):
    await member.remove_roles(role)
    await ctx.send(f"Removed {role} from {member.mention}")

bot.run("MTUwODY1MTYyMjM3OTY4Mzg4Mg.G1LtzP.cLN5bSRw-Eg0b-LwdN3jPg-Ba8yyxFtN3uqMZg")