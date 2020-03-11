from storage_module.server_data import DiskServerData
from steam_announcement_module import text
from discord.ext import commands
import universal_module.utils
import universal_module.text
import logging


logger = logging.getLogger("Main")


async def steam_announcement_admin(server_data: DiskServerData, context: commands.Context, arg1=None, arg2=None, *args):
    if not arg1:
        await context.send(text.ADMIN_HELP)
    elif args:
        await context.send(universal_module.text.TOO_MANY_ARGUMENTS)
    elif arg1 == "set_channel":
        await set_channel(server_data, context, arg2)
    elif arg1 == "unset_channel":
        await unset_channel(server_data, context)
    elif arg1 == "list_games":
        await list_games(server_data, context)
    elif arg1 == "add_game":
        await add_game(server_data, context, arg2)
    elif arg1 == "remove_game":
        await remove_game(server_data, context, arg2)


async def set_channel(server_data: DiskServerData, context: commands.Context, arg=None):
    # channel = context.guild.get_channel(int(universal_module.utils.get_numbers_legacy(arg)[0]))
    channel = context.guild.get_channel(universal_module.utils.get_numbers(arg))
    if arg and not channel:
        await context.send(universal_module.text.INVALID_CHANNEL_ID)
    elif channel:
        server_data.steam_announcement_channel_id = channel.id
        await context.send(text.ADMIN_SET_CHANNEL_SUCCESS)
    elif not arg:
        server_data.steam_announcement_channel_id = context.channel.id
        await context.send(text.ADMIN_SET_CHANNEL_CURRENT)
    else:
        await context.send(universal_module.text.SHOULD_NOT_ENCOUNTER_THIS)


async def unset_channel(server_data: DiskServerData, context: commands.Context):
    server_data.steam_announcement_channel_id = 0
    await context.send(text.ADMIN_UNSET_SUCCESS)


async def list_games(server_data: DiskServerData, context: commands.Context):
    if server_data.steam_announcement_games:
        output = ""
        for game_id in server_data.steam_announcement_games:
            output += "`{}`, ".format(game_id)
        await context.send(text.ADMIN_LIST_GAMES.format(output)[:-2])
    else:
        await context.send(text.ADMIN_LIST_NO_GAMES)


async def add_game(server_data: DiskServerData, context: commands.Context, arg=None):
    steam_id = universal_module.utils.get_numbers(arg)
    if not arg:
        await context.send(text.ADMIN_ADD_GAME_HELP)
    elif not steam_id:
        await context.send(universal_module.text.INVALID_NUMBER)
    else:
        server_data.steam_announcement_games.add(steam_id)
        await context.send(text.ADMIN_ADD_GAME_ADDED.format(steam_id))


async def remove_game(server_data: DiskServerData, context: commands.Context, arg=None):
    steam_id = universal_module.utils.get_numbers(arg)
    if not arg:
        await context.send(text.ADMIN_REMOVE_GAME_HELP)
    elif not steam_id:
        await context.send(universal_module.text.INVALID_NUMBER)
    else:
        if steam_id not in server_data.steam_announcement_games:
            await context.send(text.ADMIN_REMOVE_GAME_NOT_IN_STORAGE.format(steam_id))
        else:
            server_data.steam_announcement_games.remove(steam_id)
            await context.send(text.ADMIN_REMOVE_GAME_SUCCESS.format(steam_id))
