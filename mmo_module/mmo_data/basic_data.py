from alento_bot import guild_data_transformer, user_data_transformer, cache_transformer
from typing import Set


@cache_transformer(name="basic_mmo_data")
class BasicMMODataStorage:
    def __init__(self):
        self.enabled_users: Set[int] = set()
        self.enabled_guilds: Set[int] = set()


@guild_data_transformer(name="mmo_config")
class GuildMMOConfig:
    def __init__(self):
        self.enabled: bool = False


@user_data_transformer(name="mmo_config")
class UserMMOConfig:
    def __init__(self):
        self.enabled: bool = False
