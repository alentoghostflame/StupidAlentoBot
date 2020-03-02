from misc_module.callout_delete import callout_delete, callout_delete_admin
from misc_module.welcome import welcome, welcome_admin
from storage_module.disk_storage import DiskStorage
from storage_module.ram_storage import RAMStorage
from misc_module.userinfo import userinfo
from misc_module.status import bot_status
from universal_module import utils
from discord.ext import commands
import universal_module.text
import logging
import discord
# import random
import sys

logger = logging.getLogger("Main")
sys.excepthook = utils.log_exception_handler


class MiscCog(commands.Cog, name="Misc Module"):
    def __init__(self, bot: commands.Bot, disk_storage: DiskStorage, ram_storage: RAMStorage):
        super().__init__()
        self.bot = bot
        self.disk_storage = disk_storage
        self.ram_storage = ram_storage

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Misc module ready.")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        server_data = self.disk_storage.get_server(member.guild.id)
        logger.debug("Member {} joined a server, {}".format(member.display_name, server_data.welcome_enabled))
        if server_data.welcome_enabled:
            # await self.send_welcome(member)
            await welcome(server_data, member)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        self.ram_storage.total_messages_read += 1
        if message.author.id == self.bot.user.id:
            self.ram_storage.total_messages_sent += 1

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        server_data = self.disk_storage.get_server(message.guild.id)
        if server_data.callout_delete_enabled:
            await callout_delete(server_data, message)

    @commands.command(name="status", brief="Lists information about the bot and what it does on your server.")
    async def status(self, context):
        server_data = self.disk_storage.get_server(context.guild.id)
        await bot_status(server_data, self.ram_storage, context)

    @commands.has_permissions(administrator=True)
    @commands.command(name="welcome_admin", usage="toggle, add, remove, list, set_channel, unset_channel",
                      brief="Control welcome messages on join.")
    async def welcome_admin_command(self, context, arg1=None, arg2=None, *args):
        server_data = self.disk_storage.get_server(context.guild.id)
        await welcome_admin(server_data, context, arg1, arg2, *args)

    @commands.has_permissions(administrator=True)
    @commands.command(name="callout_delete_admin", usage="toggle",
                      brief="Control the calling out of deletes.")
    async def callout_delete_admin_command(self, context, arg1=None, arg2=None, *args):
        server_data = self.disk_storage.get_server(context.guild.id)
        await callout_delete_admin(server_data, context, arg1, arg2, *args)

    @commands.command(name="userinfo", brief="Get information of provided user.")
    async def userinfo_command(self, context, arg=None):
        await userinfo(self.bot, context, arg)

    @welcome_admin_command.error
    async def administrator_permission_error(self, context, error):
        if isinstance(error, commands.MissingPermissions):
            await context.send(universal_module.text.PERMISSION_MISSING_ADMINISTRATOR)
