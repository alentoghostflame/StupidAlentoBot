from storage_module.stupid_storage import DiskStorage
import faq_module.provide_faq
import faq_module.faq_admin
from discord.ext import commands
import stupid_utils
import logging
# import discord
import sys


logger = logging.getLogger("Main")
sys.excepthook = stupid_utils.log_exception_handler


class FAQCog(commands.Cog, name="FAQ Module"):
    def __init__(self, disk_storage: DiskStorage):
        super().__init__()
        self.disk_storage = disk_storage

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("FAQ cog ready.")

    @commands.Cog.listener()
    async def on_message(self, message):
        server_data = self.disk_storage.get_server(message.guild.id)

        if server_data.faq_enabled and not message.author.bot and not message.content.startswith(";"):
            await faq_module.provide_faq.provide_info(server_data.faq_phrases, message)

    @commands.has_permissions(administrator=True)
    @commands.command(name="faq_admin", usage="", brief="")
    async def faq_admin(self, context, arg1=None, arg2=None, arg3=None, *args):
        server_data = self.disk_storage.get_server(context.guild.id)
        await faq_module.faq_admin.faq_admin(server_data, context, arg1, arg2, arg3, *args)
