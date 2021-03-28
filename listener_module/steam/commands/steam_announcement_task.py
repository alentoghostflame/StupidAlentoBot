from listener_module.steam.steam_announcement_data import SteamAnnouncementConfig, SteamAnnouncementCache
# from misc_module.steam_announcements.commands import text
from alento_bot import StorageManager
from discord.ext import commands
from datetime import datetime
from aiohttp import ClientSession
import logging
import discord
# import requests
from json.decoder import JSONDecodeError

# import typing
# import re


logger = logging.getLogger("main_bot")


# All of this is probably bad and probably should be rewritten. TOO BAD.
# But seriously, I/somebody needs to rewrite this.


BASE_STEAM_GET_NEWS_FOR_APP = "http://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid={}&count=1&maxlength=200&format=json"


async def announcement_checker(bot: commands.Bot, storage: StorageManager, steam_cache: SteamAnnouncementCache,
                               session: ClientSession):
    # guild_ids = disk_storage.get_guild_ids()
    # for guild_id in guild_ids:
    #     guild_data = disk_storage.get_server(guild_id)
    #     guild = bot.get_guild(guild_id)
    #     if guild and guild_data.steam_announcement_channel_id != 0 and guild_data.steam_announcement_games:
    #         channel = guild.get_channel(guild_data.steam_announcement_channel_id)
    #         if channel:
    #             for game_id in guild_data.steam_announcement_games:
    #                 await process_server_game(guild_data, channel, game_id)

    for guild_id in steam_cache.tracked_guilds:
        # logger.info(f"Checking guild {guild_id}")
        steam_config: SteamAnnouncementConfig = storage.guilds.get(guild_id, "steam_announcement_config")
        guild: discord.Guild = bot.get_guild(guild_id)
        if steam_config.enabled and guild and steam_config.announcement_channel_id and steam_config.tracked_game_ids:
            # logger.info(f"Enabled, Channel kinda set, and there are tracked game IDs")
            channel = guild.get_channel(steam_config.announcement_channel_id)
            if channel:
                # logger.info("Channel exists!")
                for game_id in steam_config.tracked_game_ids.copy():
                    if not steam_config.previous_announcement_ids.get(game_id, None):
                        # logger.warning("Previous announcement IDs didn't exist, creating.")
                        steam_config.previous_announcement_ids[game_id] = set()
                    await process_server_game(steam_config, session, channel, game_id)


# async def process_server_game(guild_data: DiskServerData, channel: discord.TextChannel, game_id: int):
async def process_server_game(steam_config: SteamAnnouncementConfig, session: ClientSession,
                              channel: discord.TextChannel, game_id: int):
    # logger.info("RUNNING PROCESS SERVER GAME")
    # url = urllib.request.urlopen(BASE_STEAM_GET_NEWS_FOR_APP.format(game_id))
    # request = requests.get(BASE_STEAM_GET_NEWS_FOR_APP.format(game_id))
    response = await session.get(BASE_STEAM_GET_NEWS_FOR_APP.format(game_id))
    # full_data = json.loads(url.read().decode())
    try:
        # raw_json_data = request.json()
        raw_json_data = await response.json()
    except JSONDecodeError:
        raw_json_data = None
    # request.close()
    response.close()
    # if full_data and full_data.get("appnews", None) and full_data["appnews"].get("newsitems", None) and \
    #         len(full_data["appnews"]["newsitems"]) > 0:
    if raw_json_data and len(raw_json_data.get("appnews", dict()).get("newsitems", list())) > 0:
        # logger.info("Raw json data exists, and it has appnews/newsitems with itemcount greater than 0")
        # data = full_data["appnews"]["newsitems"][0]
        data = raw_json_data["appnews"]["newsitems"][0]
        # past_announce_ids = guild_data.get_steam_announcement_past_ids(game_id)
        # if data.get("gid", None) and int(data["gid"]) not in past_announce_ids:
        if data.get("gid", None).isdecimal() and int(data["gid"]) not in steam_config.previous_announcement_ids[game_id]:
            # logger.info("GID is decimal and isn't in the previous announcement IDs")
            # logger.debug("Actually processing game announcement. Game ID: {}  Announcement ID: {}".format(game_id,
            #                                                                                               data["gid"]))
            # logger.debug("Adding announcement ID {} to storage.".format(data["gid"]))
            steam_config.previous_announcement_ids[game_id].add(int(data["gid"]))
            # past_announce_ids.add(int(data["gid"]))
            # logger.debug("Added!")
            # await channel.send(embed=data_embed_creator(data))
            await channel.send(embed=await data_embed_creator(session, data))
    else:
        await channel.send(f"Couldn't get announcement data for ID `{game_id}`, does it actually exist?")


async def data_embed_creator(session: ClientSession, data: dict) -> discord.Embed:
    # announcement_url = urllib.request.urlopen(data["url"])
    # announcement_url = requests.get(data["url"])
    response = await session.get(data["url"])
    # announcement_data = announcement_url.read().decode()\

    # announcement_data = announcement_url.text
    announcement_data = await response.text()
    found_image = None
    for stuff in announcement_data.split("\n"):
        stripped_text = stuff.strip()
        if "meta" in stripped_text:
            meta_tag = meta_reader(stripped_text)
            if meta_tag.get("property", None) == "og:image":
                found_image = meta_reader(stripped_text).get("content", None)
                # logger.debug("Found image for game.")
    # return announcement_embed_creator(data, announcement_url.url, found_image)
    return announcement_embed_creator(data, str(response.url), found_image)


def meta_reader(given_text):
    split_text = given_text[1:-1].split(" ")
    output = dict()
    for bit in split_text:
        if bit[:5] == "name=":
            output["name"] = bit[5:].strip("\"")
        elif bit[:9] == "property=":
            output["property"] = bit[9:].strip("\"")
        elif bit[:8] == "content=":
            output["content"] = bit[8:].strip("\"")
    return output


def announcement_embed_creator(announcement_data: dict, website_url: str, image_url: str) -> discord.Embed:
    embed = discord.Embed(title=announcement_data.get("title", "YOU SHOULD NOT ENCOUNTER THIS, YELL AT ALENTO"),
                          color=0xffff00)

    embed.add_field(name="Preview",
                    value=announcement_data.get("contents", "YOU SHOULD NOT SEE THIS, YELL AT ALENTO")[:998],
                    inline=False)
    logger.debug(f"URL {image_url}")
    embed.add_field(name="URL", value=website_url, inline=False)
    if image_url:
        embed.set_image(url=image_url)
    embed.timestamp = datetime.utcfromtimestamp(announcement_data.get("date", 0))

    return embed
