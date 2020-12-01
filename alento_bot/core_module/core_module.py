from alento_bot.core_module.core_cog import CoreCog
from alento_bot.external_objects import BaseModule


class CoreModule(BaseModule):
    def __init__(self, *args):
        BaseModule.__init__(self, *args)
        self.add_cog(CoreCog(self.storage, self.timer))
