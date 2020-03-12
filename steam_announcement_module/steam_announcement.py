from steam_announcement_module.background_task import announcement_checker
from steam_announcement_module.admin import steam_announcement_admin
from storage_module.disk_storage import DiskStorage
from discord.ext import commands, tasks
import logging


logger = logging.getLogger("Main")


class SteamAnnouncementCog(commands.Cog, name="Steam Announcement Module"):
    def __init__(self, bot: commands.Bot, disk_storage: DiskStorage):
        super().__init__()
        self.bot = bot
        self.disk_storage = disk_storage

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Steam Announcement cog ready.")
        self.announcement_checker_loop.add_exception_type(Exception)
        self.announcement_checker_loop.start()

    def cog_unload(self):
        self.announcement_checker_loop.cancel()

    @commands.has_permissions(administrator=True)
    @commands.command(name="steam_announcement_admin", aliases=["sa_admin", "sat_admin"],
                      usage="set_channel/unset_channel/list_games/add_game/remove_game arg2",
                      brief="Configures the Steam Announcement feature.")
    async def steam_announcement_admin_command(self, context: commands.Context, arg1=None, arg2=None, *args):
        server_data = self.disk_storage.get_server(context.guild.id)
        await steam_announcement_admin(server_data, context, arg1, arg2, *args)

    @tasks.loop(minutes=10)
    async def announcement_checker_loop(self):
        await announcement_checker(self.bot, self.disk_storage)
