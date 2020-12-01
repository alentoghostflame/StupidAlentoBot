from alento_bot.storage_module import StorageManager
from alento_bot.core_bot.custom_help import AlentoHelpCommand
from alento_bot.external_objects.timer_manager import TimerManager
from alento_bot.external_objects import BaseModule
import warnings
from alento_bot.core_bot import text
from discord.ext import commands
from discord import Intents
from typing import Set, Type
import logging
import sys
import os


LOGGING_FORMAT = "[{asctime}][{filename}][{lineno:3}][{funcName}][{levelname}] {message}"
LOGGING_LEVEL = logging.DEBUG


def setup_logging():
    setup_logger = logging.getLogger("main_bot")
    log_format = logging.Formatter(LOGGING_FORMAT, style="{")

    os.makedirs("logs", exist_ok=True)
    log_latest_handler = logging.FileHandler("logs/Bot Latest.log", mode="w")

    log_latest_handler.setFormatter(log_format)
    log_console_handler = logging.StreamHandler(sys.stdout)
    log_console_handler.setFormatter(log_format)

    setup_logger.addHandler(log_latest_handler)
    setup_logger.addHandler(log_console_handler)

    setup_logger.setLevel(LOGGING_LEVEL)


logger = logging.getLogger("main_bot")


class StupidAlentoBot:
    def __init__(self):
        self._module_types: Set[Type[BaseModule]] = set()
        self._modules: Set[BaseModule] = set()

        self.storage: StorageManager = StorageManager()
        self.timer: TimerManager = TimerManager()
        intents = Intents.all()
        self.bot = commands.Bot(command_prefix=self.storage.config.discord_command_prefix, case_insensitive=True,
                                intents=intents, help_command=AlentoHelpCommand())
        setup_logging()
        self._legacy_module = LegacyModule(self.bot, self.storage, self.timer)
        self._modules.add(self._legacy_module)

    def add_cog(self, cog: commands.Cog):
        warnings.warn("This function will be removed.", DeprecationWarning)
        self._legacy_module.add_cog(cog)

    def add_module(self, module: Type[BaseModule]):
        if issubclass(module, BaseModule):
            self._module_types.add(module)
        else:
            logger.error(f"Given module {module.__name__} does not subclass {module.__name__}")

    def init_modules(self):
        logger.debug("Initializing modules.")
        for module in self._module_types:
            logger.debug(f"  Initializing the {module.__name__} module.")
            self._modules.add(module(self.bot, self.storage, self.timer))

    def init_cogs(self):
        logger.debug("Initializing module cogs.")
        for module in self._modules:
            logger.debug(f"  Initializing the {type(module).__name__} cogs.")
            module.init_cogs()

    def load(self):
        self.storage.load()
        for module in self._modules:
            module.load()

    def save(self):
        for module in self._modules:
            module.save()
        self.storage.save()

    def run(self):
        passed_checks = True
        if not self.storage.config.discord_bot_token:
            logger.critical(text.MISSING_DISCORD_TOKEN)
            passed_checks = False

        if self.storage.config.discord_command_prefix != ";":
            self.bot.command_prefix = self.storage.config.discord_command_prefix
            logger.debug(f"Command prefix \"{self.bot.command_prefix}\" set!")

        if passed_checks:
            logger.info("Beginning bot loop.")
            self.bot.run(self.storage.config.discord_bot_token)


class LegacyModule(BaseModule):
    pass
