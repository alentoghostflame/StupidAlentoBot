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
# moderation = ModeratorModule(discord_bot)
# faq = FAQModule(discord_bot)
# eve = EVEModule(discord_bot)

try:
    discord_bot.add_module(CoreModule)
    # discord_bot.add_module(Misc2Module)
    # discord_bot.add_module(SelfRoleModule)
    # faq.register_cogs()
    # eve.register_cogs(discord_bot)
    # moderation.register_cogs()

    discord_bot.init_modules()
    discord_bot.init_cogs()

    discord_bot.load()
    # eve.load()
    # moderation.load()

    discord_bot.run()
except Exception as e:
    logger.critical("SOMETHING TERRIBLE HAPPENED:")
    logger.exception(e)
    raise e
finally:
    # moderation.save()
    # eve.save()
    discord_bot.save()
