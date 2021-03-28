from listener_module.steam.commands import announcement_checker, steam_commands
from listener_module.steam.steam_announcement_data import SteamAnnouncementConfig, SteamAnnouncementCache
from listener_module.steam import text
from discord.ext import commands, tasks
from discord.ext.commands.errors import MissingRequiredArgument, BadArgument
from alento_bot import StorageManager
from aiohttp import ClientSession
import logging


logger = logging.getLogger("main_bot")


class SteamAnnouncementCog(commands.Cog, name="Listeners"):
    def __init__(self, bot: commands.Bot, storage: StorageManager, cache: SteamAnnouncementCache,
                 session: ClientSession):
        self.session = session
        self.storage: StorageManager = storage
        self.cache: SteamAnnouncementCache = cache
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.announcement_checker_loop.start()

    def cog_unload(self):
        self.announcement_checker_loop.stop()

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.group(name="steam", brief=text.STEAM_BRIEF, invoke_without_command=True)
    async def steam(self, context: commands.Context, *subcommand):
        if subcommand:
            await context.send(text.INVALID_COMMAND)
        else:
            await context.send_help(context.command)

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @steam.command(name="info", brief=text.STEAM_INFO_BRIEF)
    async def steam_info(self, context: commands.Context):
        steam_config: SteamAnnouncementConfig = self.storage.guilds.get(context.guild.id, "steam_announcement_config")
        await steam_commands.send_list_embed(steam_config, context)

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @steam.command(name="enable", brief=text.STEAM_ENABLE_BRIEF)
    async def steam_enable(self, context: commands.Context):
        steam_config: SteamAnnouncementConfig = self.storage.guilds.get(context.guild.id, "steam_announcement_config")
        if steam_config.enabled:
            await context.send(text.STEAM_ENABLED_ALREADY)
        else:
            steam_config.enabled = True
            await context.send(text.STEAM_ENABLED)
        self.cache.tracked_guilds.add(context.guild.id)

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @steam.command(name="disable", brief=text.STEAM_ENABLE_BRIEF)
    async def steam_disable(self, context: commands.Context):
        steam_config: SteamAnnouncementConfig = self.storage.guilds.get(context.guild.id, "steam_announcement_config")
        if steam_config.enabled:
            steam_config.enabled = False
            await context.send(text.STEAM_DISABLED)
        else:
            await context.send(text.STEAM_DISABLED_ALREADY)
        self.cache.tracked_guilds.discard(context.guild.id)

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @steam.command(name="set", brief=text.STEAM_SET_BRIEF)
    async def steam_set(self, context: commands.Context):
        steam_config: SteamAnnouncementConfig = self.storage.guilds.get(context.guild.id, "steam_announcement_config")
        steam_config.announcement_channel_id = context.channel.id
        await context.send(text.STEAM_SET_CHANNEL)

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @steam.command(name="add", brief=text.STEAM_ADD_BRIEF)
    async def steam_add(self, context: commands.Context, game_id: int):
        steam_config: SteamAnnouncementConfig = self.storage.guilds.get(context.guild.id, "steam_announcement_config")
        if game_id in steam_config.tracked_game_ids:
            await context.send(text.STEAM_ADDED_DUPLICATE)
        else:
            steam_config.tracked_game_ids.add(game_id)
            await context.send(text.STEAM_ADDED.format(game_id))

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @steam.command(name="remove", brief=text.STEAM_REMOVE_BRIEF, aliases=["rm", ])
    async def steam_remove(self, context: commands.Context, game_id: int):
        steam_config: SteamAnnouncementConfig = self.storage.guilds.get(context.guild.id, "steam_announcement_config")
        if game_id in steam_config.tracked_game_ids:
            steam_config.tracked_game_ids.remove(game_id)
            await context.send(text.STEAM_REMOVED.format(game_id))
        else:
            await context.send(text.STEAM_REMOVED_NOTHING)

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @steam.command(name="trigger", brief="Force an announcement immediately.")
    async def steam_trigger(self, context: commands.Context):
        await announcement_checker(self.bot, self.storage, self.cache, self.session)
        await context.send("Triggered the Steam Announcement checker.")

    @tasks.loop(minutes=10)
    async def announcement_checker_loop(self):
        await announcement_checker(self.bot, self.storage, self.cache, self.session)

    @steam_add.error
    @steam_remove.error
    async def exception_handler(self, context: commands.Context, exception: Exception):
        if isinstance(exception, MissingRequiredArgument):
            await context.send_help(context.command)
        elif isinstance(exception, BadArgument):
            await context.send(text.BAD_ARGUMENT)
        else:
            await context.send(f"a critical error has occurred. send this message to alento ghostflame.\n"
                               f"{type(exception)}\n{exception}")
            raise exception
