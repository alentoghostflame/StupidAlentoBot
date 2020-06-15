from OLD.sidebar_status_module.desktop_portal import desktop_portal_sidebars
# from storage_module.server_data import DiskServerData
from OLD.storage_module.ram_storage import RAMStorage
from discord.ext import commands, tasks
# import universal_module.utils
# import universal_module.text
import logging
# import discord
# import sys


logger = logging.getLogger("Main")
# sys.excepthook = universal_module.utils.log_exception_handler


class SidebarStatusCog(commands.Cog, name="Sidebar Status Module"):
    def __init__(self, bot: commands.Bot, ram_storage: RAMStorage):
        super().__init__()
        self.bot = bot
        self.ram_storage = ram_storage

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Sidebar Status cog ready.")
        self.desktop_portal_loop.start()

    def cog_unload(self):
        self.desktop_portal_loop.cancel()

    @tasks.loop(minutes=5)
    async def desktop_portal_loop(self):
        await desktop_portal_sidebars(self.bot, self.ram_storage)
