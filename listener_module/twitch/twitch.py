from alento_bot import cache_transformer, guild_data_transformer, error_handler, universal_text
from listener_module.twitch.twitch_api import TwitchAPI, TwitchStreamData, TwitchUserData
from typing import Optional, Set, List, Dict
from discord.ext import commands, tasks
from aiohttp import ClientSession
from alento_bot import StorageManager
import discord
import logging


# TODO: Unhandled error occurred, <class 'discord.ext.commands.errors.CommandInvokeError'> Command raised an exception: AttributeError: 'NoneType' object has no attribute 'get_user_data'
# Without the config filled out, certain commands are getting through.


TOKEN_URL = "https://id.twitch.tv/oauth2/token"


logger = logging.getLogger("main_bot")


@cache_transformer(name="twitch_config")
class TwitchBotConfig:
    def __init__(self):
        self.client_id = ""
        self.client_secret = ""


@cache_transformer(name="twitch_cache")
class TwitchBotCache:
    def __init__(self):
        # self.access_token = ""
        # self.expiration: Optional[datetime] = None
        self.tracked_servers: Set[int] = set()
        self.was_streamer_online: Dict[int, bool] = dict()

    # async def update_token(self, config: TwitchBotConfig, session: ClientSession):
    #     response = await session.post(TOKEN_URL, params={"client_id": config.client_id,
    #                                                      "client_secret": config.client_secret,
    #                                                      "grant_type": "client_credentials"})
    #     response_json = await response.json()
    #     logger.debug(response_json)
    #     if status := response_json.get("status", None):
    #         if status == 400:
    #             raise TwitchInvalidClientID("Invalid Client ID, is the twitch config properly setup?")
    #         elif status == 403:
    #             raise TwitchInvalidClientSecret("Invalid Client Secret, is the twitch config properly setup?")
    #         else:
    #             raise TwitchInvalidClientOther(f"Invalid Client something, status {status}, FIXME.")
    #     else:
    #         self.access_token = response_json["access_token"]
    #         self.expiration = datetime.utcnow() + timedelta(seconds=response_json["expires_in"])
    #
    # async def get_token(self, config: TwitchBotConfig, session: ClientSession) -> str:
    #     if not self.expiration or self.expiration < datetime.utcnow():
    #         await self.update_token(config, session)
    #     return self.access_token


@guild_data_transformer(name="twitch_config")
class TwitchGuildConfig:
    def __init__(self):
        self.streamers: List[int] = list()
        # self.id_to_name: Dict[int, str] = dict()
        self.channel_id: Optional[int] = None
        self.enabled = False


class TwitchCog(commands.Cog, name="Listeners"):
    def __init__(self, bot: commands.Bot, storage: StorageManager, twitch_config: TwitchBotConfig,
                 twitch_cache: TwitchBotCache, session: ClientSession):
        self.storage = storage
        self.config = twitch_config
        self.cache = twitch_cache
        self.bot: commands.Bot = bot
        self.session = session
        self.api: Optional[TwitchAPI] = None
        if not self.config.client_id:
            logger.warning("client_id in twitch_config is empty, make an application and fill it out!")
        if not self.config.client_secret:
            logger.warning("client_secret in twitch_config is empty, make an application and fill it out!")

    @commands.Cog.listener()
    async def on_ready(self):
        if self.config.client_id and self.config.client_secret:
            # TODO: Actually make errors related to this appear when trying to activate twitch.
            self.api = TwitchAPI(self.session, self.config.client_id, self.config.client_secret)
            self.twitch_checker.start()
        else:
            logger.info("Missing Client ID and Secret, not starting Twitch Checker.")

    def cog_unload(self):
        self.twitch_checker.stop()

    @commands.group(name="twitch", brief="Show when streamers go offline or online!", invoke_without_command=True)
    async def twitch(self, context: commands.Context, *subcommand):
        if subcommand:
            await context.send(universal_text.INVALID_SUBCOMMAND)
        else:
            await context.send_help(context.command)

    @twitch.command(name="info", brief="Shows Twitch Listener info.")
    async def twitch_info(self, context: commands.Context):
        config: TwitchGuildConfig = self.storage.guilds.get(context.guild.id, "twitch_config")
        embed = discord.Embed(title="Twitch", color=0x6441A5)

        if config.channel_id is None:
            channel = f"`None`"
        elif temp := context.guild.get_channel(config.channel_id):
            channel = temp
        else:
            channel = f"`{config.channel_id}`"

        basic_text = f"Enabled: {config.enabled}\nChannel: {channel}"
        embed.add_field(name="Basic", value=basic_text, inline=False)
        if config.streamers:
            user_data_list = await self.api.get_bulk_user_data([], config.streamers)
            streamer_text = "\n".join([user_data.display_name for user_data in user_data_list])
            # for i in range(len(config.streamers)):
                # streamer_text += f"{i + 1}: `{config.id_to_name[config.streamers[i]]}\n"
        else:
            streamer_text = "None"
        embed.add_field(name="Streamers Added", value=streamer_text)
        await context.send(embed=embed)

    @commands.has_permissions(administrator=True)
    @twitch.command(name="enable", brief="Enables the Twitch Listener for this server.")
    async def twitch_enable(self, context: commands.Context):
        config: TwitchGuildConfig = self.storage.guilds.get(context.guild.id, "twitch_config")
        if config.enabled:
            await context.send(universal_text.FEATURE_ALREADY_ENABLED_FORMAT.format("Twitch Listener"))
        else:
            config.enabled = True
            await context.send(universal_text.FEATURE_ENABLED_FORMAT.format("Twitch Listener"))
        self.cache.tracked_servers.add(context.guild.id)

    @commands.has_permissions(administrator=True)
    @twitch.command(name="disable", brief="Disables the Twitch Listener for this server.")
    async def twitch_disable(self, context: commands.Context):
        config: TwitchGuildConfig = self.storage.guilds.get(context.guild.id, "twitch_config")
        if config.enabled:
            config.enabled = False
            await context.send(universal_text.FEATURE_DISABLED_FORMAT.format("Twitch Listener"))
        else:
            await context.send(universal_text.FEATURE_ALREADY_DISABLED_FORMAT.format("Twitch Listener"))
        self.cache.tracked_servers.discard(context.guild.id)

    @commands.has_permissions(administrator=True)
    @twitch.command(name="set", brief="Sets the current channel to be the announcement channel.")
    async def twitch_set(self, context: commands.Context):
        config: TwitchGuildConfig = self.storage.guilds.get(context.guild.id, "twitch_config")
        config.channel_id = context.channel.id
        await context.send("This is now the Twitch announcement channel.")

    @commands.has_permissions(administrator=True)
    @twitch.command(name="add", brief="Adds the given streamer to the notification list.")
    async def twitch_add(self, context: commands.Context, twitch_name: str):
        config: TwitchGuildConfig = self.storage.guilds.get(context.guild.id, "twitch_config")
        # if twitch_id := await self.get_streamer_id(twitch_name):
        if user_data := await self.api.get_user_data(twitch_name):
            if user_data.id in config.streamers:
                await context.send("That streamer was already added!")
            else:
                # streamer_data = await self.get_streamer_data(user_data.id)
                # self.id_to_name_cache[twitch_id] = streamer_data["broadcaster_name"]
                config.streamers.append(user_data.id)
                await context.send(f"ID: `{user_data.id}`, {user_data.display_name} has been added to the "
                                   f"tracked users.")
        else:
            await context.send("No streamer with that name was found.")

    @commands.has_permissions(administrator=True)
    @twitch.command(name="rm", brief="Removes a given streamer from the notification list.")
    async def twitch_rm(self, context: commands.Context, twitch_name: str):
        config: TwitchGuildConfig = self.storage.guilds.get(context.guild.id, "twitch_config")
        if user_data := await self.api.get_user_data(twitch_name):
            if user_data.id in config.streamers:
                config.streamers.remove(user_data.id)
                await context.send(f"{user_data.display_name} has been removed from the tracked users.")
            else:
                await context.send("You aren't tracking that streamer.")
        else:
            await context.send("No streamer with that name was found.")

    @tasks.loop(minutes=10)
    async def twitch_checker(self):
        send_streamer_to = dict()

        for guild_id in self.cache.tracked_servers:
            guild_config: TwitchGuildConfig = self.storage.guilds.get(guild_id, "twitch_config")
            guild: discord.Guild = self.bot.get_guild(guild_id)
            if guild_config.enabled and guild_config.channel_id and \
                    (channel := guild.get_channel(guild_config.channel_id)):
                for streamer_id in guild_config.streamers:
                    if streamer_id not in send_streamer_to:
                        send_streamer_to[streamer_id] = list()
                    send_streamer_to[streamer_id].append(channel)

        offline_streamers = set(send_streamer_to.keys())
        streamer_data_list = await self.api.get_stream_data(list(send_streamer_to.keys()))
        # logger.debug(streamer_data_list)
        # logger.debug(f"Total streamer set: {offline_streamers}")
        for stream_data in streamer_data_list:
            if not self.cache.was_streamer_online.get(stream_data.user_id, False):
                user_data = await self.api.get_user_data(stream_data.user_id)
                embed = get_online_stream_embed(stream_data, user_data)
                for guild_channel in send_streamer_to[stream_data.user_id]:
                    # await guild_channel.send(f"{user_data.display_name} is now streaming!")
                    await guild_channel.send(embed=embed)
                self.cache.was_streamer_online[stream_data.user_id] = True
            offline_streamers.remove(stream_data.user_id)
        # logger.debug(f"Supposedly offline ")
        for user_id in offline_streamers:
            if self.cache.was_streamer_online.get(user_id, True):
                user_data = await self.api.get_user_data(user_id)
                for guild_channel in send_streamer_to[user_id]:
                    await guild_channel.send(f"{user_data.display_name} is now offline.")
                self.cache.was_streamer_online[user_id] = False

        # streamer_cache: Dict[int, discord.Embed] = dict()
        # streamer_cache: Dict[int, str] = dict()
        # for guild_id in self.cache.tracked_servers:
        #     guild_config: TwitchGuildConfig = self.storage.guilds.get(guild_id, "twitch_config")
        #     guild: discord.Guild = self.bot.get_guild(guild_id)
        #     for twitch_id in guild_config.streamers:
        #         if twitch_id not in streamer_cache:
        #             # if twitch_id not in self.id_to_name_cache:
        #                 streamer_data = await self.get_streamer_data(twitch_id)
        #                 self.id_to_name_cache[twitch_id] = streamer_data["broadcaster_name"]
        #             if stream_data := await self.get_stream_data(twitch_id):
        #                 if not self.cache.was_streamer_online.get(twitch_id, False):
        #                     streamer_cache[twitch_id] = f"{self.id_to_name_cache.get(twitch_id, twitch_id)} is now " \
        #                                                 f"streaming!"
        #                     self.cache.was_streamer_online[twitch_id] = True
        #
        #             else:
        #                 if self.cache.was_streamer_online.get(twitch_id, True):
        #                     streamer_cache[twitch_id] = f"{self.id_to_name_cache.get(twitch_id, twitch_id)} is now " \
        #                                                 f"offline."
        #                     self.cache.was_streamer_online[twitch_id] = False
        #         if twitch_id in streamer_cache and guild_config.channel_id and \
        #                 (channel := guild.get_channel(guild_config.channel_id)):
        #             await channel.send(streamer_cache[twitch_id])

    @twitch.error
    @twitch_set.error
    @twitch_enable.error
    @twitch_disable.error
    @twitch_info.error
    @twitch_add.error
    @twitch_rm.error
    async def self_error_handler(self, context: commands.Context, exception: Exception):
        await error_handler(context, exception)


def get_online_stream_embed(stream_data: TwitchStreamData, user_data: TwitchUserData) -> discord.Embed:
    embed = discord.Embed(title=f"is now playing: {stream_data.game_name}", color=0x6441A5,
                          url=f"https://www.twitch.tv/{user_data.login}")
    embed.set_author(name=user_data.display_name, icon_url=user_data.profile_image_url)
    embed.set_image(url=stream_data.thumbnail_url.format(width="128", height="128"))
    embed.timestamp = stream_data.started_at
    return embed

