from storage_module.stupid_storage import DiskStorage
import admin_module.warn
from discord.ext import commands
import stupid_utils
import logging
# import discord
import sys


logger = logging.getLogger("Main")
sys.excepthook = stupid_utils.log_exception_handler


class AdminCog(commands.Cog, name="New Admin Module"):
    def __init__(self, disk_storage: DiskStorage):
        self.disk_storage = disk_storage

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Admin cog ready.")

    @commands.command(name="new_warn", usage="@user \"reason\"", brief="Warn the user.")
    async def warn(self, context, mentioned_user=None, reason=None, *args):
        server_data = self.disk_storage.get_server(context.guild.id)
        await admin_module.warn.warn(server_data.warner_roles, server_data.warn_role_id, context, mentioned_user,
                                     reason, *args)

    @commands.has_permissions(administrator=True)
    @commands.command(name="warn_admin", usage="", brief="Admin command to configure warns.")
    async def warn_admin(self, context, arg1=None, arg2=None, *args):
        server_data = self.disk_storage.get_server(context.guild.id)
        await admin_module.warn.warn_admin(server_data, context, arg1, arg2, *args)
