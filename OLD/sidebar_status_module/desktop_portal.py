from OLD.storage_module.ram_storage import RAMStorage
from discord.ext import commands
import OLD.universal_module.utils
import urllib.request
import urllib.error
import logging
# import discord
import json
# import sys


DP_GUILD_ID: int = 633487238784876573
CURRENT_USERS_ID: int = 685959963641643009
CURRENT_USERS_URL: str = "http://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid=1178460"


logger = logging.getLogger("Main")
# sys.excepthook = universal_module.utils.log_exception_handler


async def desktop_portal_sidebars(bot: commands.Bot, ram_storage: RAMStorage):
    guild = bot.get_guild(DP_GUILD_ID)
    if guild:
        current_user_category = OLD.universal_module.utils.get_category(guild, CURRENT_USERS_ID)
        try:
            url = urllib.request.urlopen(CURRENT_USERS_URL)
            data: dict = json.loads(url.read().decode())
            response: dict = data.get("response", dict())
            player_count = response.get("player_count")
            url.close()
        except urllib.error.HTTPError:
            player_count = None

        if player_count != ram_storage.dp_last_user_count:
            ram_storage.dp_last_user_count = player_count
            if player_count is None:
                await current_user_category.edit(name="Current Users - N/A")
            else:
                await current_user_category.edit(name="Current Users - {}".format(player_count))
            logger.debug("New DP user count: \"{}\"".format(player_count))
    # logger.debug("Ran DP Sidebars loop. {}".format(player_count))

