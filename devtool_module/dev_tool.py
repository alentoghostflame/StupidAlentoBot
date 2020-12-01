from alento_bot import StorageManager, BaseModule, user_data_transformer, universal_text
from discord.ext import commands
import logging


logger = logging.getLogger("main_bot")


# @user_data_transformer(name="example_user_data")
# class ExampleUserData:
#     def __init__(self):
#         self.example_count = 0


class DevToolModule(BaseModule):
    def __init__(self, *args):
        BaseModule.__init__(self, *args)
        # self.storage.users.register_data_name("example_user_data", ExampleUserData)
        self.add_cog(DevToolCog(self.storage))


class DevToolCog(commands.Cog, name="Dev Tools"):
    def __init__(self, storage: StorageManager):
        self.storage = storage

    @commands.is_owner()
    @commands.group(name="dev", invoke_without_command=True, brief="devtools")
    async def dev(self, context: commands.Context, *subcommand):
        if subcommand:
            await context.send(universal_text.INVALID_SUBCOMMAND)
        else:
            await context.send_help(context.command)

    @commands.is_owner()
    @dev.command(name="msg", brief="Says real text of message and logs it.")
    async def dev_msg(self, context: commands.Context, message_id: int):
        if message := await context.fetch_message(message_id):
            logger.info(message.content)
            await context.send(f"```{message.content}```")

    @dev.error
    @dev_msg.error
    async def on_error(self, context: commands.Context, exception: Exception):
        if isinstance(exception, commands.MissingRequiredArgument):
            await context.send_help(context.command)
        elif isinstance(exception, commands.BadArgument):
            await context.send(universal_text.ERROR_BAD_ARGUMENT_NUMBERS)
        elif isinstance(exception, commands.CommandInvokeError):
            await context.send(f"Command Error occured: {type(exception)}, {exception}")
        else:
            await context.send(f"A CRITICAL ERROR OCCURED:\n\n {type(exception)}\n\n {exception}\n\n"
                               f"REPORT THIS TO SOMBRA/ALENTO GHOSTFLAME!")
            raise exception
