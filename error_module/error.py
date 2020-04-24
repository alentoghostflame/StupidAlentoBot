from admin_module.background_task import background_task
from storage_module.disk_storage import DiskStorage
from discord.ext import commands
# from universal_module import utils
from error_module import text
import admin_module.warn
import logging
# import sys


logger = logging.getLogger("Main")
# sys.excepthook = utils.log_exception_handler


class ErrorCog(commands.Cog, name="Error Module"):
    def __init__(self):
        pass

    @commands.Cog.listener()
    async def on_command_error(self, context: commands.Context, error):

        if hasattr(context.command, "on_error"):
            return

        ignored = (commands.CommandNotFound, )
        error = getattr(error, "original", error)

        if isinstance(error, ignored):
            return
        elif isinstance(error, commands.DisabledCommand):
            return await context.send(text.COMMAND_DISABLED)
        elif isinstance(error, commands.NoPrivateMessage):
            try:
                return await context.send(text.NO_PRIVATE_MESSAGE)
            except:
                pass
        elif isinstance(error, commands.InvalidEndOfQuotedStringError):
            await context.send(text.INVALID_END_OF_QUOTED_STRING)
