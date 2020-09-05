from misc2_module.callouts import text
from discord.ext import commands
import discord


async def send_help_embed(context: commands.Context):
    embed = discord.Embed(title="Authorization Manager", color=0x79d26b)

    embed.add_field(name="Description", value=text.CALLOUT_HELP_DESCRIPTION, inline=False)
    embed.add_field(name="Usage", value=text.CALLOUT_HELP_USAGE, inline=False)

    await context.send(embed=embed)
