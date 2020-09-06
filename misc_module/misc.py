from misc_module.storage import WelcomeConfig, SteamAnnouncementConfig, SteamAnnouncementCache
from misc_module.steam_announcements import SteamAnnouncementCog
from misc_module.super_jank_ville import SidebarStatusCog
from misc_module.welcomes import WelcomeCog
from alento_bot import BaseModule
import logging


logger = logging.getLogger("main_bot")


class MiscModule(BaseModule):
    def __init__(self, bot, storage):
        BaseModule.__init__(self, bot, storage)
        # noinspection PyArgumentList
        self.steam_cache = SteamAnnouncementCache(self.storage.config)
        self.storage.caches.register_cache(self.steam_cache, "steam_announcement_cache")
        self.storage.guilds.register_data_name("welcome_config", WelcomeConfig)
        self.storage.guilds.register_data_name("steam_announcement_config", SteamAnnouncementConfig)

        self.add_cog(WelcomeCog(self.storage))
        self.add_cog(SteamAnnouncementCog(self.bot, self.storage, self.steam_cache))
        self.add_cog(SidebarStatusCog(self.bot))
