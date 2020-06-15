from misc_module.storage import WelcomeConfig
from misc_module.welcomes.commands import text
from discord.ext import commands
import misc_module.text
import logging
import discord
import random
import typing
import re


logger = logging.getLogger("main_bot")


async def welcome_on_join(welcome_config: WelcomeConfig, member: discord.Member):
    channel: discord.TextChannel = member.guild.get_channel(welcome_config.welcome_channel_id)
    if channel and len(welcome_config.messages) > 0:
        await channel.send(random.sample(welcome_config.messages, 1)[0].format(member.display_name, member.mention))
