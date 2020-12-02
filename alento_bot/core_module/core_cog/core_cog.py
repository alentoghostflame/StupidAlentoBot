from alento_bot.storage_module import StorageManager
from alento_bot.external_objects.timer_manager import TimerManager
from discord.ext import commands, tasks
from alento_bot.core_module.core_cog import text
import logging
import random


logger = logging.getLogger("main_bot")


class CoreCog(commands.Cog, name="Core"):
    def __init__(self, storage: StorageManager, timer: TimerManager):
        self.storage = storage
        self.timer = timer
        self._first_save = True

    @commands.Cog.listener()
    async def on_ready(self):
        logger.debug("Starting core background.")
        if not self.auto_save.is_running():
            self.auto_save.start()
        if not self.timer_tick.is_running():
            self.timer_tick.start()

    def cog_unload(self):
        self.auto_save.cancel()
        self.timer_tick.cancel()

    @commands.command(name="patreon", brief="Posts the Patreon link.")
    async def patreon(self, context: commands.Context):
        patreon_link = "https://www.patreon.com/AlentoGhostflame"
        await context.send(random.sample(text.PATREON_MESSAGES, 1)[0].format(patreon_link))

    @commands.command(name="invite", brief="Posts the bot invite link.")
    async def invite(self, context: commands.Context):
        config = self.storage.config
        if config.bot_invite_link:
            await context.send(config.bot_invite_link)
        else:
            await context.send("Bot owner hasn't set the `bot_invite_link` in the config. Go bug them, not me.")

    @tasks.loop(minutes=1)
    async def timer_tick(self):
        await self.timer.tick()

    @tasks.loop(hours=1)
    async def auto_save(self):
        if self._first_save:
            self._first_save = False
        else:
            self.storage.save()
