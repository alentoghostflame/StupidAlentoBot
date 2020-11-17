from misc_module.storage import WelcomeConfig
import logging
import discord
import random


logger = logging.getLogger("main_bot")


async def welcome_on_join(welcome_config: WelcomeConfig, member: discord.Member):
    channel: discord.TextChannel = member.guild.get_channel(welcome_config.welcome_channel_id)
    if channel and len(welcome_config.messages) > 0:
        await channel.send(random.choice(welcome_config.messages).format(member.display_name, member.mention))
