from misc2_module.callouts.callout_data import CalloutGuildConfig
from misc2_module.callouts import text
from discord.ext import commands
from datetime import datetime, timedelta
import discord
import random


async def callout_fistbump(message: discord.Message):
    if "🤛" in message.content:
        messages = await message.channel.history(limit=2).flatten()
        if len(messages) >= 2 and "🤜" in messages[1].content:
            await message.channel.send(text.CALLOUT_FISTBUMP_MESSAGE.format(messages[1].author.display_name,
                                                                            messages[0].author.display_name))


async def enable(callout_config: CalloutGuildConfig, context: commands.Context):
    if callout_config.fistbumps:
        await context.send(text.CALLOUT_FISTBUMP_ALREADY_ENABLED)
    else:
        callout_config.fistbumps = True
        await context.send(text.CALLOUT_FISTBUMP_ENABLED)


async def disable(callout_config: CalloutGuildConfig, context: commands.Context):
    if callout_config.fistbumps:
        callout_config.fistbumps = False
        await context.send(text.CALLOUT_FISTBUMP_DISABLED)
    else:
        await context.send(text.CALLOUT_FISTBUMP_ALREADY_ENABLED)

