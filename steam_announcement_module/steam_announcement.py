from steam_announcement_module.background_task import announcement_checker
from steam_announcement_module.admin import steam_announcement_admin
from storage_module.disk_storage import DiskStorage
from discord.ext import commands, tasks
import universal_module.utils
# import discord
import logging
import sys


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


# import discord, urllib.request, json, datetime
#
# def meta_reader(given_text):
#     split_text = given_text[1:-1].split(" ")
#     output = dict()
#     for bit in split_text:
#         if "name=" in bit[:5]:
#             output["name"] = bit[5:].strip("\"")
#         elif "property=" in bit[:9]:
#             output["property"] = bit[9:].strip("\"")
#         elif "content=" in bit[:8]:
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
# If Meta and property="og:image"
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

