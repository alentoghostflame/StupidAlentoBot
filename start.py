from alento_bot import StupidAlentoBot, CoreModule
from devtool_module import DevToolModule
from example_module import ExampleModule
# from timekeeper_module import TimekeeperModule
# from moderation_module import ModerationModule
# from eve_module import EVEModule
# from faq_module import FAQModule
# from misc_module import MiscModule
# from misc2_module import MiscModule as Misc2Module
# from self_roles_module import SelfRoleModule
# from mmo_module import MMOModule
# from mudaemod_module import MudaeModModule
# from battle_module import BattleModule
# from listener_module import ListenerModule
# from dnd_module import DnDModule


import logging


logger = logging.getLogger("main_bot")


discord_bot = StupidAlentoBot()
logger.setLevel(logging.DEBUG)

try:
    discord_bot.add_module(CoreModule)
    discord_bot.add_module(DevToolModule)
    discord_bot.add_module(ExampleModule)
    # discord_bot.add_module(TimekeeperModule)
    # discord_bot.add_module(ModerationModule)
    # discord_bot.add_module(EVEModule)
    # discord_bot.add_module(FAQModule)
    # discord_bot.add_module(MiscModule)
    # discord_bot.add_module(Misc2Module)
    # discord_bot.add_module(SelfRoleModule)
    # discord_bot.add_module(MMOModule)
    # discord_bot.add_module(MudaeModModule)
    # discord_bot.add_module(BattleModule)
    # discord_bot.add_module(ListenerModule)
    # discord_bot.add_module(DnDModule)

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
