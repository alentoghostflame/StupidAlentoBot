from alento_bot import guild_data_transformer
import logging
import typing


logger = logging.getLogger("main_bot")


@guild_data_transformer(name="guild_logging_config")
class GuildLoggingConfig:
    def __init__(self):
        self.toggled_on: bool = False
        self.log_channel_id: int = 0
        self.exempt_channels: typing.Set[int] = set()
        self.log_bots: bool = False

