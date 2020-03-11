from storage_module.server_data import DiskServerData
from storage_module.disk_storage import DiskStorage
from discord.ext import commands
from datetime import datetime
import universal_module.utils
import universal_module.text
import urllib.request
import logging
import discord
import json


BASE_STEAM_GET_NEWS_FOR_APP = "http://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/?appid={}&count=1&maxlength=200&format=json"


logger = logging.getLogger("Main")

# async def announcement_checker(bot: commands.Bot, disk_storage: DiskStorage):
#     guild_ids = disk_storage.get_guild_ids()
#     for guild_id in guild_ids:
#         guild_data = disk_storage.get_server(guild_id)
#         guild = bot.get_guild(guild_id)
#         if guild and guild_data.steam_announcement_channel_id != 0 and guild_data.steam_announcement_games:
#             channel = guild.get_channel(guild_data.steam_announcement_channel_id)
#             if channel:
#                 for game_id in guild_data.steam_announcement_games:
#                     url = urllib.request.urlopen(BASE_STEAM_GET_NEWS_FOR_APP.format(game_id))
#                     full_data = json.loads(url.read().decode())
#                     if full_data:
#                         data = full_data["appnews"]["newsitems"][0]
#                         if data["gid"] != guild_data.steam_announcement_last_id.get(game_id, 0):
#                             guild_data.steam_announcement_last_id[game_id] = data["gid"]
#                             announcement_url = urllib.request.urlopen(data["url"])
#                             announcement_data = announcement_url.read().decode()
#                             found_image = None
#                             for stuff in announcement_data.split("\n"):
#                                 text = stuff.strip()
#                                 if "meta" in text:
#                                     meta_tag = meta_reader(text)
#                                     if meta_tag.get("property", None) == "og:image":
#                                         found_image = meta_reader(text).get("content", None)
#                             embed = announcement_embed_creator(data, announcement_url.url, found_image)
#                             channel.send(embed=embed)


# async def announcement_checker(bot: commands.Bot, disk_storage: DiskStorage):
#     guild_ids = disk_storage.get_guild_ids()
#     for guild_id in guild_ids:
#         guild_data = disk_storage.get_server(guild_id)
#         guild = bot.get_guild(guild_id)
#         if guild and guild_data.steam_announcement_channel_id != 0 and guild_data.steam_announcement_games:
#             channel = guild.get_channel(guild_data.steam_announcement_channel_id)
#             if channel:
#                 for game_id in guild_data.steam_announcement_games:
#                     url = urllib.request.urlopen(BASE_STEAM_GET_NEWS_FOR_APP.format(game_id))
#                     full_data = json.loads(url.read().decode())
#                     if full_data:
#                         data = full_data["appnews"]["newsitems"][0]
#                         if data["gid"] != guild_data.steam_announcement_last_id.get(game_id, 0):
#                             guild_data.steam_announcement_last_id[game_id] = data["gid"]
#                             embed = data_embed_creator(data)
#                             channel.send(embed=embed)


async def announcement_checker(bot: commands.Bot, disk_storage: DiskStorage):
    guild_ids = disk_storage.get_guild_ids()
    for guild_id in guild_ids:
        guild_data = disk_storage.get_server(guild_id)
        guild = bot.get_guild(guild_id)
        if guild and guild_data.steam_announcement_channel_id != 0 and guild_data.steam_announcement_games:
            channel = guild.get_channel(guild_data.steam_announcement_channel_id)
            if channel:
                for game_id in guild_data.steam_announcement_games:
                    await process_server_game(guild_data, channel, game_id)


async def process_server_game(guild_data: DiskServerData, channel: discord.TextChannel, game_id: int):
    url = urllib.request.urlopen(BASE_STEAM_GET_NEWS_FOR_APP.format(game_id))
    full_data = json.loads(url.read().decode())
    if full_data and full_data.get("appnews", None) and full_data["appnews"].get("newsitems", None) and \
            len(full_data["appnews"]["newsitems"]) > 0:
        data = full_data["appnews"]["newsitems"][0]
        if data.get("gid", 0) != 0 and data["gid"] != guild_data.steam_announcement_last_id.get(game_id, 0):
            logger.debug("Actually processing the game.")
            guild_data.steam_announcement_last_id[game_id] = data["gid"]
            await channel.send(embed=data_embed_creator(data))


def data_embed_creator(data: dict) -> discord.Embed:
    announcement_url = urllib.request.urlopen(data["url"])
    announcement_data = announcement_url.read().decode()

    found_image = None
    for stuff in announcement_data.split("\n"):
        stripped_text = stuff.strip()
        if "meta" in stripped_text:
            meta_tag = meta_reader(stripped_text)
            if meta_tag.get("property", None) == "og:image":
                found_image = meta_reader(stripped_text).get("content", None)
                logger.debug("Found image for game.")
    return announcement_embed_creator(data, announcement_url.url, found_image)


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


def announcement_embed_creator(announcement_data: dict, webiste_url: str, image_url: str) -> discord.Embed:
    embed = discord.Embed(title=announcement_data.get("title", universal_module.text.SHOULD_NOT_ENCOUNTER_THIS),
                          color=0xffff00)

    embed.add_field(name="Preview", value=announcement_data.get("contents",
                                                                universal_module.text.SHOULD_NOT_ENCOUNTER_THIS),
                    inline=False)
    embed.add_field(name="URL", value=webiste_url, inline=False)
    embed.set_image(url=image_url)
    embed.timestamp = datetime.utcfromtimestamp(announcement_data.get("date", 0))

    return embed


# import discord, urllib.request, json, datetime
#
# def meta_reader(given_text):
#     split_text = given_text[1:-1].split(" ")
#     output = dict()
#     for bit in split_text:
#         if bit[:5] == "name=":
#             output["name"] = bit[5:].strip("\"")
#         elif bit[:9] == "property=":
#             output["property"] = bit[9:].strip("\"")
#         elif bit[:8] == "content=":
#             output["content"] = bit[8:].strip("\"")
#     return output
#
# url = urllib.request.urlopen("http://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/?appid=1178460&count=3&maxlength=200&format=json")
# full_data = json.loads(url.read().decode())
# data = full_data["appnews"]["newsitems"][0]
#
# announcement_url = urllib.request.urlopen(data["url"])
# announcement_data = announcement_url.read().decode()
# found_image = None
# for stuff in announcement_data.split("\n"):
#     text = stuff.strip()
#     if "meta" in text:
# # If Meta and property="og:image"
#         found_image = meta_reader(text).get("content", None)
#
# embed = discord.Embed(title=data["title"], color=0xffff00)
#
# embed.add_field(name="Preview", value=data["contents"], inline=False)
# embed.add_field(name="URL", value=announcement_url.url, inline=False)
# embed.set_image(url=found_image)
# embed.timestamp = datetime.datetime.utcfromtimestamp(data["date"])
#
# await context.send(embed=embed)
