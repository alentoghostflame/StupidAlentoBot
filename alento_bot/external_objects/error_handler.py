from alento_bot.external_objects import universal_text
from discord.ext import commands
import logging


logger = logging.getLogger("main_bot")


async def error_handler(context: commands.Context, exception: Exception, raise_exception: bool = True) -> bool:
    if isinstance(exception, commands.MissingPermissions):
        await context.send(universal_text.ERROR_MISSING_PERMISSION)
        return True
    elif isinstance(exception, commands.MissingRequiredArgument):
        await context.send_help(context.command)
        return True
    elif isinstance(exception, commands.NotOwner):
        await context.send("You are not the owner.")
    elif raise_exception:
        await context.send(f"Critical error occurred, {type(exception)} {exception}")
        logger.error(f"Critical error occurred, {type(exception)} {exception}")
        raise exception
    else:
        return False

