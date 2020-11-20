from alento_bot import StupidAlentoBot, CoreModule
from devtool_module import DevToolModule
from example_module import ExampleModule
from coffee_module import CoffeeModule
# from moderation_module import ModeratorModule
# from eve_module import EVEModule
# from faq_module import FAQModule
# from misc_module import MiscModule
from misc2_module import MiscModule as Misc2Module
from self_roles_module import SelfRoleModule
from eval_module import EvalModule
# from mmo_module import MMOModule
# from mudaemod_module import MudaeModModule


import logging


logger = logging.getLogger("main_bot")


discord_bot = StupidAlentoBot()

try:
    discord_bot.add_module(CoreModule)
    discord_bot.add_module(DevToolModule)
    # discord_bot.add_module(ExampleModule)
    discord_bot.add_module(CoffeeModule)
    # discord_bot.add_module(ModeratorModule)
    # discord_bot.add_module(EVEModule)
    # discord_bot.add_module(FAQModule)
    # discord_bot.add_module(MiscModule)
    discord_bot.add_module(Misc2Module)
    discord_bot.add_module(SelfRoleModule)
    discord_bot.add_module(EvalModule)
    # discord_bot.add_module(MMOModule)
    # discord_bot.add_module(MudaeModModule)

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
