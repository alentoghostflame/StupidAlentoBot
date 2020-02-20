# from storage_module.stupid_storage import DiskStorage
from storage_module.storage_utils import DiskServerData
from discord.ext import commands
from faq_module import text
import stupid_utils
import logging
import discord
import typing
import sys
import re


logger = logging.getLogger("Main")
sys.excepthook = stupid_utils.log_exception_handler


async def faq_admin(server_data: DiskServerData, context, arg1=None, arg2=None, arg3=None, *args):
    if not arg1:
        await context.send(text.FAQ_ADMIN_HELP)
        logger.debug("User {} didn't specify arguments.".format(context.author.display_name))
    elif args:
        await context.send(text.TOO_MANY_ARGUMENTS)
        logger.debug("User {} specified too many arguments.".format(context.author.display_name))
    elif arg1 == "toggle":
        await toggle(server_data, context, arg2)
    elif arg1 == "add_keyword":
        await add_keyword(server_data.faq_phrases, context, arg2, arg3)
    elif arg1 == "remove_keyword":
        await remove_keyword(server_data.faq_phrases, context, arg2, arg3)
    elif arg1 == "list_keywords":
        await list_keywords(server_data.faq_phrases, context, arg2, arg3)
    elif arg1 == "add_edit_role":
        pass
    elif arg1 == "remove_edit_role":
        pass
    elif arg1 == "list_edit_roles":
        pass
    else:
        await context.send(text.INVALID_FIRST_ARGUMENT)


async def toggle(server_data: DiskServerData, context: commands.Context, arg: str):
    server_data.faq_enabled, message = stupid_utils.toggle_feature(arg, "faq", stupid_utils.ENABLE_PHRASES,
                                                                   stupid_utils.DISABLE_PHRASES,
                                                                   server_data.faq_enabled)
    await context.send(message)


async def add_keyword(faq_phrases: typing.Dict[str, str], context: commands.Context, keyword=None, statement=None):
    if not keyword:
        await context.send(text.ADD_KEYWORD_HELP)
        logger.debug("User {} didn't specify a keyword.".format(context.author.display_name))
    elif not statement:
        await context.send(text.ADD_KEYWORD_MISSING_STATEMENT)
        logger.debug("User {} didn't specify a statement".format(context.author.display_name))
    elif keyword in faq_phrases:
        faq_phrases[keyword] = statement
        await context.send(text.ADD_KEYWORD_OVERWROTE.format(keyword))
        logger.debug("User {} overwrote keyword {} with {}".format(context.author.display_name, keyword, statement))
    else:
        faq_phrases[keyword] = statement
        await context.send(text.ADD_KEYWORD_NEW.format(keyword))
        logger.debug("User {} created keyword {} with {}".format(context.author.display_name, keyword, statement))


async def remove_keyword(faq_phrases: typing.Dict[str, str], context: commands.Context, keyword=None, arg2=None):
    if not keyword:
        await context.send(text.REMOVE_KEYWORD_HELP)
        logger.debug("User {} didn't specify a keyword.".format(context.author.display_name))
    if arg2:
        await context.send(text.DONT_NEED_ADD_ARGS)
        logger.debug("User {} didn't specify a statement".format(context.author.display_name))
    else:
        flag = faq_phrases.pop(keyword, None)
        if flag:
            await context.send(text.REMOVE_KEYWORD_FOUND.format(keyword))
            logger.debug("User {} removed keyword {}".format(context.author.display_name, keyword))
        else:
            await context.send(text.REMOVE_KEYWORD_MISSING.format(keyword))
            logger.debug("User {} tried to remove keyword {}".format(context.author.display_name, keyword))


async def list_keywords(faq_phrases: typing.Dict[str, str], context: commands.Context, arg1=None, arg2=None):
    if arg1:
        await context.send(text.DONT_NEED_ADD_ARGS)
        logger.debug("User {} specified too many arguments.".format(context.author.display_name))
    else:
        await context.send("List of keywords: {}".format(list(faq_phrases)))
        logger.debug("User {} asked for list of keywords.".format(context.author.display_name))


async def add_edit_role(faq_edit_roles: typing.Set[int], context: commands.Context, arg1, arg2):
    role = context.guild.get_role(int(stupid_utils.get_numbers(arg1)[0]))
    if not arg1:
        pass
