from misc2_module.activity_cog import ActivityCog
from misc2_module.callouts import CalloutCog
from alento_bot import BaseModule
import logging

logger = logging.getLogger("main_bot")


class MiscModule(BaseModule):
    def __init__(self, *args):
        BaseModule.__init__(self, *args)
        self.add_cog(ActivityCog(self.bot))
        self.add_cog(CalloutCog(self.storage))
