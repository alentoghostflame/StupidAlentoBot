from discord.ext import commands
from datetime import datetime
import urllib.request
import traceback
import logging
import discord
import typing
# import sys
import re


ENABLE_PHRASES: set = {"true", "on", "enable", "online"}
DISABLE_PHRASES: set = {"false", "off", "disable", "offline"}


logger = logging.getLogger("Main")


def log_exception_handler(error_type, value, tb):
    # TODO: Unify logging errors.
    the_logger = logging.getLogger("Main")
    the_logger.critical("Uncaught exception:\n"
                        "Type: {}\n"
                        "Value: {}\n"
                        "Traceback:\n {}".format(str(error_type), str(value), "".join(traceback.format_tb(tb))))


# sys.excepthook = log_exception_handler


class DataSync:
    def __init__(self, parent, bot: commands.Bot):
        self.parent = parent
        self.bot = bot

        self.messages_read: int = 0
        self.messages_sent: int = 0

        # self.callout_delete_enable: dict = dict()


class StoredServerData:
    def __init__(self):
        self.callout_delete_enabled: bool = False

        self.info_braces_enabled: bool = True

        self.warn_role_id: int = 0
        self.warner_roles: typing.Set[int] = set()
        self.warned_users: typing.Set[typing.Tuple[int, datetime]] = set()
        self.mute_role_id: int = 0
        self.muter_roles: typing.Set[int] = set()
        self.muted_users: typing.Set[typing.Tuple[int, datetime]] = set()


def get_numbers_legacy(string: str) -> typing.List[str]:
    comp = re.compile("(\\d+)")
    return comp.findall(string)


def get_numbers(string: str):
    if string:
        comp = re.compile("(\\d+)")
        num_list = comp.findall(string)

        if num_list:
            return int("".join(num_list))
    return None


def default_config_file() -> dict:
    output = dict()

    output["token"] = ""

    return output


def has_any_role(guild: discord.Guild, given_roles: set, member: discord.Member) -> bool:
    for role in given_roles:
        for user_role in member.roles:
            if guild.get_role(role) == user_role:
                return True
    return False


def default_server_data():
    output = dict()
    output["messages_read_total"] = 0
    output["messages_sent_total"] = 0

    # noinspection SpellCheckingInspection
    output["callout_delete_enabled"]: bool = True
    output["info_braces_enabled"]: bool = False

    output["warn_roles"] = set()
    output["warn_role"] = 0
    output["mute_roles"] = set()
    output["mute_role"] = 0

    output["warned_users"]: set = set()  # (user_id, datetime)
    output["muted_users"]: set = set()  # (user_id, datetime)

    output["info"]: dict = dict()

    return output


def get_user_from_mention(guild: discord.Guild, mention: str):
    # member_id = get_id_from_mention(mention)
    # member = guild.get_member(member_id)
    # return member
    member_id = get_numbers(mention)
    if member_id:
        return guild.get_member(member_id)
    else:
        return None


def get_role_from_mention(guild: discord.Guild, mention: str) -> typing.Optional[discord.Role]:
    role_id = get_numbers(mention)
    if role_id:
        return guild.get_role(role_id)
    else:
        return None


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


async def safe_fetch_user(bot: commands.Bot, user_id: int):
    try:
        return await bot.fetch_user(user_id)
    except discord.NotFound:
        return None


def toggle_feature(arg: str, feature_name: str, enable_phrases: set, disable_phrases: set, enabled_var: bool):
    if arg:
        if any(x in arg.lower() for x in enable_phrases):
            if enabled_var:
                return True, "`{}` is already enabled.".format(feature_name)
            else:
                return True, "`{}` enabled.".format(feature_name)
        elif any(x in arg.lower() for x in disable_phrases):
            if enabled_var:
                return False, "`{}` disabled.".format(feature_name)
            else:
                return False, "`{}` is already disabled.".format(feature_name)
        else:
            return enabled_var, "Argument `{}` is not a valid on/off for feature `{}`.".format(arg, feature_name)
    else:
        return enabled_var, "You need to actually say something after the command, like enable or disable."


def get_category(guild: discord.Guild, category_id: int) -> discord.CategoryChannel:
    categories = guild.categories
    found = None
    for catagory in categories:
        if catagory.id == category_id:
            found = catagory
    return found


def is_image_url(image_url: str) -> bool:
    image_formats = {".png", ".jpeg", ".jpg"}
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"
    if str_contains_element(image_url[-5:], image_formats):
        try:
            image_request = urllib.request.Request(image_url, data=None, headers={"User-Agent": user_agent})
            urllib.request.urlopen(image_request)
            return True
            # If this is able to complete, then the file ends with an image format and is a reachable URL.
        except Exception:
            return False
    else:
        return False


def str_contains_element(string: str, substring_list: typing.Iterable) -> bool:
    for substring in substring_list:
        if substring in string:
            return True
    return False


def find_mentions(guild: discord.Guild, input_string: str) -> typing.List[int]:
    if input_string:
        extended_comp = re.compile("<@!?(\\d+)>")
        raw_mentions = extended_comp.findall(input_string)
        output = []
        for raw in raw_mentions:
            member_id = int(raw)
            if guild.get_member(member_id):
                output.append(member_id)
        return output
    return []
