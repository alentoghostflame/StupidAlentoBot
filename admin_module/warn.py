from storage_module.server_data import DiskServerData
from datetime import datetime, timedelta
from universal_module import utils
import universal_module.text
from discord.ext import commands
from admin_module import text
import universal_module
import logging
import sys


logger = logging.getLogger("Main")
sys.excepthook = utils.log_exception_handler


async def warn(warner_roles: set, warn_role_id: int, warned_users: set, mute_role_id: int, muted_users: set,
               context: commands.Context, user_mention=None, reason=text.WARN_DEFAULT_REASON, *args):
    member = utils.get_user_from_mention(context.guild, user_mention)
    warn_role = context.guild.get_role(warn_role_id)
    mute_role = context.guild.get_role(mute_role_id)

    if not utils.has_any_role(context.guild, warner_roles, context.author) and not \
            context.author.guild_permissions.administrator:
        await context.send(text.WARN_MISSING_ROLE)
        logger.debug("User {} lacked role required to warn.".format(context.author.display_name))
    elif member is None:
        await context.send(universal_module.text.INVALID_MEMBER_ID)
        logger.debug("User {} didn't specify a valid user.".format(context.author.display_name))
    elif utils.has_any_role(context.guild, warner_roles, member) or member.guild_permissions.administrator:
        await context.send(text.WARN_CANT_WARN_WARNERS)
        logger.debug("User {} tried to warn a warner.".format(context.author.display_name))
    elif args:
        await context.send(universal_module.text.TOO_MANY_ARGUMENTS)
        logger.debug("User {} specified too many arguments.".format(context.author.display_name))
    elif not warn_role:
        await context.send(text.WARN_MUTE_MISSING)
        logger.debug("User {} warned with non-existent warn role.".format(context.author.display_name))
    elif user_mention is None:
        await context.send(text.WARN_HELP)
        logger.debug("User {} didn't specify any arguments.".format(context.author.display_name))
    elif warn_role in member.roles:
        if mute_role:
            await member.add_roles(mute_role, reason=text.WARN_DOUBLE_REASON.format(member.display_name, reason))
            muted_users.add((member.id, datetime.utcnow() + timedelta(minutes=30)))
            await context.send(text.WARN_DOUBLE)
            logger.debug("User {} double warned user {}".format(context.author.display_name, member.display_name))
        else:
            await context.send(text.WARN_MUTE_MISSING)
            logger.debug("User {} tried to double warn user {}".format(context.author.display_name,
                                                                       member.display_name))

    else:
        await member.add_roles(warn_role, reason=text.WARN_REASON.format(member.display_name, reason))
        warned_users.add((member.id, datetime.utcnow() + timedelta(minutes=30)))
        await context.send(text.WARN_GIVEN)
        logger.debug("User {} warned user {}".format(context.author.display_name, member.display_name))


async def warn_admin(server_data: DiskServerData, context, arg1=None, arg2=None, *args):
    if not arg1:
        await context.send("You need to specify at least one argument, such as `add_warner_role`, `remove_warner_role`"
                           ", `set_warn_role`, and `unset_warn_role`")
        logger.debug("User {} didn't specify any arguments".format(context.author.display_name))
    elif args:
        await context.send(universal_module.text.TOO_MANY_ARGUMENTS)
    elif arg1 == "add_warner_role":
        await add_warner_role(server_data.warner_roles, context, arg2)
    elif arg1 == "remove_warner_role":
        await remove_warner_role(server_data.warner_roles, context, arg2)
    elif arg1 == "set_warn_role":
        await set_warn_role(server_data, context, arg2)
    elif arg1 == "unset_warn_role":
        await unset_warn_role(server_data, context, arg2)
    else:
        await context.send("Invalid first argument.")


async def add_warner_role(warner_roles: set, context: commands.Context, role_mention=None):
    role = context.guild.get_role(int(utils.get_numbers_legacy(role_mention)[0]))
    if not role_mention:
        await context.send("Adds a role to the list of roles allowed to warn people. @mention the role after the "
                           "command to add it, like `;warn_admin add_warner_role @role`")
        logger.debug("User {} didn't specify any arguments.".format(context.author.display_name))
    if not role:
        await context.send("Invalid role specified.")
        logger.debug("User {} specified an invalid role.".format(context.author.display_name))
    else:
        warner_roles.add(role.id)
        await context.send("Role added.")
        logger.debug("User {} added role {}: {}.".format(context.author.display_name, role.id, role.name))


async def remove_warner_role(warner_roles: set, context: commands.Context, role_mention=None):
    role = context.guild.get_role(int(utils.get_numbers_legacy(role_mention)[0]))
    if not role_mention:
        await context.send("Removes a role from the list of roles allowed to warn people. @mention the role after the "
                           "command to remove it, like `;warn_admin add_warner_role @role`")
        logger.debug("User {} didn't specify any arguments.".format(context.author.display_name))
    if not role:
        await context.send("Invalid role specified.")
        logger.debug("User {} specified an invalid role.".format(context.author.display_name))
    else:
        warner_roles.remove(role.id)
        await context.send("Role removed.")
        logger.debug("User {} removed role {}: {}.".format(context.author.display_name, role.id, role.name))


async def set_warn_role(server_data: DiskServerData, context: commands.Context, role_mention=None):
    role = context.guild.get_role(int(utils.get_numbers_legacy(role_mention)[0]))
    if not role_mention:
        await context.send("Sets the role to warn users with. @mention the role after the command to set it, like "
                           "`;warn_admin set_warn_role @role`")
        logger.debug("User {} didn't specify any arguments.".format(context.author.display_name))
    if not role:
        await context.send("Invalid role specified.")
        logger.debug("User {} specified an invalid role.".format(context.author.display_name))
        print(utils.get_numbers_legacy(role_mention))
    else:
        server_data.warn_role_id = role.id
        await context.send("Role set.")
        logger.debug("User {} set role {}: {}.".format(context.author.display_name, role.id, role.name))


async def unset_warn_role(server_data: DiskServerData, context: commands.Context, arg2=None):
    if arg2:
        await context.send("...you don't need to specify a second argument.")
        logger.debug("User {} didn't specify any arguments.".format(context.author.display_name))
    else:
        server_data.warn_role_id = 0
        await context.send("Role unset.")
        logger.debug("User {} unset the role.".format(context.author.display_name))
