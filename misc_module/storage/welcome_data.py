from alento_bot import guild_data_transformer
import logging
import typing


logger = logging.getLogger("main_bot")


@guild_data_transformer(name="welcome_config")
class WelcomeConfig:
    def __init__(self):
        self.enabled: bool = False
        self.messages: typing.List[str] = list()
        self.welcome_channel_id: int = 0
