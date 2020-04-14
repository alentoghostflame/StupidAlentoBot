from storage_module.disk_storage import DiskStorage
from universal_module import utils
from discord.ext import commands
import faq_module.text as text
import faq_module.provide_faq
import faq_module.faq_admin
import logging
import sys


logger = logging.getLogger("Main")
sys.excepthook = utils.log_exception_handler


class FAQCog(commands.Cog, name="FAQ Module"):
    def __init__(self, disk_storage: DiskStorage):
        super().__init__()
        self.disk_storage = disk_storage

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("FAQ cog ready.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild:
            server_data = self.disk_storage.get_server(message.guild.id)
            if server_data.faq_enabled and not message.author.bot and not message.content.startswith(";"):
                await faq_module.provide_faq.provide_info(server_data.faq_phrases, message)

    @commands.command(name="faq_admin", usage="toggle, add_keyword, remove_keyword, list_keywords, list_edit_roles, "
                                              "add_edit_role, remove_edit_role",
                      brief="Controls the FAQ feature on your server.")
    async def faq_admin(self, context: commands.Context, arg1=None, arg2=None, arg3=None, image_url=None, *args):
        server_data = self.disk_storage.get_server(context.guild.id)

        if not utils.has_any_role(context.guild, server_data.faq_edit_roles, context.author) and not \
                context.author.guild_permissions.administrator:
            await context.send(text.LACK_PERMISSION_OR_ROLE)
            logger.debug("User {} lacks a permission or role.".format(context.author.display_name))
        else:
            await faq_module.faq_admin.faq_admin(server_data, context, arg1, arg2, arg3, image_url, *args)
