from OLD.admin_module.background_task import background_task
from OLD.storage_module.disk_storage import DiskStorage
from discord.ext import commands, tasks
# from universal_module import utils
import OLD.admin_module.warn
import OLD.admin_module.mute
import logging
# import sys


logger = logging.getLogger("Main")
# sys.excepthook = utils.log_exception_handler


class AdminCog(commands.Cog, name="Admin Module"):
    def __init__(self, disk_storage: DiskStorage, bot: commands.Bot):
        self.disk_storage = disk_storage
        self.bot = bot

    def cog_unload(self):
        self.remove_warn_mute_loop.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Admin cog ready.")
        self.remove_warn_mute_loop.start()

    @commands.command(name="warn", usage="@user \"reason\"", brief="Warn the user.")
    async def warn(self, context, mentioned_user=None, reason=None, *args):
        server_data = self.disk_storage.get_server(context.guild.id)
        await OLD.admin_module.warn.warn(server_data, context, mentioned_user, reason, *args)

    @commands.has_permissions(administrator=True)
    @commands.command(name="warn_admin", usage="", brief="Admin command to configure warns.")
    async def warn_admin(self, context, arg1=None, arg2=None, *args):
        server_data = self.disk_storage.get_server(context.guild.id)
        await OLD.admin_module.warn.warn_admin(server_data, context, arg1, arg2, *args)

    @commands.command(name="mute", usage="@user \"reason\"", brief="Mute the user.")
    async def mute(self, context, mentioned_user=None, reason=None, *args):
        server_data = self.disk_storage.get_server(context.guild.id)
        await OLD.admin_module.mute.mute(server_data, context, mentioned_user, reason, *args)

    @commands.has_permissions(administrator=True)
    @commands.command(name="mute_admin", usage="", brief="Admin command to configure mutes.")
    async def mute_admin(self, context, arg1=None, arg2=None, *args):
        server_data = self.disk_storage.get_server(context.guild.id)
        await OLD.admin_module.mute.mute_admin(server_data, context, arg1, arg2, *args)

    @tasks.loop(seconds=60)
    async def remove_warn_mute_loop(self):
        await background_task(self.bot, self.disk_storage)
