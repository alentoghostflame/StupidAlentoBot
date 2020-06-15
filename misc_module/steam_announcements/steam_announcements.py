from misc_module.steam_announcements.commands import steam_announcement_control, announcement_checker
from misc_module.storage import SteamAnnouncementConfig, SteamAnnouncementCache
from discord.ext import commands, tasks
from alento_bot import StorageManager
import logging
import discord


logger = logging.getLogger("main_bot")


class SteamAnnouncementCog(commands.Cog, name="Steam Announcements"):
    def __init__(self, bot: commands.Bot, storage: StorageManager, cache: SteamAnnouncementCache):
        self.storage: StorageManager = storage
        self.cache: SteamAnnouncementCache = cache
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.announcement_checker_loop.start()

    def cog_unload(self):
        self.announcement_checker_loop.stop()

    @commands.has_permissions(administrator=True)
    @commands.command(name="steam_announcement_control", aliases=["sa_control", "steam"])
    async def steam_announcment_control_command(self, context: commands.Context, arg1=None, arg2=None):
        self.cache.tracked_guilds.add(context.guild.id)
        steam_config: SteamAnnouncementConfig = self.storage.guilds.get(context.guild.id, "steam_announcement_config")
        await steam_announcement_control(steam_config, context, arg1, arg2)

    @tasks.loop(minutes=10)
    async def announcement_checker_loop(self):
        # logger.info("RUNNING TOP LEVEL CHECKER.")
        await announcement_checker(self.bot, self.storage, self.cache)


