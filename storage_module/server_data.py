from discord.ext import commands
from datetime import datetime
import logging
import typing


logger = logging.getLogger("Main")


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
        self.welcome_messages: typing.List[str] = list()
        self.welcome_channel_id: int = 0

        self.steam_announcement_games: typing.Set[int] = set()
        self._steam_announcement_past_ids: typing.Dict[int, typing.Set[int]] = dict()
        self.steam_announcement_channel_id: int = 0

        self.member_karma: typing.Dict[int] = dict()

    def __setstate__(self, state: dict):
        self.__dict__ = state
        self.faq_edit_roles = state.get("faq_edit_roles", set())

        self.steam_announcement_games = state.get("steam_announcement_games", set())
        self._steam_announcement_past_ids = state.get("_steam_announcement_past_ids", dict())
        self.steam_announcement_channel_id = state.get("steam_announcement_channel_id", 0)

        self.steam_announcement_past_ids = None
        self.steam_announcement_last_id = None

        self.member_karma = state.get("member_karma", dict())

    def get_steam_announcement_past_ids(self, game_id: int):
        if game_id not in self._steam_announcement_past_ids:
            self._steam_announcement_past_ids[game_id] = set()
            logger.debug("Created set for game ID of {}".format(game_id))
        return self._steam_announcement_past_ids[game_id]


def get_all_server_names(server_storage: typing.Dict[int, DiskServerData], bot: commands.Bot) -> dict:
    output = dict()
    for server_id in server_storage:
        server = bot.get_guild(server_id)
        if server:
            output[server_id] = server.name
        else:
            output[server_id] = "NOT IN SERVER"
    return output
