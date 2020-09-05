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


class SelfRoleModule:
    def __init__(self, discord_bot: DiscordBot):
        self.discord_bot: DiscordBot = discord_bot

        self.discord_bot.storage.guilds.register_data_name("self_roles_data", RoleSelfAssignData)

    def register_cogs(self):
        logger.info("Registering SelfRole cog.")
        self.discord_bot.add_cog(SelfRoleCog(self.discord_bot.storage))


class SelfRoleCog(commands.Cog, name="Self Roles"):
    def __init__(self, storage: StorageManager):
        self.storage: StorageManager = storage

    @commands.guild_only()
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.group(name="role", invoke_without_command=True, brief=text.ROLE_GROUP_BRIEF)
    async def role_group(self, context: commands.Context, role_keyword: Optional[str]):
        if context.invoked_subcommand is None:
            if role_keyword:
                guild_data: RoleSelfAssignData = self.storage.guilds.get(context.guild.id, "self_roles_data")
                if role_keyword.lower() in guild_data.roles:
                    await role_cmds.toggle_user_role(guild_data, context, role_keyword)
                else:
                    await context.send(text.ROLE_INVALID_SUBCOMMAND)
            else:
                await role_cmds.send_help_embed(context)

    @commands.guild_only()
    @role_group.command(name="info", brief=text.ROLE_INFO_BRIEF)
    async def role_info(self, context: commands.Context, role_keyword: Optional[str]):
        guild_data: RoleSelfAssignData = self.storage.guilds.get(context.guild.id, "self_roles_data")
        await role_cmds.send_list_embed(guild_data, context, role_keyword)

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @role_group.command(name="add", brief=text.ROLE_ADD_BRIEF)
    async def role_add(self, context: commands.Context, role_keyword: Optional[str],
                       role_mention: Optional[discord.Role]):
        guild_data: RoleSelfAssignData = self.storage.guilds.get(context.guild.id, "self_roles_data")
        await role_cmds.add_role(guild_data, context, role_keyword, role_mention)

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @role_group.command(name="remove", aliases=["rm", ], brief=text.ROLE_REMOVE_BRIEF)
    async def role_remove(self, context: commands.Context, role_keyword: Optional[str]):
        guild_data: RoleSelfAssignData = self.storage.guilds.get(context.guild.id, "self_roles_data")
        await role_cmds.remove_self_role(guild_data, context, role_keyword)

    @role_group.error
    @role_info.error
    @role_add.error
    @role_remove.error
    async def role_error_handler(self, context: commands.Context, error: Exception):
        if isinstance(error, commands.NoPrivateMessage):
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
