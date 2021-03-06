from OLD.steam_announcement_module.steam_announcement import SteamAnnouncementCog
from OLD.sidebar_status_module.sidebar_status import SidebarStatusCog
from OLD.storage_module.storage import StorageManager
from OLD.error_module.error import ErrorCog
from OLD.admin_module.admin import AdminCog
from OLD.karma_module.karma import KarmaCog
from OLD.eval_module.eval import EvalCog
from OLD.misc_module.misc import MiscCog
from OLD.faq_module.faq import FAQCog
from discord.ext import commands
# import universal_module.utils
import logging
# import sys


logger = logging.getLogger("Main")
# sys.excepthook = universal_module.utils.log_exception_handler


class StupidAlentoBot:
    def __init__(self):
        self.bot = commands.Bot(command_prefix=";", case_insensitive=True)
        self.storage_manager = StorageManager()

        self.disk_storage = self.storage_manager.get_disk_storage()
        self.ram_storage = self.storage_manager.get_ram_storage()

        self.bot.add_cog(MiscCog(self.bot, self.disk_storage, self.ram_storage))
        self.bot.add_cog(EvalCog(self.bot, self.disk_storage))
        self.bot.add_cog(AdminCog(self.disk_storage, self.bot))
        self.bot.add_cog(FAQCog(self.disk_storage))
        self.bot.add_cog(SidebarStatusCog(self.bot, self.ram_storage))
        self.bot.add_cog(SteamAnnouncementCog(self.bot, self.disk_storage))
        self.bot.add_cog(KarmaCog(self.disk_storage))
        self.bot.add_cog(ErrorCog())

    def run(self):
        if not self.disk_storage.config.token:
            logger.critical("Please put your token into config.yaml")
        else:
            self.bot.run(self.disk_storage.config.token)

    def load_data(self):
        self.storage_manager.load_everything()

    def save_data(self):
        # TODO: do NOT re-enable clean_servers() until safeguards are added to stop the file from getting wiped if
        #  Discord isn't reached before shutting down the bot.
        # self.disk_storage.clean_servers(self.bot)
        self.storage_manager.save_everything()
