from OLD.storage_module.server_data import DiskServerData
from discord.ext import commands
import OLD.misc_module.text as text
import OLD.universal_module.utils
import OLD.universal_module.text
import logging
import discord
import random
import sys


logger = logging.getLogger("Main")
sys.excepthook = OLD.universal_module.utils.log_exception_handler


async def welcome(server_data: DiskServerData, member: discord.Member):
    channel = member.guild.get_channel(server_data.welcome_channel_id)
    if channel and len(server_data.welcome_messages) > 0:
        await channel.send(random.sample(server_data.welcome_messages, 1)[0].format(member.display_name))


async def welcome_admin(server_data: DiskServerData, context: commands.Context, arg1=None, arg2=None, *args):
    if not arg1:
        await context.send(text.WELCOME_ADMIN_HELP)

    elif args:
        await context.send(OLD.universal_module.text.TOO_MANY_ARGUMENTS)
    elif arg1 == "toggle":
        await toggle(server_data, context, arg2)
    elif arg1 == "add":
        await add(server_data, context, arg2)
    elif arg1 == "remove":
        await remove(server_data, context, arg2)
    elif arg1 == "list":
        await list_welcome(server_data, context)
    elif arg1 == "set_channel":
        await set_channel(server_data, context, arg2)
    elif arg1 == "unset_channel":
        await unset_channel(server_data, context)
    else:
        await context.send(OLD.universal_module.text.FIRST_ARGUMENT_INVALID)


async def toggle(server_data: DiskServerData, context: commands.Context, arg=None):
    if not context.guild.get_channel(server_data.welcome_channel_id):
        await context.send(text.WELCOME_TOGGLE_NO_CHANNEL)
    else:
        server_data.welcome_enabled, message = \
            OLD.universal_module.utils.toggle_feature(arg, "welcome", OLD.universal_module.utils.ENABLE_PHRASES,
                                                      OLD.universal_module.utils.DISABLE_PHRASES, server_data.welcome_enabled)
        await context.send(message)


async def add(server_data: DiskServerData, context: commands.Context, arg=None):
    if not arg:
        await context.send(text.WELCOME_ADD_HELP)
    else:
        server_data.welcome_messages.append(arg)
        await context.send(text.WELCOME_ADD_SUCCESS)


async def remove(server_data: DiskServerData, context: commands.Context, arg=None):
    if not arg:
        await context.send(text.WELCOME_REMOVE_HELP)
    else:
        try:
            index = int(arg)
            if -1 * len(server_data.welcome_messages) <= index < len(server_data.welcome_messages):
                server_data.welcome_messages.pop(index)
                await context.send(text.WELCOME_REMOVE_SUCCESS)
            else:
                await context.send(OLD.universal_module.text.INDEX_OUT_OF_BOUNDS)
        except ValueError:
            await context.send(OLD.universal_module.text.INVALID_NUMBER)


async def list_welcome(server_data: DiskServerData, context: commands.Context):
    message = ""
    for i in range(0, len(server_data.welcome_messages)):
        message += "{}: {}\n".format(i, server_data.welcome_messages[i])
    await context.send("List of welcome messages:\n{}".format(message))


async def set_channel(server_data: DiskServerData, context: commands.Context, channel_id=None):
    channel = context.guild.get_channel(channel_id)

    if not channel_id:
        server_data.welcome_channel_id = context.channel.id
        await context.send(text.WELCOME_SET_CHANNEL_CURRENT)
    elif channel:
        server_data.welcome_channel_id = channel.id
        await context.send(text.WELCOME_SET_CHANNEL_OTHER)
    else:
        await context.send(OLD.universal_module.text.INVALID_CHANNEL_ID)


async def unset_channel(server_data: DiskServerData, context: commands.Context):
    server_data.welcome_channel_id = 0
    await context.send(text.WELCOME_UNSET_SUCCESS)
