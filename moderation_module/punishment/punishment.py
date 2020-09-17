from moderation_module.punishment.commands import send_list_embed, add_role, remove_role, set_role, warn_cmd, mute_cmd
from moderation_module.storage import PunishmentManager
from moderation_module.punishment import text
from discord.ext import commands, tasks
from alento_bot import StorageManager
import moderation_module.text
import logging
import discord


logger = logging.getLogger("main_bot")


class PunishmentCog(commands.Cog, name="Moderation"):
    def __init__(self, storage: StorageManager, punishment_manager: PunishmentManager, bot: commands.Bot):
        self.storage: StorageManager = storage
        self.punish_manager: PunishmentManager = punishment_manager
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.remove_punish_loop.start()

    def cog_unload(self):
        self.remove_punish_loop.stop()

    @commands.has_permissions(administrator=True)
    @commands.group(name="admin", brief=text.ADMIN_BRIEF, invoke_without_command=True)
    async def admin(self, context: commands.Context):
        if context.message.content.strip() == f"{context.prefix}{context.command.name}":
            await context.send_help(context.command)
        else:
            await context.send(text.ADMIN_INVALID_COMMAND.format(context.prefix))

    @admin.command(name="info", brief=text.ADMIN_INFO_BRIEF)
    async def admin_info(self, context: commands.Context):
        punish_config = self.storage.guilds.get(context.guild.id, "punishment_config")
        await send_list_embed(punish_config, context)
    """
    START OF ADD GROUP
    """
    @admin.group(name="add", brief=text.ADMIN_ADD_BRIEF, invoke_without_command=True)
    async def admin_add(self, context: commands.Context):
        if context.message.content.strip() == f"{context.prefix}admin {context.command.name}":
            await context.send_help(context.command)
        else:
            await context.send(text.ADMIN_ADD_INVALID_COMMAND.format(context.prefix))

    @admin_add.command("warn", brief=text.ADMIN_ADD_WARN_BRIEF)
    async def admin_add_warn(self, context: commands.Context, role: discord.Role):
        punish_config = self.storage.guilds.get(context.guild.id, "punishment_config")
        await add_role(punish_config, context, "warn", role)

    @admin_add.command("mute", brief=text.ADMIN_ADD_MUTE_BRIEF)
    async def admin_add_mute(self, context: commands.Context, role: discord.Role):
        punish_config = self.storage.guilds.get(context.guild.id, "punishment_config")
        await add_role(punish_config, context, "mute", role)
    """
    END OF ADD GROUP
    
    START OF REMOVE GROUP
    """
    @admin.group(name="remove", aliases=["rm"], brief=text.ADMIN_REMOVE_BRIEF, invoke_without_command=True)
    async def admin_remove(self, context: commands.Context):
        if context.message.content.strip() == f"{context.prefix}admin {context.command.name}" or \
                context.message.content.strip() == f"{context.prefix}admin rm":
            await context.send_help(context.command)
        else:
            await context.send(text.ADMIN_REMOVE_INVALID_COMMAND.format(context.prefix))

    @admin_remove.command("warn", brief=text.ADMIN_REMOVE_WARN_BRIEF)
    async def admin_remove_warn(self, context: commands.Context, role: discord.Role):
        punish_config = self.storage.guilds.get(context.guild.id, "punishment_config")
        await remove_role(punish_config, context, "warn", role)

    @admin_remove.command("mute", brief=text.ADMIN_REMOVE_MUTE_BRIEF)
    async def admin_remove_mute(self, context: commands.Context, role: discord.Role):
        punish_config = self.storage.guilds.get(context.guild.id, "punishment_config")
        await remove_role(punish_config, context, "mute", role)
    """
    END OF REMOVE GROUP
    
    START OF SET GROUP
    """
    @admin.group(name="set", brief=text.ADMIN_SET_BRIEF, invoke_without_command=True)
    async def admin_set(self, context: commands.Context):
        if context.message.content.strip() == f"{context.prefix}admin {context.command.name}":
            await context.send_help(context.command)
        else:
            await context.send(text.ADMIN_SET_INVALID_COMMAND.format(context.prefix))

    @admin_set.command(name="warn", brief=text.ADMIN_SET_WARN_BRIEF)
    async def admin_set_warn(self, context: commands.Context, role: discord.Role):
        punish_config = self.storage.guilds.get(context.guild.id, "punishment_config")
        await set_role(punish_config, context, "warn", role)

    @admin_set.command(name="mute", brief=text.ADMIN_SET_MUTE_BRIEF)
    async def admin_set_mute(self, context: commands.Context, role: discord.Role):
        punish_config = self.storage.guilds.get(context.guild.id, "punishment_config")
        await set_role(punish_config, context, "mute", role)
    """
    END OF SET GROUP
    
    START OF NON-GROUPS
    """
    @commands.command(name="warn", brief=text.WARN_BRIEF)
    async def warn(self, context: commands.Context, mention: discord.Member):
        punish_config = self.storage.guilds.get(context.guild.id, "punishment_config")
        await warn_cmd(self.punish_manager, punish_config, context, mention)

    @commands.command(name="mute", brief=text.MUTE_BRIEF)
    async def mute(self, context: commands.Context, mention: discord.Member):
        punish_config = self.storage.guilds.get(context.guild.id, "punishment_config")
        await mute_cmd(self.punish_manager, punish_config, context, mention)

    @admin.error
    @admin_set_warn.error
    @admin_set_mute.error
    @admin_add_warn.error
    @admin_add_mute.error
    @admin_remove_warn.error
    @admin_remove_mute.error
    @warn.error
    @mute.error
    async def missing_permissions_error(self, context, error: Exception):
        if isinstance(error, commands.MissingPermissions):
            await context.send(moderation_module.text.MISSING_PERMISSIONS)
        elif isinstance(error, commands.CommandInvokeError):
            await context.send(moderation_module.text.IM_MISSING_PERMISSIONS.format(error))
        elif isinstance(error, commands.BadArgument) or isinstance(error, commands.MissingRequiredArgument):
            await context.send_help(context.command)
        else:
            await context.send(f"ERROR:\nType: {type(error)}\n{error}")
            raise error

    # @warn.error
    # async def punish_error(self, context, error: Exception):
    #     if isinstance(error, commands.CommandInvokeError):
    #         await context.send(moderation_module.text.IM_MISSING_PERMISSIONS.format(error))
    #     else:
    #         await context.send(f"ERROR:\nType: {type(error)}\n{error}")
    #         raise error

    @tasks.loop(seconds=30)
    async def remove_punish_loop(self):
        await self.punish_manager.remove_expired(self.bot)
