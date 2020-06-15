from moderation_module.punishment.commands import mod_control, warn_cmd, mute_cmd
from moderation_module.storage import PunishmentManager
from discord.ext import commands, tasks
from alento_bot import StorageManager
import moderation_module.text
import logging


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
    @commands.command(name="moderator_control", aliases=["moderator", "mod"])
    async def moderator_control(self, context: commands.Context, arg1=None, arg2=None, arg3=None):
        punish_config = self.storage.guilds.get(context.guild.id, "punishment_config")
        await mod_control(punish_config, context, arg1, arg2, arg3)

    @commands.command(name="warn")
    async def warn(self, context: commands.Context, arg1=None):
        punish_config = self.storage.guilds.get(context.guild.id, "punishment_config")
        await warn_cmd(self.punish_manager, punish_config, context, arg1)

    @commands.command(name="mute")
    async def mute(self, context: commands.Context, arg1=None):
        punish_config = self.storage.guilds.get(context.guild.id, "punishment_config")
        await mute_cmd(self.punish_manager, punish_config, context, arg1)

    @moderator_control.error
    async def missing_permissions_error(self, context, error: Exception):
        if isinstance(error, commands.MissingPermissions):
            await context.send(moderation_module.text.MISSING_PERMISSIONS)
        else:
            await context.send(f"ERROR:\nType: {type(error)}\n{error}")
            raise error

    @warn.error
    async def punish_error(self, context, error: Exception):
        if isinstance(error, commands.CommandInvokeError):
            await context.send(moderation_module.text.IM_MISSING_PERMISSIONS.format(error))
        else:
            await context.send(f"ERROR:\nType: {type(error)}\n{error}")
            raise error

    @tasks.loop(seconds=30)
    async def remove_punish_loop(self):
        await self.punish_manager.remove_expired(self.bot)
