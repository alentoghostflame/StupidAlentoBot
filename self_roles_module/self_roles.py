from alento_bot import BaseModule, universal_text
from self_roles_module import role_cmds
from self_roles_module import text
from self_roles_module.storage import RoleSelfAssignData
from alento_bot import DiscordBot, StorageManager
from discord.ext import commands
import logging
from typing import Optional
import discord
import discord.errors


logger = logging.getLogger("main_bot")


class SelfRoleModule(BaseModule):
    def __init__(self, bot, storage):
        BaseModule.__init__(self, bot, storage)
        self.storage.guilds.register_data_name("self_roles_data", RoleSelfAssignData)
        self.add_cog(SelfRoleCog(self.storage))


class SelfRoleCog(commands.Cog, name="Self Roles"):
    def __init__(self, storage: StorageManager):
        self.storage: StorageManager = storage

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild_data: RoleSelfAssignData = self.storage.guilds.get(member.guild.id, "self_roles_data")
        if guild_data.auto_enabled and guild_data.auto_role and (role := member.guild.get_role(guild_data.auto_role)):
            await member.add_roles(role, reason="Auto-role")

    @commands.guild_only()
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.group(name="role", invoke_without_command=True, brief=text.ROLE_GROUP_BRIEF)
    async def role(self, context: commands.Context, role_keyword: Optional[str]):
        if context.invoked_subcommand is None:
            if role_keyword:
                guild_data: RoleSelfAssignData = self.storage.guilds.get(context.guild.id, "self_roles_data")
                if role_keyword.lower() in guild_data.roles:
                    await role_cmds.toggle_user_role(guild_data, context, role_keyword)
                else:
                    await context.send(text.ROLE_INVALID_SUBCOMMAND)
            else:
                # await role_cmds.send_help_embed(context)
                await context.send_help(context.command)

    @commands.guild_only()
    @role.command(name="info", brief=text.ROLE_INFO_BRIEF)
    async def role_info(self, context: commands.Context, role_keyword: Optional[str]):
        guild_data: RoleSelfAssignData = self.storage.guilds.get(context.guild.id, "self_roles_data")
        await role_cmds.send_list_embed(guild_data, context, role_keyword)

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @role.command(name="add", brief=text.ROLE_ADD_BRIEF)
    async def role_add(self, context: commands.Context, role_keyword: Optional[str],
                       role_mention: Optional[discord.Role]):
        guild_data: RoleSelfAssignData = self.storage.guilds.get(context.guild.id, "self_roles_data")
        await role_cmds.add_role(guild_data, context, role_keyword, role_mention)

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @role.command(name="remove", aliases=["rm", ], brief=text.ROLE_REMOVE_BRIEF)
    async def role_remove(self, context: commands.Context, role_keyword: Optional[str]):
        guild_data: RoleSelfAssignData = self.storage.guilds.get(context.guild.id, "self_roles_data")
        await role_cmds.remove_self_role(guild_data, context, role_keyword)

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @role.group(name="auto", brief=text.ROLE_AUTO_BRIEF, invoke_without_command=True)
    async def role_auto(self, context: commands.Context, *subcommand):
        if subcommand:
            await context.send(universal_text.INVALID_SUBCOMMAND)
        else:
            await context.send_help(context.command)

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_roles=True)
    @role_auto.command(name="enable", brief=text.ROLE_AUTO_ENABLE_BRIEF)
    async def role_auto_enable(self, context: commands.Context):
        guild_data: RoleSelfAssignData = self.storage.guilds.get(context.guild.id, "self_roles_data")
        if guild_data.auto_enabled:
            await context.send(universal_text.FEATURE_ALREADY_ENABLED_FORMAT.format("Auto-roles"))
        else:
            guild_data.auto_enabled = True
            await context.send(universal_text.FEATURE_ENABLED_FORMAT.format("Auto-roles"))

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @role_auto.command(name="disable", brief=text.ROLE_AUTO_DISABLE_BRIEF)
    async def role_auto_disable(self, context: commands.Context):
        guild_data: RoleSelfAssignData = self.storage.guilds.get(context.guild.id, "self_roles_data")
        if guild_data.auto_enabled:
            guild_data.auto_enabled = False
            await context.send(universal_text.FEATURE_DISABLED_FORMAT.format("Auto-roles"))
        else:
            await context.send(universal_text.FEATURE_ALREADY_DISABLED_FORMAT.format("Auto-roles"))

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_roles=True)
    @role_auto.command(name="set", brief=text.ROLE_AUTO_SET_BRIEF)
    async def role_auto_set(self, context: commands.Context, role: discord.Role):
        guild_data: RoleSelfAssignData = self.storage.guilds.get(context.guild.id, "self_roles_data")
        guild_data.auto_role = role.id
        await context.send(text.ROLE_AUTO_SET)

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_roles=True)
    @role_auto.command(name="sync", brief=text.ROLE_AUTO_SYNC_BRIEF)
    async def role_auto_sync(self, context: commands.Context):
        guild_data: RoleSelfAssignData = self.storage.guilds.get(context.guild.id, "self_roles_data")
        if guild_data.auto_role:
            role = context.guild.get_role(guild_data.auto_role)
            if role:
                updated_members = 0
                for member in context.guild.members:
                    if role not in member.roles:
                        updated_members += 1
                        await member.add_roles(role)
                await context.send(text.ROLE_AUTO_SYNC.format(updated_members))
            else:
                await context.send(text.AUTO_ROLE_INVALID)
        else:
            await context.send(text.NO_AUTO_ROLE_SET)

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @role_auto.command(name="info", brief=text.ROLE_AUTO_INFO_BRIEF)
    async def role_auto_info(self, context: commands.Context):
        guild_data: RoleSelfAssignData = self.storage.guilds.get(context.guild.id, "self_roles_data")
        embed = discord.Embed(title="Auto-Role Info", color=0x00ff00)

        basic_text = f"Enabled: `{guild_data.auto_enabled}`\n"
        if guild_data.auto_role:
            if role := context.guild.get_role(guild_data.auto_role):
                basic_text += f"Role: {role.mention}"
            else:
                basic_text += "Role: `<invalid-role>`"
        else:
            basic_text += "Role: `None`"

        embed.add_field(name="Basic", value=basic_text)

        await context.send(embed=embed)

    @role.error
    @role_info.error
    @role_add.error
    @role_remove.error
    @role_auto.error
    @role_auto_enable.error
    @role_auto_disable.error
    @role_auto_set.error
    @role_auto_sync.error
    @role_auto_info.error
    async def role_error_handler(self, context: commands.Context, error: Exception):
        if isinstance(error, commands.MissingRequiredArgument):
            await context.send_help(context.command)
        elif isinstance(error, commands.NoPrivateMessage):
            await context.send(text.NO_PRIVATE_MESSAGE)
        elif isinstance(error, commands.BotMissingPermissions):
            await context.send(text.BOT_MISSING_MANAGE_ROLES_PERMISSION)
        elif isinstance(error, commands.CommandInvokeError) and isinstance(error.original, discord.errors.Forbidden):
            await context.send(text.BOT_CANT_ADD_OR_REMOVE_ROLE)
        elif isinstance(error, commands.MissingPermissions):
            await context.send(text.USER_MISSING_ADMIN_PERMISSION)
        else:
            await context.send(f"A CRITICAL ERROR OCCURED:\n\n {type(error)}\n\n {error}\n\n"
                               f"REPORT THIS TO SOMBRA/ALENTO GHOSTFLAME!")
            raise error
