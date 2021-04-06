from alento_bot.external_objects import universal_text
from discord.ext import commands
import logging


logger = logging.getLogger("main_bot")


async def error_handler(context: commands.Context, exception: Exception, raise_exception: bool = True) -> bool:
    if isinstance(exception, commands.MissingPermissions):
        await context.send(universal_text.ERROR_MISSING_PERMISSION)
    elif isinstance(exception, commands.MissingRequiredArgument):
        await context.send_help(context.command)
    elif isinstance(exception, commands.NotOwner):
        await context.send("You are not the owner.")
    elif isinstance(exception, commands.RoleNotFound):
        await context.send("Role not found.")
    elif isinstance(exception, commands.MissingRequiredArgument):
        await context.send_help(context.command)
    elif raise_exception:
        await context.send(f"Unhandled error occurred, {type(exception)} {exception}")
        logger.error(f"Unhandled error occurred, {type(exception)} {exception}")
        raise exception
    else:
        return False
    return True

