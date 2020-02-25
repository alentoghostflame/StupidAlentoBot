from admin_module.background_task import background_task
from storage_module.stupid_storage import DiskStorage
from discord.ext import commands, tasks
from admin_module import text
import admin_module.warn
import stupid_utils
import logging
# import discord
import sys


logger = logging.getLogger("Main")
sys.excepthook = stupid_utils.log_exception_handler


class AdminCog(commands.Cog, name="New Admin Module"):
    def __init__(self, disk_storage: DiskStorage, bot: commands.Bot):
        self.disk_storage = disk_storage
        self.bot = bot

    def cog_unload(self):
        self.remove_warn_mute_loop.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Admin cog ready.")
        self.remove_warn_mute_loop.start()

    @commands.command(name="new_warn", usage="@user \"reason\"", brief="Warn the user.")
    async def warn(self, context, mentioned_user=None, reason=None, *args):
        server_data = self.disk_storage.get_server(context.guild.id)
        await admin_module.warn.warn(server_data.warner_roles, server_data.warn_role_id, server_data.warned_users,
                                     server_data.mute_role_id, server_data.muted_users, context, mentioned_user, reason,
                                     *args)

    @commands.has_permissions(administrator=True)
    @commands.command(name="warn_admin", usage="", brief="Admin command to configure warns.")
    async def warn_admin(self, context, arg1=None, arg2=text.DEFAULT_WARN_REASON, *args):
        server_data = self.disk_storage.get_server(context.guild.id)
        await admin_module.warn.warn_admin(server_data, context, arg1, arg2, *args)

    @tasks.loop(seconds=60)
    async def remove_warn_mute_loop(self):
        await background_task(self.bot, self.disk_storage)
