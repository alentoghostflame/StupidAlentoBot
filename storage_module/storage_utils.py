from discord.ext import commands
from datetime import datetime
import typing


class DiskServerData:
    def __init__(self):
        self.callout_delete_enabled: bool = False

        self.faq_enabled: bool = True
        self.faq_phrases: typing.Dict[str, str] = dict()
        self.faq_edit_roles: typing.Set[int] = set()

        self.warn_role_id: int = 0
        self.warner_roles: typing.Set[int] = set()
        self.warned_users: typing.Set[typing.Tuple[int, datetime]] = set()
        self.mute_role_id: int = 0
        self.muter_roles: typing.Set[int] = set()
        self.muted_users: typing.Set[typing.Tuple[int, datetime]] = set()

        self.welcome_enabled: bool = False
        self.welcome_channel_id: int = 0
        self.welcome_messages: typing.List[str] = list()


def get_all_server_names(server_storage: typing.Dict[int, DiskServerData], bot: commands.Bot) -> dict:
    output = dict()
    for server_id in server_storage:
        server = bot.get_guild(server_id)
        if server:
            output[server_id] = server.name
        else:
            output[server_id] = "NOT IN SERVER"
    return output



