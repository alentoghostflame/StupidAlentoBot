from OLD.storage_module.server_data import DiskServerData
from datetime import datetime, timedelta
import OLD.universal_module.utils
import OLD.universal_module.text
from discord.ext import commands
from OLD.admin_module import text, utils
import logging
import discord
import typing
import sys

logger = logging.getLogger("Main")
sys.excepthook = OLD.universal_module.utils.log_exception_handler


async def mute(server_data: DiskServerData, context: commands.Context, user_mention=None, reason=text.MUTE_DEFAULT_REASON, *args):
    member: discord.Member = OLD.universal_module.utils.get_user_from_mention(context.guild, user_mention)
    mute_role = context.guild.get_role(server_data.mute_role_id)

    if not OLD.universal_module.utils.has_any_role(context.guild, server_data.muter_roles, context.author) and not \
            context.author.guild_permissions.administrator:
        await context.send(text.MUTE_MISSING_ROLE)
        logger.debug("User {} lacked role required to mute.".format(context.author.display_name))
    elif user_mention is None:
        await context.send(text.MUTE_HELP)
    elif member is None:
        await context.send(OLD.universal_module.text.INVALID_MEMBER_ID)
        logger.debug("User {} didn't specify a valid user.".format(context.author.display_name))
    elif OLD.universal_module.utils.has_any_role(context.guild, server_data.muter_roles, member) or member.guild_permissions.administrator:
        await context.send(text.MUTE_CANT_MUTE_MUTERS)
        logger.debug("User {} tried to mute a muter.".format(context.author.display_name))
    elif args:
        await context.send(OLD.universal_module.text.TOO_MANY_ARGUMENTS)
        logger.debug("User {} specified too many arguments.".format(context.author.display_name))
    elif not mute_role:
        await context.send(text.MUTE_ROLE_MISSING)
        logger.debug("User {} warned with non-existent warn role.".format(context.author.display_name))
    else:
        utils.remove_id_from_set(server_data.muted_users, member.id)
        await member.add_roles(mute_role, reason=text.WARN_DOUBLE_REASON.format(member.display_name, reason))
        server_data.muted_users.add((member.id, datetime.utcnow() + timedelta(minutes=20)))
        await context.send(text.MUTE_GIVEN)
        logger.debug("User {} muted user {}".format(context.author.display_name, member.display_name))


async def mute_admin(server_data: DiskServerData, context, arg1=None, arg2=None, *args):
    if not arg1:
        await context.send(text.MUTE_ADMIN_HELP)
        logger.debug("User {} didn't specify any arguments".format(context.author.display_name))
    elif args:
        await context.send(OLD.universal_module.text.TOO_MANY_ARGUMENTS)
    elif arg1 == "add_muter_role":
        await add_muter_role(server_data.muter_roles, context, arg2)
    elif arg1 == "remove_muter_role":
        await remove_muter_role(server_data.muter_roles, context, arg2)
    elif arg1 == "list_muter_roles":
        await list_muter_roles(server_data.muter_roles, context)
    elif arg1 == "set_mute_role":
        await set_mute_role(server_data, context, arg2)
    elif arg1 == "unset_mute_role":
        await unset_mute_role(server_data, context)
    else:
        await context.send(OLD.universal_module.text.INVALID_FIRST_ARGUMENT)


async def add_muter_role(muter_roles: typing.Set[int], context: commands.Context, role_mention=None):
    role = OLD.universal_module.utils.get_role_from_mention(context.guild, role_mention)
    if not role_mention:
        await context.send(text.MUTE_ADMIN_ADD_ROLE_HELP)
        logger.debug("User {} didn't specify any arguments.".format(context.author.display_name))
    elif not role:
        await context.send(OLD.universal_module.text.INVALID_ROLE_ID)
        logger.debug("User {} specified an invalid role.".format(context.author.display_name))
    else:
        muter_roles.add(role.id)
        await context.send(text.MUTE_ADMIN_ADD_ROLE_SUCCESS)
        logger.debug("User {} added role {}: {}.".format(context.author.display_name, role.id, role.name))


async def remove_muter_role(muter_roles: typing.Set[int], context: commands.Context, role_mention=None):
    role_id = OLD.universal_module.utils.get_numbers(role_mention)
    if not role_mention:
        await context.send(text.MUTE_ADMIN_REMOVE_ROLE_HELP)
        logger.debug("User {} didn't specify any arguments.".format(context.author.display_name))
    elif not role_id:
        await context.send(OLD.universal_module.text.INVALID_ROLE_ID)
        logger.debug("User {} specified an invalid role.".format(context.author.display_name))
    elif role_id not in muter_roles:
        await context.send(text.MUTE_ADMIN_REMOVE_ROLE_MISSING)
        logger.debug("User {} tried to remove an non-existent ID from the muters set.".format(context.author.
                                                                                              display_name))
    else:
        muter_roles.remove(role_id)
        await context.send(text.MUTE_ADMIN_REMOVE_ROLE_SUCCESS)


async def list_muter_roles(muter_roles: typing.Set[int], context: commands.Context):
    output_message = "Roles capable of muting:"
    for role_id in muter_roles:
        role = context.guild.get_role(role_id)
        if role:
            output_message += "\n{} : {}".format(role_id, role.name)
        else:
            output_message += "\n{} : N/A".format(role_id)
    await context.send(output_message)


async def set_mute_role(server_data: DiskServerData, context: commands.Context, role_mention=None):
    role = OLD.universal_module.utils.get_role_from_mention(context.guild, role_mention)
    if not role_mention:
        await context.send(text.MUTE_ADMIN_SET_ROLE_HELP)
        logger.debug("User {} didn't specify any arguments.".format(context.author.display_name))
    elif not role:
        await context.send(OLD.universal_module.text.INVALID_ROLE_ID)
        logger.debug("User {} specified an invalid role.".format(context.author.display_name))
    else:
        server_data.warn_role_id = role.id
        await context.send(text.MUTE_ADMIN_SET_ROLE_SUCCESS)
        logger.debug("User {} set role {}: {}.".format(context.author.display_name, role.id, role.name))


async def unset_mute_role(server_data: DiskServerData, context: commands.Context):
    server_data.mute_role_id = 0
    await context.send(text.MUTE_ADMIN_UNSET_ROLE_SUCCESS)
    logger.debug("User {} unset the role to mute people with.".format(context.author.display_name))
