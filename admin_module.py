# from stupid_utils import DataSync, ENABLE_PHRASES, DISABLE_PHRASES, default_server_data
from discord.ext import tasks, commands
from datetime import datetime, timedelta
# from discord import utils
import stupid_utils
import logging
import discord
import typing
import random
import sys
import re


REMIND_DELETE_PHRASES: set = {"Hey, I thought I remembered {1} saying \"{0}\"",
                              "Hey {1}, didn't you say something like \"{0}\"?", "\"{0}\" - {1}."}


logger = logging.getLogger("Main")

sys.excepthook = stupid_utils.log_exception_handler


class AdminCog(commands.Cog, name="Admin Module"):
    def __init__(self, data_sync: stupid_utils.DataSync, bot_data: typing.Dict[str, dict]):
        super().__init__()
        self.data_sync = data_sync
        self.bot_data = bot_data

        self.enable_phrases: set = stupid_utils.ENABLE_PHRASES
        self.disable_phrases: set = stupid_utils.DISABLE_PHRASES

        self.remind_delete_phrases: set = REMIND_DELETE_PHRASES

    def cog_unload(self):
        self.warn_mute_loop.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        print("Admin-ish Module Ready.")
        self.warn_mute_loop.start()

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        await self.callout_delete(message)
    """

    Warning Related

    """
    @commands.command(name="warn", usage="@user", brief="Warn the user.")
    async def warn(self, context, arg=None, *reason):
        server = context.guild.id
        if server not in self.bot_data:
            self.bot_data[server] = stupid_utils.default_server_data()

        member = stupid_utils.get_user_from_mention(context.guild, arg)
        warn_role = context.guild.get_role(int(self.bot_data[server]["warn_role"]))

        if not role_check(context.author.roles, self.bot_data[server]["warn_roles"]):
            await context.send("You lack the role required to warn.")
        elif not warn_role:
            await context.send("You need to assign a valid warn role via `;set_warn_role @role` first.")
        elif not member:
            await context.send("That doesn't appear to be a user on your server.")
        elif role_check(member.roles, self.bot_data[server]["warn_roles"]):
            await context.send("You can't warn the warners.")
        elif role_check(member.roles, {warn_role.id}):
            mute_role = context.guild.get_role(int(self.bot_data[server]["warn_role"]))
            if not mute_role:
                await context.send("You need to assign a valid mute role via `;set_mute_role @role` before the "
                                   "double-warn -> mute can happen.")
            elif reason:
                await member.add_roles(mute_role, reason="{} did the 2nd warn for: \"{}\"".format(context.author.name,
                                                                                                  " ".join(reason)))
                await context.send("Due to double warn, muted for 30 minutes for: \"{}\"".format(" ".join(reason)))
                stupid_utils.rm_id_from_bot_data(self.bot_data, server, member.id, "muted_users")
                self.bot_data[server]["muted_users"].add((member.id, datetime.utcnow() + timedelta(minutes=30)))
            else:
                await member.add_roles(mute_role, reason="{} did the 2nd warn.".format(context.author.name))
                await context.send("Due to double warn, muted for 30 minutes.")
                stupid_utils.rm_id_from_bot_data(self.bot_data, server, member.id, "muted_users")
                self.bot_data[server]["muted_users"].add((member.id, datetime.utcnow() + timedelta(minutes=30)))
        else:
            if reason:
                await member.add_roles(warn_role, reason="{} warned because: \"{}\"".format(context.author.name,
                                                                                            " ".join(reason)))
                await context.send("Warned for 30 seconds for: \"{}\"".format(" ".join(reason)))
            else:
                await member.add_roles(warn_role, reason="{} warned them.".format(context.author.name))
                await context.send("Warned for 30 minutes.")
            stupid_utils.rm_id_from_bot_data(self.bot_data, server, member.id, "warned_users")
            self.bot_data[server]["warned_users"].add((member.id, datetime.utcnow() + timedelta(minutes=30)))

    @commands.has_permissions(administrator=True)
    @commands.command(name="set_warn_role", usage="@role", brief="Set the role to give warned users.")
    async def set_warn_role(self, context, arg=None):
        server = context.guild.id
        if server not in self.bot_data:
            self.bot_data[server] = stupid_utils.default_server_data()
        self.bot_data[server]["warn_role"], message = set_role_to(self.bot_data[server]["warn_role"], arg,
                                                                  "Set {} to the warned role.",
                                                                  "That role is already set.")
        await context.send(message)

    @commands.has_permissions(administrator=True)
    @commands.command(name="clear_warn_role", brief="Clears the role given to warned users.")
    async def clear_warn_role(self, context):
        server = context.guild.id
        if server not in self.bot_data:
            self.bot_data[server] = stupid_utils.default_server_data()
        if self.bot_data[server]["warn_role"] == 0:
            await context.send("No role was set?")
        else:
            self.bot_data[server]["warn_role"] = 0
            await context.send("Warned role cleared.")

    @commands.has_permissions(administrator=True)
    @commands.command(name="add_warn_role", usage="@role", brief="Allow a role to warn users.")
    async def add_warn_role(self, context, arg=None):
        server = context.guild.id
        if server not in self.bot_data:
            self.bot_data[server] = stupid_utils.default_server_data()
        message = add_role_to(self.bot_data[server]["warn_roles"], arg, "Added {} to roles that can warn.",
                              "That role can already warn.")
        await context.send(message)

    @commands.has_permissions(administrator=True)
    @commands.command(name="remove_warn_role", usage="@role", brief="Un-allow a role to warn users.")
    async def remove_warn_role(self, context, arg=None):
        server = context.guild.id
        if server not in self.bot_data:
            self.bot_data[server] = stupid_utils.default_server_data()
        message = remove_role_from(self.bot_data[server]["warn_roles"], arg, "Removed {} from roles that can warn.",
                                   "That role already can't warn.")
        await context.send(message)
    """
    
    Mute Related
    
    """
    @commands.command(name="mute", usage="@user", brief="Mute the user.")
    async def mute(self, context, arg=None, *reason):
        server = context.guild.id
        if server not in self.bot_data:
            self.bot_data[server] = stupid_utils.default_server_data()

        member = stupid_utils.get_user_from_mention(context.guild, arg)

        if not role_check(context.author.roles, self.bot_data[server]["mute_roles"]):
            await context.send("You lack the role required to mute.")
        elif self.bot_data[server]["mute_role"] == 0:
            await context.send("You need to assign a mute role via `;set_mute_role @role` first.")
        elif not member:
            await context.send("That doesn't appear to be a user on your server.")
        elif role_check(member.roles, self.bot_data[server]["mute_roles"]):
            await context.send("You can't mute the muters.")
        else:
            role = context.guild.get_role(int(self.bot_data[server]["mute_role"]))
            await member.add_roles(role, reason="{} muted because: \"{}\"".format(context.author.name,
                                                                                  " ".join(reason)))
            if reason:
                await member.add_roles(role, reason="{} muted because: \"{}\"".format(context.author.name,
                                                                                      " ".join(reason)))
                await context.send("Muted for 30 minutes for: \"{}\"".format(" ".join(reason)))
            else:
                await member.add_roles(role, reason="{} muted them.".format(context.author.name))
                await context.send("Muted for 30 minutes.")
            stupid_utils.rm_id_from_bot_data(self.bot_data, server, member.id, "muted_users")
            self.bot_data[server]["muted_users"].add((member.id, datetime.utcnow() + timedelta(minutes=30)))

    @commands.has_permissions(administrator=True)
    @commands.command(name="set_mute_role", usage="@role", brief="Set the role to give muted users.")
    async def set_mute_role(self, context, arg=None):
        server = context.guild.id
        if server not in self.bot_data:
            self.bot_data[server] = stupid_utils.default_server_data()
        self.bot_data[server]["mute_role"], message = set_role_to(self.bot_data[server]["mute_role"], arg,
                                                                  "Set {} to the muted role.",
                                                                  "That role is already set.")
        await context.send(message)

    @commands.has_permissions(administrator=True)
    @commands.command(name="clear_mute_role", brief="Clears the role given to muted users.")
    async def clear_mute_role(self, context):
        server = context.guild.id
        if server not in self.bot_data:
            self.bot_data[server] = stupid_utils.default_server_data()
        if self.bot_data[server]["mute_role"] == 0:
            await context.send("No role was set?")
        else:
            self.bot_data[server]["mute_role"] = 0
            await context.send("Muted role cleared.")

    @commands.has_permissions(administrator=True)
    @commands.command(name="add_mute_role", usage="@role", brief="Allow a role to mute users.")
    async def add_mute_role(self, context, arg=None):
        server = context.guild.id
        if server not in self.bot_data:
            self.bot_data[server] = stupid_utils.default_server_data()
        message = add_role_to(self.bot_data[server]["mute_roles"], arg, "Added {} to roles that can mute.",
                              "That role can already mute.")
        await context.send(message)

    @commands.has_permissions(administrator=True)
    @commands.command(name="remove_mute_role", usage="@role", brief="Un-allow a role to mute users.")
    async def remove_mute_role(self, context, arg=None):
        server = context.guild.id
        if server not in self.bot_data:
            self.bot_data[server] = stupid_utils.default_server_data()
        message = remove_role_from(self.bot_data[server]["mute_roles"], arg, "Removed {} from roles that can mute.",
                                   "That role already can't mute.")
        await context.send(message)
    """
    
    Warn/Mute Task Related.
    
    """

    # noinspection PyCallingNonCallable
    @tasks.loop(seconds=60.0)
    async def warn_mute_loop(self):
        for server in self.bot_data:
            server_obj = self.data_sync.bot.get_guild(server)

            if self.bot_data[server]["warn_role"] != 0:
                warn_role_obj = server_obj.get_role(int(self.bot_data[server]["warn_role"]))
                temp_warned_users: set = self.bot_data[server]["warned_users"].copy()

                for user_date in self.bot_data[server]["warned_users"]:
                    if user_date[1] < datetime.utcnow():
                        user_obj = server_obj.get_member(user_date[0])
                        if user_obj:
                            await user_obj.remove_roles(warn_role_obj, reason="Warn Time Expired.")
                        temp_warned_users.remove(user_date)
                self.bot_data[server]["warned_users"] = temp_warned_users.copy()

            if self.bot_data[server]["mute_role"] != 0:
                mute_role_obj = server_obj.get_role(int(self.bot_data[server]["mute_role"]))
                temp_muted_users = self.bot_data[server]["muted_users"].copy()

                for user_date in self.bot_data[server]["muted_users"]:
                    if user_date[1] < datetime.utcnow():
                        user_obj = server_obj.get_member(user_date[0])
                        if user_obj:
                            await user_obj.remove_roles(mute_role_obj, reason="Mute Time Expired.")
                        temp_muted_users.remove(user_date)
                        print("Removed mute on {}.".format(user_obj.name))
                self.bot_data[server]["muted_users"] = temp_muted_users.copy()
    """
    
    Call-out related.
    
    """
    @commands.has_permissions(administrator=True)
    @commands.command(name="callout_delete", usage="true/false, on/off, enable/disable, online/offline",
                      brief="Toggle call-out on message delete.")
    async def toggle_callout_delete(self, context, arg=None):
        server = context.guild.id
        if server not in self.bot_data:
            self.bot_data[server] = stupid_utils.default_server_data()

        self.bot_data[server]["callout_delete_enabled"], message = toggle_feature(arg, "callout_delete", self.enable_phrases, self.disable_phrases, self.bot_data[server]["callout_delete_enabled"])
        await context.send(message)

    async def callout_delete(self, message: discord.Message):
        server = message.guild.id
        if server not in self.bot_data:
            self.bot_data[server] = stupid_utils.default_server_data()
        try:
            if self.bot_data[server]["callout_delete_enabled"] and not message.author.bot and await check_audit_message_delete(message, message.author):
                await message.channel.send(random.sample(self.remind_delete_phrases, 1)[0].format(message.content, mention(message.author.id)))
        except discord.errors.Forbidden as ex:
            if ex.code == 50013:
                self.bot_data[server]["callout_delete_enabled"] = False
                await message.channel.send("I need permission to view the audit log to call out deletes. Disabling.")
    """

    Error Related

    """
    @set_mute_role.error
    @clear_mute_role.error
    @add_mute_role.error
    @remove_mute_role.error
    @set_warn_role.error
    @clear_warn_role.error
    @add_warn_role.error
    @remove_warn_role.error
    @toggle_callout_delete.error
    async def administrator_permission_error(self, context, error):
        if isinstance(error, commands.MissingPermissions):
            await context.send("You lack the administrator permission.")

    @warn.error
    @mute.error
    async def missing_access_error(self, context, error):
        if isinstance(error, commands.CommandInvokeError):
            await context.send("`403 FORBIDDEN: Missing Access` Am I missing a permission?")


"""

Outside of Cog.

"""


async def check_audit_message_delete(message: discord.Message, user: discord.User):
    audit_logs = message.guild.audit_logs(limit=1, action=discord.AuditLogAction.message_delete)
    async for audit in audit_logs:
        if audit.target.id == user.id:
            return False
    return True


def mention(author_id: str) -> str:
    return "<@{}>".format(author_id)


def role_check(user_roles: list, data_roles: set) -> bool:
    for role in user_roles:
        if str(role.id) in data_roles:
            return True
    return False


def add_role_to(storage: set, argument, success_message: str, duplicate_message: str) -> str:
    numbers = re.compile('\d+(?:\.\d+)?')
    if argument:
        if bool(re.search('\\d', argument)):
            role_id = numbers.findall(argument)[0]
        else:
            role_id = "invalid"
        if role_id in storage:
            message = duplicate_message
        elif role_id == "invalid":
            message = "You have to @mention the role."
        elif len(argument) > 4 and argument[:3] == "<@&" and argument[-1] == ">":
            storage.add(role_id)
            message = success_message.format(argument)
        else:
            message = "Role specified is invalid."
        return message
    else:
        return "You have to actually mention the role."


def remove_role_from(storage: set, argument, success_message: str, duplicate_message: str) -> str:
    numbers = re.compile('\d+(?:\.\d+)?')
    if argument:
        if bool(re.search('\\d', argument)):
            role_id = numbers.findall(argument)[0]
        else:
            role_id = "invalid"
        if role_id not in storage:
            message = duplicate_message
        elif role_id == "invalid":
            message = "you have to @mention the role."
        elif len(argument) > 4 and argument[:3] == "<@&" and argument[-1] == ">":
            storage.remove(role_id)
            message = success_message.format(argument)
        else:
            message = "Role specified is invalid."
        return message
    else:
        return "You have to actually mention the role."


def set_role_to(storage: int, argument, success_message: str, duplicate_message: str):
    numbers = re.compile('\d+(?:\.\d+)?')
    modified_storage = storage
    if argument:
        if bool(re.search('\\d', argument)):
            role_id = numbers.findall(argument)[0]
        else:
            role_id = "invalid"
        if role_id == storage:
            message = duplicate_message
        elif role_id == "invalid":
            message = "you have to @mention the role."
        elif len(argument) > 4 and argument[:3] == "<@&" and argument[-1] == ">":
            modified_storage = role_id
            message = success_message.format(argument)
        else:
            message = "Role specified is invalid."
        return modified_storage, message
    else:
        return storage, "You have to actually mention the role."


def toggle_feature(arg: str, feature_name: str, enable_phrases: set, disable_phrases: set, enabled_var: bool):
    if arg:
        if any(x in arg.lower() for x in enable_phrases):
            if enabled_var:
                return True, "{} is already enabled.".format(feature_name)
            else:
                return True, "{} enabled.".format(feature_name)
        elif any(x in arg.lower() for x in disable_phrases):
            if enabled_var:
                return False, "{} disabled.".format(feature_name)
            else:
                return False, "{} is already disabled.".format(feature_name)
        else:
            return enabled_var, "Argument `{}` is invalid for feature `{}`.".format(arg, feature_name)
    else:
        return enabled_var, "You need to actually say something after `;{}`, like enable or disable.".format(feature_name.lower())
