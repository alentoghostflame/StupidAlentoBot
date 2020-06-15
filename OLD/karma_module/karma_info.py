from OLD.storage_module.server_data import DiskServerData
from discord.ext import commands
from OLD.karma_module import text
import OLD.universal_module.utils
import logging
import typing


logger = logging.getLogger("Main")


async def list_karma(server_data: DiskServerData, context: commands.Context, arg1=None):
    mentions = OLD.universal_module.utils.find_mentions(context.guild, arg1)
    if arg1:
        await context.send(text.LIST_KARMA_OBJECT.format(arg1, server_data.member_karma.get(arg1, 0)))
    elif mentions:
        display_name = context.guild.get_member(mentions[0]).display_name
        await context.send(text.LIST_KARMA_MEMBER.format(display_name, server_data.member_karma.get(mentions[0], 0)))
    else:
        await context.send(text.LIST_KARMA_OWN.format(server_data.member_karma.get(context.author.id, 0)))


async def karma_top(server_data: DiskServerData, context: commands.Context):
    # noinspection PyTypeChecker
    sorted_tuples: typing.List[tuple] = sorted(server_data.member_karma.items(), reverse=True, key=lambda x: x[1])
    output = text.KARMA_TOP_START
    i = 0
    while i < len(sorted_tuples) and i < 10:
        if isinstance(sorted_tuples[i][0], int) and context.guild.get_member(sorted_tuples[i][0]):
            output += text.KARMA_TOP_FORMAT.format(i + 1, context.guild.get_member(sorted_tuples[i][0]).display_name,
                                                   sorted_tuples[i][1])
        else:
            output += text.KARMA_TOP_FORMAT.format(i + 1, sorted_tuples[i][0], sorted_tuples[i][1])
        i += 1
    await context.send(output)




