from moderation_module.punishment import PunishmentCog, WordBanCog
from moderation_module.guild_logging import GuildLoggingCog
from moderation_module.storage import PunishmentManager
from alento_bot import BaseModule
import logging


logger = logging.getLogger("main_bot")


class ModeratorModule(BaseModule):
    def __init__(self, *args):
        BaseModule.__init__(self, *args)
        self.punish_manager: PunishmentManager = PunishmentManager(self.storage)
        self.add_cog(PunishmentCog(self.storage, self.punish_manager, self.bot))
        self.add_cog(WordBanCog(self.storage, self.punish_manager, self.bot))
        self.add_cog(GuildLoggingCog(self.storage))
