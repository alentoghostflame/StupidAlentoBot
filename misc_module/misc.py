from misc_module.storage import WelcomeConfig
# from misc_module.steam_announcements import SteamAnnouncementCog
from misc_module.super_jank_ville import SidebarStatusCog
from misc_module.welcomes import WelcomeCog
from alento_bot import BaseModule
import aiohttp, asyncio
import logging
# from alento_bot import StorageManager, BaseModule, user_data_transformer
from discord.ext import commands


logger = logging.getLogger("main_bot")


class MiscModule(BaseModule):
    def __init__(self, *args):
        BaseModule.__init__(self, *args)
        self.session = aiohttp.ClientSession()
        # noinspection PyArgumentList
        # self.steam_cache = SteamAnnouncementCache(self.storage.config)
        # self.storage.caches.register_cache("steam_announcement_cache", self.steam_cache)
        self.storage.guilds.register_data_name("welcome_config", WelcomeConfig)
        # self.storage.guilds.register_data_name("steam_announcement_config", SteamAnnouncementConfig)

        self.add_cog(WelcomeCog(self.storage))
        # self.add_cog(SteamAnnouncementCog(self.bot, self.storage, self.steam_cache))
        self.add_cog(SidebarStatusCog(self.bot, self.session))
        self.add_cog(MiscCog())

    def save(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.session.close())
        loop.close()


class MiscCog(commands.Cog, name="Misc"):
    def __init__(self):
        pass



