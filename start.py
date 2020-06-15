from moderation_module import ModeratorModule
from misc_module import MiscModule
from eve_module import EVEModule
from faq_module import FAQModule
from alento_bot import DiscordBot
from alento_bot import CoreCog
import logging

logger = logging.getLogger("main_bot")


discord_bot = DiscordBot()
moderation = ModeratorModule(discord_bot)
# eve = EVEModule(discord_bot.storage)
faq = FAQModule(discord_bot)
misc = MiscModule(discord_bot)

try:
    discord_bot.add_cog(CoreCog(discord_bot.storage))

    moderation.register_cogs()
    # eve.register_cogs(discord_bot)
    faq.register_cogs()
    misc.register_cogs()

    discord_bot.load()
    moderation.load()
    # eve.load()

    discord_bot.run()
except Exception as e:
    logger.critical("SOMETHING TERRIBLE HAPPENED:")
    logger.exception(e)
    raise e
finally:
    moderation.save()
    discord_bot.save()

