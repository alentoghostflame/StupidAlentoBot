from alento_bot import StorageManager, BaseModule, error_handler, universal_text, TimerManager
from devtool_module.eval import owner_eval
from devtool_module import text
from discord.ext import commands
from typing import Union
import discord
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
        self.add_cog(DevToolCog(self.bot, self.storage, self.timer))


class DevToolCog(commands.Cog, name="Dev Tools"):
    def __init__(self, bot: commands.Bot, storage: StorageManager, timer: TimerManager):
        self.bot = bot
        self.storage = storage
        self.timer = timer

    @commands.is_owner()
    @commands.group(name="dev", invoke_without_command=True, brief="Bot Developer Tools.")
    async def dev(self, context: commands.Context, *subcommand):
        if subcommand:
            await context.send(universal_text.INVALID_SUBCOMMAND)
        else:
            await context.send_help(context.command)

    @commands.is_owner()
    @dev.command(name="msg", brief="Says the real text of message and logs it in console.")
    async def dev_msg(self, context: commands.Context, message_id: int):
        if message := await context.fetch_message(message_id):
            logger.info(message.content)
            await context.send(f"```{message.content}```")

    @commands.is_owner()
    @dev.command(name="say", brief="Repeats the message you give.")
    async def dev_say(self, context: commands.Context, *, message):
        await context.send(message)

    @commands.is_owner()
    @dev.command(name="saych", brief="Repeats the message you give in the text channel provided.")
    async def dev_saych(self, context: commands.Context, channel: Union[int, discord.TextChannel], *, message):
        # await channel.send(message)
        send_channel = channel
        if isinstance(channel, int) and not (context.guild and (send_channel := context.guild.get_channel(channel))):
            send_channel = await self.bot.fetch_channel(channel)

        if send_channel:
            await send_channel.send(message)
        else:
            await context.send("Either that channel doesn't exist, or I don't have access to it.")

    @commands.is_owner()
    @commands.command(name="eval", brief=text.EVAL_BRIEF)
    async def owner_eval(self, context: commands.Context, *, code=None):
        await owner_eval(self.bot, self.storage, self.timer, context, given_code=code)

    @dev.error
    @dev_msg.error
    @dev_say.error
    @owner_eval.error
    async def on_error(self, context: commands.Context, exception: Exception):
        if isinstance(exception, commands.BadArgument):
            await context.send(universal_text.ERROR_BAD_ARGUMENT_NUMBERS)
        elif isinstance(exception, commands.CommandInvokeError):
            await context.send(f"Command Error occured: {type(exception)}, {exception}")
        else:
            await error_handler(context, exception)

    @dev_saych.error
    async def on_saych_error(self, context: commands.Context, exception: Exception):
        if isinstance(exception, commands.BadUnionArgument):
            await context.send("Channel specified has to be either #channel or the channel ID. (numbers)")
        else:
            await error_handler(context, exception)
