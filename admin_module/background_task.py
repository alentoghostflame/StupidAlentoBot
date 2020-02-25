from storage_module.stupid_storage import DiskStorage
from discord.ext import commands
from datetime import datetime
# from admin_module import text
import stupid_utils
import logging
import typing
import discord
import sys


logger = logging.getLogger("Main")
sys.excepthook = stupid_utils.log_exception_handler


async def background_task(bot: commands.Bot, disk_storage: DiskStorage):
    guild_ids = disk_storage.get_guild_ids()
    for guild_id in guild_ids:
        guild_data = disk_storage.get_server(guild_id)
        guild = bot.get_guild(guild_id)
        warn_role = guild.get_role(guild_data.warn_role_id)
        mute_role = guild.get_role(guild_data.mute_role_id)

        if warn_role:
            await if_time_remove_role(guild_data.warned_users, guild, warn_role)
        if mute_role:
            await if_time_remove_role(guild_data.muted_users, guild, mute_role)


async def if_time_remove_role(member_set: typing.Set[typing.Tuple[int, datetime]], guild: discord.Guild,
                              role: discord.Role):
    looping_set = member_set.copy()
    for member_datetime in looping_set:
        member = guild.get_member(member_datetime[0])
        if member:
            if member_datetime[1] <= datetime.utcnow():
                await member.remove_roles(role, reason="Time expired.")
                member_set.remove(member_datetime)
                logger.debug("Removed user {} from set.".format(member.display_name))
        else:
            member_set.remove(member_datetime)
            logger.debug("Removed invalid user from set.")
