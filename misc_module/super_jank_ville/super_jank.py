from alento_bot import DiscordBot, StorageManager
from discord.ext import commands, tasks
from aiohttp import ClientSession, ClientError
# import requests
import logging
import discord


logger = logging.getLogger("main_bot")


DP_GUILD_ID: int = 633487238784876573
CURRENT_USERS_ID: int = 685959963641643009
CURRENT_USERS_URL: str = "http://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid=1178460"


class SidebarStatusCog(commands.Cog, name="Sidebar Status Module"):
    def __init__(self, bot: commands.Bot, session: ClientSession):
        self.bot: commands.Bot = bot
        self.last_player_count = 0
        self.session = session

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Sidebar Status cog ready.")
        self.desktop_portal_loop.start()
        game_activity = discord.Game("SiIvagunner rips")
        await self.bot.change_presence(activity=game_activity)

    def cog_unload(self):
        self.desktop_portal_loop.cancel()

    @tasks.loop(minutes=5)
    async def desktop_portal_loop(self):
        await self.desktop_portal_sidebars()

    async def desktop_portal_sidebars(self):
        guild = self.bot.get_guild(DP_GUILD_ID)
        if guild:
            current_user_category = get_category(guild, CURRENT_USERS_ID)
            try:
                # url = urllib.request.urlopen(CURRENT_USERS_URL)
                # request = requests.get(CURRENT_USERS_URL)
                request = await self.session.get(CURRENT_USERS_URL)
                # data: dict = json.loads(url.read().decode())
                data: dict = await request.json()
                response: dict = data.get("response", dict())
                player_count = response.get("player_count")
                # url.close()
                request.close()
            # except urllib.error.HTTPError:
            # except requests.exceptions.HTTPError:
            except ClientError:
                player_count = None

            if player_count != self.last_player_count:
                self.last_player_count = player_count
                if player_count is None:
                    await current_user_category.edit(name="Current Users - N/A")
                else:
                    await current_user_category.edit(name="Current Users - {}".format(player_count))
                logger.debug("New DP user count: \"{}\"".format(player_count))


def get_category(guild: discord.Guild, category_id: int) -> discord.CategoryChannel:
    categories = guild.categories
    found = None
    for category in categories:
        if category.id == category_id:
            found = category
    return found

