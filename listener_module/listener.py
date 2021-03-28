from alento_bot import StorageManager, BaseModule
from discord.ext import commands
from listener_module.steam import SteamAnnouncementCog, SteamAnnouncementCache, SteamAnnouncementConfig
from listener_module import twitch
import aiohttp, asyncio


class ListenerModule(BaseModule):
    def __init__(self, *args):
        BaseModule.__init__(self, *args)
        # self.storage.users.register_data_name("example_user_data", ExampleUserData)
        self.steam_cache = self.storage.caches.register_cache("steam_announcement_cache", SteamAnnouncementCache)
        self.twitch_config = self.storage.caches.register_cache("twitch_config", twitch.TwitchBotConfig)
        self.twitch_cache = self.storage.caches.register_cache("twitch_cache", twitch.TwitchBotCache)
        self.storage.guilds.register_data_name("steam_announcement_config", SteamAnnouncementConfig)
        self.storage.guilds.register_data_name("twitch_config", twitch.TwitchGuildConfig)
        self.session = aiohttp.ClientSession()
        self.add_cog(ListenerCog(self.storage))
        self.add_cog(SteamAnnouncementCog(self.bot, self.storage, self.steam_cache, self.session))
        self.add_cog(twitch.TwitchCog(self.bot, self.storage, self.twitch_config, self.twitch_cache, self.session))

    def save(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.session.close())
        loop.close()


class ListenerCog(commands.Cog, name="Listeners"):
    def __init__(self, storage: StorageManager):
        self.storage = storage

    # @commands.command(name="example", description="Example description text.", brief="Example brief text.")
    # async def example_command(self, context: commands.Context, *args):
    #     user_data: ExampleUserData = self.storage.users.get(context.author.id, "example_user_data")
    #     if args:
    #         user_data.example_count += 1
    #         await context.send(f"You gave: {', '.join(args)}.")
    #     else:
    #         user_data.example_count += 1
    #         await context.send("Hi there!")
