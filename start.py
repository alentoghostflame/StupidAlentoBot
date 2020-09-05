from alento_bot import StupidAlentoBot, CoreModule
# from moderation_module import ModeratorModule
# from faq_module import FAQModule
# from misc_module import MiscModule
# from self_roles_module import SelfRoleModule
# from misc2_module import MiscModule as Misc2Module
# from eve_module import EVEModule
import logging


logger = logging.getLogger("main_bot")


discord_bot = StupidAlentoBot()

try:
    discord_bot.add_module(CoreModule)
    # discord_bot.add_module(ModeratorModule)
    # discord_bot.add_module(FAQModule)
    # discord_bot.add_module(SelfRoleModule)
    # discord_bot.add_module(Misc2Module)
    # discord_bot.add_module(EVEModule)

    discord_bot.init_modules()
    discord_bot.init_cogs()

    discord_bot.load()

    discord_bot.run()
except Exception as e:
    logger.critical("SOMETHING TERRIBLE HAPPENED:")
    logger.exception(e)
    raise e
finally:
    discord_bot.save()
