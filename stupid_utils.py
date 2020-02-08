from discord.ext import commands
import traceback
import logging
import discord
import sys
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


sys.excepthook = log_exception_handler


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


def toggle_feature(arg: str, feature_name: str, enable_phrases: set, disable_phrases: set, enabled_var: bool):
    if arg:
        if any(x in arg.lower() for x in enable_phrases):
            if enabled_var:
                return True, "{} is already enabled.".format(feature_name)
            else:
                return True, "{} enabled.".format(feature_name)
        elif any(x in arg.lower() for x in disable_phrases):
            if enabled_var:
                return False, "{} disabled.".format(feature_name)
            else:
                return False, "{} is already disabled.".format(feature_name)
        else:
            return enabled_var, "Argument `{}` is invalid for feature `{}`.".format(arg, feature_name)
    else:
        return enabled_var, "You need to actually say something after `;{}`, like enable or disable.".format(feature_name.lower())
