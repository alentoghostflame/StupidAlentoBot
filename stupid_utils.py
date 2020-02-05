from discord.ext import commands
import discord
import re


ENABLE_PHRASES: set = {"true", "on", "enable", "online"}
DISABLE_PHRASES: set = {"false", "off", "disable", "offline"}


class DataSync:
    def __init__(self, parent, bot: commands.Bot):
        self.parent = parent
        self.bot = bot

        self.messages_read: int = 0
        self.messages_sent: int = 0

        # self.callout_delete_enable: dict = dict()


def default_config_file() -> dict:
    output = dict()

    output["token"] = ""

    return output


def default_server_data():
    output = dict()
    output["messages_read_total"] = 0
    output["messages_sent_total"] = 0

    # noinspection SpellCheckingInspection
    output["callout_delete_enabled"] = True

    output["warn_roles"] = set()
    output["warn_role"] = 0
    output["mute_roles"] = set()
    output["mute_role"] = 0

    output["warned_users"]: set = set()  # (user_id, datetime)
    output["muted_users"]: set = set()  # (user_id, datetime)

    return output


def get_user_from_mention(guild: discord.Guild, mention: str):
    member_id = get_id_from_mention(mention)
    member = guild.get_member(member_id)
    return member


def get_id_from_mention(mention: str) -> int:
    numbers = re.compile('\\d+(?:\\.\\d+)?')
    if bool(re.search('\\d', mention)):
        return int(numbers.findall(mention)[0])


def rm_id_from_bot_data(bot_data: dict, guild_id: int, user_id: int, bot_data_section):
    set_copy: set = bot_data[guild_id][bot_data_section].copy()
    for user_date in bot_data[guild_id][bot_data_section]:
        if user_date[0] == user_id:
            set_copy.remove(user_date)
            print("Removed user ID {} from bot data.".format(user_date[0]))
