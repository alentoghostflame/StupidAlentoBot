from alento_bot.storage_module import StorageManager
from alento_bot.external_objects.timer_manager import TimerManager
from discord.ext import commands
from typing import Set


class BaseModule:
    def __init__(self, bot: commands.Bot, storage: StorageManager, timer: TimerManager):
        self._cogs_to_add: Set[commands.Cog] = set()
        self.bot: commands.Bot = bot
        self.storage: StorageManager = storage
        self.timer: TimerManager = timer

    def add_cog(self, cog: commands.Cog):
        self._cogs_to_add.add(cog)

    def init_cogs(self):
        for cog in self._cogs_to_add:
            self.bot.add_cog(cog)

    def load(self):
        pass

    def save(self):
        pass
