from alento_bot.storage_module import StorageManager
from alento_bot.external_objects import BaseModule
from discord.ext import commands
from alento_bot.core_module import text
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
        self.bot = commands.Bot(command_prefix=self.storage.config.discord_command_prefix, case_insensitive=True)

    def add_module(self, module: Type[BaseModule]):
        self._module_types.add(module)

    def init_modules(self):
        for module in self._module_types:
            self._modules.add(module(self.bot, self.storage))

    def init_cogs(self):
        for module in self._modules:
            module.init_cogs()

    def load(self):
        for module in self._modules:
            module.load()

    def save(self):
        for module in self._modules:
            module.save()

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


# class DiscordBot:
#     def __init__(self):
#         self.storage: StorageManager = StorageManager()
#         self.bot = commands.Bot(command_prefix=self.storage.config.discord_command_prefix, case_insensitive=True)
#         setup_logging()
#
#     def add_cog(self, cog: commands.Cog):
#         self.bot.add_cog(cog)
#
#     def save(self):
#         self.storage.save()
#
#     def load(self):
#         self.storage.load()
#
#     def run(self):
#         passed_checks = True
#         if not self.storage.config.discord_bot_token:
#             logger.critical(text.MISSING_DISCORD_TOKEN)
#             passed_checks = False
#
#         if self.storage.config.discord_command_prefix != ";":
#             self.bot.command_prefix = self.storage.config.discord_command_prefix
#             logger.debug(f"Command prefix \"{self.bot.command_prefix}\" set!")
#
#         if passed_checks:
#             logger.info("Beginning bot loop.")
#             self.bot.run(self.storage.config.discord_bot_token)
