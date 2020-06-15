from misc_module.storage import WelcomeConfig, SteamAnnouncementConfig, SteamAnnouncementCache
from misc_module.steam_announcements import SteamAnnouncementCog
from misc_module.super_jank_ville import SidebarStatusCog
from misc_module.welcomes import WelcomeCog
from alento_bot import DiscordBot
from discord.ext import commands
import logging
import discord


logger = logging.getLogger("main_bot")


class MiscModule:
    def __init__(self, discord_bot: DiscordBot):
        self.discord_bot: DiscordBot = discord_bot
        # self.discord_bot.storage.guilds.register_data_name("faq_config", FAQConfig)
        # self.faq_manager: FAQManager = FAQManager(self.discord_bot.storage)
        # noinspection PyArgumentList
        self.steam_cache = SteamAnnouncementCache(self.discord_bot.storage.config)
        self.discord_bot.storage.caches.register_cache(self.steam_cache, "steam_announcement_cache")
        self.discord_bot.storage.guilds.register_data_name("welcome_config", WelcomeConfig)
        self.discord_bot.storage.guilds.register_data_name("steam_announcement_config", SteamAnnouncementConfig)

    def register_cogs(self):
        logger.info("Registering cogs for Misc.")
        # self.discord_bot.add_cog(FAQCog(self.discord_bot.storage, self.faq_manager, self.discord_bot.bot))
        self.discord_bot.add_cog(WelcomeCog(self.discord_bot.storage))
        self.discord_bot.add_cog(SteamAnnouncementCog(self.discord_bot.bot, self.discord_bot.storage, self.steam_cache))
        self.discord_bot.add_cog(SidebarStatusCog(self.discord_bot.bot))
