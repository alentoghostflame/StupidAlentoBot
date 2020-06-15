from moderation_module.punishment import PunishmentCog, WordBanCog
from moderation_module.guild_logging import GuildLoggingCog
from moderation_module.storage import PunishmentManager
from alento_bot import DiscordBot
import logging


logger = logging.getLogger("main_bot")


class ModeratorModule:
    def __init__(self, discord_bot: DiscordBot):
        self.discord_bot: DiscordBot = discord_bot
        self.punish_manager: PunishmentManager = PunishmentManager(self.discord_bot.storage)

    def register_cogs(self):
        logger.info("Registering cogs for Moderation.")
        self.discord_bot.add_cog(PunishmentCog(self.discord_bot.storage, self.punish_manager, self.discord_bot.bot))
        self.discord_bot.add_cog(WordBanCog(self.discord_bot.storage, self.punish_manager, self.discord_bot.bot))
        self.discord_bot.add_cog(GuildLoggingCog(self.discord_bot.storage))

    def load(self):
        pass

    def save(self):
        pass
