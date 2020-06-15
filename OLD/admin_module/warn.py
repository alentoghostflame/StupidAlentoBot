from OLD.storage_module.server_data import DiskServerData
from datetime import datetime, timedelta
import OLD.universal_module.utils
import OLD.universal_module.text
from discord.ext import commands
from OLD.admin_module import text, utils
import logging
import discord
import sys


logger = logging.getLogger("Main")
sys.excepthook = OLD.universal_module.utils.log_exception_handler


async def warn(server_data: DiskServerData, context, user_mention=None, reason=text.WARN_DEFAULT_REASON, *args):
    member: discord.Member = OLD.universal_module.utils.get_user_from_mention(context.guild, user_mention)
    warn_role = context.guild.get_role(server_data.warn_role_id)
    mute_role = context.guild.get_role(server_data.mute_role_id)

    if not OLD.universal_module.utils.has_any_role(context.guild, server_data.warner_roles, context.author) and not \
            context.author.guild_permissions.administrator:
        await context.send(text.WARN_MISSING_ROLE)
        logger.debug("User {} lacked role required to warn.".format(context.author.display_name))
    elif user_mention is None:
        await context.send(text.WARN_HELP)
        logger.debug("User {} didn't specify any arguments.".format(context.author.display_name))
    elif member is None:
        await context.send(OLD.universal_module.text.INVALID_MEMBER_ID)
        logger.debug("User {} didn't specify a valid user.".format(context.author.display_name))
    elif OLD.universal_module.utils.has_any_role(context.guild, server_data.warner_roles, member) or \
            member.guild_permissions.administrator:
        await context.send(text.WARN_CANT_WARN_WARNERS)
        logger.debug("User {} tried to warn a warner.".format(context.author.display_name))
    elif args:
        await context.send(OLD.universal_module.text.TOO_MANY_ARGUMENTS)
        logger.debug("User {} specified too many arguments.".format(context.author.display_name))
    elif not warn_role:
        await context.send(text.WARN_ROLE_MISSING)
        logger.debug("User {} warned with non-existent warn role.".format(context.author.display_name))
    elif warn_role in member.roles:
        if mute_role:
            utils.remove_id_from_set(server_data.warned_users, member.id)
            utils.remove_id_from_set(server_data.muted_users, member.id)
            server_data.warned_users.add((member.id, datetime.utcnow() + timedelta(days=3)))
            await member.add_roles(mute_role, reason=text.WARN_DOUBLE_REASON.format(member.display_name, reason))
            server_data.muted_users.add((member.id, datetime.utcnow() + timedelta(minutes=20)))
            await context.send(text.WARN_DOUBLE)
            logger.debug("User {} double warned user {}".format(context.author.display_name, member.display_name))
        else:
            await context.send(text.WARN_MUTE_MISSING)
            logger.debug("User {} tried to double warn user {} without mute role.".format(context.author.display_name,
                                                                                          member.display_name))
    else:
        await member.add_roles(warn_role, reason=text.WARN_REASON.format(member.display_name, reason))
        server_data.warned_users.add((member.id, datetime.utcnow() + timedelta(days=30)))
        await context.send(text.WARN_GIVEN)
        logger.debug("User {} warned user {}".format(context.author.display_name, member.display_name))


async def warn_admin(server_data: DiskServerData, context, arg1=None, arg2=None, *args):
    if not arg1:
        await context.send(text.WARN_ADMIN_HELP)
        logger.debug("User {} didn't specify any arguments".format(context.author.display_name))
    elif args:
        await context.send(OLD.universal_module.text.TOO_MANY_ARGUMENTS)
    elif arg1 == "add_warner_role":
        await add_warner_role(server_data.warner_roles, context, arg2)
    elif arg1 == "remove_warner_role":
        await remove_warner_role(server_data.warner_roles, context, arg2)
    elif arg1 == "set_warn_role":
        await set_warn_role(server_data, context, arg2)
    elif arg1 == "unset_warn_role":
        await unset_warn_role(server_data, context)
    else:
        await context.send(OLD.universal_module.text.INVALID_FIRST_ARGUMENT)


async def add_warner_role(warner_roles: set, context: commands.Context, role_mention=None):
    role = context.guild.get_role(int(OLD.universal_module.utils.get_numbers_legacy(role_mention)[0]))
    if not role_mention:
        await context.send(text.WARN_ADMIN_ADD_ROLE_HELP)
        logger.debug("User {} didn't specify any arguments.".format(context.author.display_name))
    elif not role:
        await context.send(OLD.universal_module.text.INVALID_ROLE_ID)
        logger.debug("User {} specified an invalid role.".format(context.author.display_name))
    else:
        warner_roles.add(role.id)
        await context.send(text.WARN_ADMIN_ADD_ROLE_SUCCESS)
        logger.debug("User {} added role {}: {}.".format(context.author.display_name, role.id, role.name))


async def remove_warner_role(warner_roles: set, context: commands.Context, role_mention=None):
    role = context.guild.get_role(int(OLD.universal_module.utils.get_numbers_legacy(role_mention)[0]))
    if not role_mention:
        await context.send(text.WARN_ADMIN_REMOVE_ROLE_HELP)
        logger.debug("User {} didn't specify any arguments.".format(context.author.display_name))
    elif not role:
        await context.send(OLD.universal_module.text.INVALID_ROLE_ID)
        logger.debug("User {} specified an invalid role.".format(context.author.display_name))
    else:
        warner_roles.remove(role.id)
        await context.send(text.WARN_ADMIN_REMOVE_ROLE_SUCCESS)
        logger.debug("User {} removed role {}: {}.".format(context.author.display_name, role.id, role.name))


async def set_warn_role(server_data: DiskServerData, context: commands.Context, role_mention=None):
    role = context.guild.get_role(int(OLD.universal_module.utils.get_numbers_legacy(role_mention)[0]))
    if not role_mention:
        await context.send(text.WARN_ADMIN_SET_ROLE_HELP)
        logger.debug("User {} didn't specify any arguments.".format(context.author.display_name))
    elif not role:
        await context.send(OLD.universal_module.text.INVALID_ROLE_ID)
        logger.debug("User {} specified an invalid role.".format(context.author.display_name))
    else:
        server_data.warn_role_id = role.id
        await context.send(text.WARN_ADMIN_SET_ROLE_SUCCESS)
        logger.debug("User {} set role {}: {}.".format(context.author.display_name, role.id, role.name))


async def unset_warn_role(server_data: DiskServerData, context: commands.Context):
    server_data.warn_role_id = 0
    await context.send(text.WARN_ADMIN_UNSET_ROLE_SUCCESS)
    logger.debug("User {} unset the role to warn people with.".format(context.author.display_name))
