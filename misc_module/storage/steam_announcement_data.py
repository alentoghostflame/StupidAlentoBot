from alento_bot import guild_data_transformer, cache_transformer
import logging
import typing


logger = logging.getLogger("main_bot")


@cache_transformer(name="steam_announcement_cache")
class SteamAnnouncementCache:
    def __init__(self):
        self.tracked_guilds: typing.Set[int] = set()


@guild_data_transformer(name="steam_announcement_config")
class SteamAnnouncementConfig:
    def __init__(self):
        self.enabled: bool = False
        self.tracked_game_ids: typing.Set[int] = set()
        self.previous_announcement_ids: typing.Dict[int, typing.Set[int]] = dict()
        self.announcement_channel_id: int = 0
