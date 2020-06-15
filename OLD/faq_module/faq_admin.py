from OLD.storage_module.server_data import DiskServerData, FAQPhraseData
from OLD.faq_module.provide_faq import migrate_to_class
import OLD.universal_module.utils
import OLD.universal_module.text
from discord.ext import commands
from OLD.faq_module import text
import logging
import typing
import sys


logger = logging.getLogger("Main")
sys.excepthook = OLD.universal_module.utils.log_exception_handler


async def faq_admin(server_data: DiskServerData, context, arg1=None, arg2=None, arg3=None, image_url=None, *args):
    if not arg1:
        await context.send(text.FAQ_ADMIN_HELP)
        logger.debug("User {} didn't specify arguments.".format(context.author.display_name))
    elif args:
        await context.send(text.TOO_MANY_ARGUMENTS)
        logger.debug("User {} specified too many arguments.".format(context.author.display_name))
    elif arg1 == "toggle":
        await toggle(server_data, context, arg2)
    elif arg1 == "add_keyword":
        await add_keyword(server_data.faq_phrases, context, arg2, arg3, image_url=image_url)
    elif arg1 == "remove_keyword":
        await remove_keyword(server_data.faq_phrases, context, arg2, arg3)
    elif arg1 == "list_keywords":
        await list_keywords(server_data.faq_phrases, context, arg2)
    elif arg1 == "list_keywords_full":
        await list_keywords_full(server_data.faq_phrases, context)
    elif arg1 == "list_edit_roles":
        await list_edit_roles(server_data.faq_edit_roles, context)
    elif not context.author.guild_permissions.administrator:
        await context.send(text.LACK_ADMINISTRATOR)
    elif arg1 == "add_edit_role":
        await add_edit_role(server_data.faq_edit_roles, context, arg2)
    elif arg1 == "remove_edit_role":
        await remove_edit_role(server_data.faq_edit_roles, context, arg2)
    else:
        await context.send(text.INVALID_FIRST_ARGUMENT)


async def toggle(server_data: DiskServerData, context: commands.Context, arg: str):
    server_data.faq_enabled, message = OLD.universal_module.utils.toggle_feature(arg, "faq",
                                                                                 OLD.universal_module.utils.ENABLE_PHRASES,
                                                                                 OLD.universal_module.utils.DISABLE_PHRASES,
                                                                                 server_data.faq_enabled)
    await context.send(message)


async def add_keyword(faq_phrases: typing.Dict[str, FAQPhraseData], context: commands.Context, keyword=None, statement=None, image_url=None):
    phrase_data = FAQPhraseData(keyword, statement, image_url=image_url)
    if not keyword:
        await context.send(text.ADD_KEYWORD_HELP)
        logger.debug("User {} didn't specify a keyword.".format(context.author.display_name))
    elif not statement:
        await context.send(text.ADD_KEYWORD_MISSING_STATEMENT)
        logger.debug("User {} didn't specify a statement".format(context.author.display_name))
    # elif keyword in faq_phrases:
    #     # faq_phrases[keyword] = statement
    #     faq_phrases[keyword] = phrase_data
    #     await context.send(text.ADD_KEYWORD_OVERWROTE.format(keyword))
    #     logger.debug("User {} overwrote keyword {} with {}".format(context.author.display_name, keyword, statement))
    # else:
    #     faq_phrases[keyword] = statement
    #     await context.send(text.ADD_KEYWORD_NEW.format(keyword))
    #     logger.debug("User {} created keyword {} with {}".format(context.author.display_name, keyword, statement))
    else:
        overwrote_flag = False
        if keyword in faq_phrases:
            overwrote_flag = True

        faq_phrases[keyword] = phrase_data

        if overwrote_flag:
            await context.send(text.ADD_KEYWORD_OVERWROTE.format(keyword))
            logger.debug("User {} overwrote keyword {} with {}".format(context.author.display_name, keyword, statement))
        else:
            await context.send(text.ADD_KEYWORD_NEW.format(keyword))
            logger.debug("User {} created keyword {} with {}".format(context.author.display_name, keyword, statement))
        if phrase_data.image_url:
            await context.send(text.ADD_KEYWORD_IMAGE_ADDED.format(phrase_data.image_url))
            logger.debug("User {} created keyword {} with image URL {}".format(context.author.display_name, keyword,
                                                                               phrase_data.image_url))


async def remove_keyword(faq_phrases: typing.Dict[str, FAQPhraseData], context: commands.Context, keyword=None, arg2=None):
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


async def list_keywords(faq_phrases: typing.Dict[str, FAQPhraseData], context: commands.Context, arg1=None):
    if arg1:
        await context.send(text.DONT_NEED_ADD_ARGS)
        logger.debug("User {} specified too many arguments.".format(context.author.display_name))
    else:
        await context.send("List of keywords: {}".format(list(faq_phrases)))
        logger.debug("User {} asked for list of keywords.".format(context.author.display_name))


async def list_keywords_full(faq_phrases: typing.Dict[str, FAQPhraseData], context: commands.Context):
    output = ""
    for keyword in faq_phrases:
        if isinstance(faq_phrases[keyword], str):
            migrate_to_class(faq_phrases, keyword)
        output += "{} : {}\n".format(keyword, faq_phrases[keyword].statement.replace("```", "``" +
                                                                                     OLD.universal_module.text.
                                                                                     ZERO_WIDTH_SPACE +
                                                                                     "`"))
    await context.send("List of keywords and phrases: ```{}```".format(output))
    logger.debug("User {} asked for a list of keywords.".format(context.author.display_name))


async def add_edit_role(faq_edit_roles: typing.Set[int], context: commands.Context, arg1):
    role = context.guild.get_role(int(OLD.universal_module.utils.get_numbers_legacy(arg1)[0]))
    if not arg1:
        await context.send(text.ADD_EDIT_ROLE_HELP)
        logger.debug("User {} didn't specify a keyword.".format(context.author.display_name))
    if not role:
        await context.send(text.INVALID_ROLE)
        logger.debug("User {} didn't specify a valid role.".format(context.author.display_name))
    else:
        faq_edit_roles.add(role.id)
        await context.send(text.ROLE_ADDED)
        logger.debug("User {} added role {}: {}.".format(context.author.display_name, role.id, role.name))


async def remove_edit_role(faq_edit_roles: typing.Set[int], context: commands.Context, arg1):
    role_id = int(OLD.universal_module.utils.get_numbers_legacy(arg1)[0])
    if not arg1:
        await context.send(text.REMOVE_EDIT_ROLE_HELP)
        logger.debug("User {} didn't specify a keyword.".format(context.author.display_name))
    else:
        if role_id in faq_edit_roles:
            faq_edit_roles.remove(role_id)
            await context.send(text.ROLE_REMOVED)
            logger.debug("User {} removed role {}".format(context.author.display_name, role_id))
        else:
            await context.send(text.ROLE_NOT_FOUND)
            logger.debug("User {} tried to remove role {}".format(context.author.display_name, role_id))


async def list_edit_roles(faq_edit_roles: typing.Set[int], context: commands.Context):
    output = ""
    for role_id in faq_edit_roles:
        role = context.guild.get_role(role_id)
        if role:
            output += "`{}`: {}\n".format(role_id, role.name)
        else:
            output += "`{}`: N/A\n".format(role_id)
    await context.send("List of roles that can edit: \n{}".format(output))
    logger.debug("User {} asked for list of edit roles.".format(context.author.display_name))
