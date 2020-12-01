from alento_bot import BaseModule, StorageManager, TimerManager
from contextlib import redirect_stdout
from discord.ext import commands
from eval_module import text
from typing import List
import traceback
import textwrap
import logging
import io


logger = logging.getLogger("main_bot")


class EvalModule(BaseModule):
    def __init__(self, *args):
        BaseModule.__init__(self, *args)
        self.add_cog(EvalCog(self.bot, self.storage, self.timer))


class EvalCog(commands.Cog, name="Eval Module"):
    def __init__(self, bot: commands.Bot, storage: StorageManager, timer: TimerManager):
        super().__init__()
        self.bot: commands.Bot = bot
        self.storage: StorageManager = storage
        self.timer: TimerManager = timer

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Eval module ready.")

    @commands.is_owner()
    @commands.command(name="eval")
    async def owner_eval(self, context, *, given_code: str = None):
        if not given_code:
            await context.send(text.EVAL_NO_ARGUMENT)
            return

        env = {
            'context': context,
            'bot': self.bot,
            'channel': context.channel,
            'author': context.author,
            'guild': context.guild,
            'message': context.message,
            "storage": self.storage,
            "timer": self.timer
        }
        error_raised = False

        env.update(globals())

        cleaned_code = cleanup_code(given_code)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(cleaned_code, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            await context.send(f'```py\n{e.__class__.__name__}: {e}\n```')
            await context.message.add_reaction('\u274C')  # x
            return

        function = env['func']
        try:
            with redirect_stdout(stdout):
                return_value = await function()
            stdout_value = stdout.getvalue()

            if stdout_value:
                for page in paginate_text(stdout_value):
                    await context.send(f"```py\n{page}```")
            if return_value:
                paginated_text = paginate_text(str(return_value), 1960)
                await context.send(text.EVAL_RETURN_VALUE.format(paginated_text[0]))
                for page in paginated_text[1:]:
                    await context.send(f"```py\n{page}```")

            if not stdout_value and not return_value:
                await context.send(f"```\n{text.EVAL_NO_STDOUT_VALUE}\n{text.EVAL_NO_RETURN_VALUE}```")

            if stdout_value or return_value:
                await context.message.add_reaction('\u2705')  # tick
            elif error_raised:
                await context.message.add_reaction('\u274C')  # x
            else:
                await context.message.add_reaction('\u2705')

        except Exception as e:
            stdout_value = stdout.getvalue()
            await context.send(f"```py\n{stdout_value}{traceback.format_exc()}```")
            await context.message.add_reaction('\u274C')  # x

    @owner_eval.error
    async def not_owner(self, context, error):
        if isinstance(error, commands.NotOwner):
            await context.send("You are not him.")
        else:
            raise error


def paginate_text(long_text: str, char_limit: int = 1980) -> List[str]:
    logger.debug("Paginating Text.")
    last_page_index = 0
    pages = []

    for current in range(0, len(long_text)):
        if current % char_limit is 0:
            pages.append(long_text[last_page_index:current])
            last_page_index = current
    if last_page_index != len(long_text) - 1:
        pages.append(long_text[last_page_index:len(long_text)])

    logger.debug(f"Returning text with length of {len(long_text)} and {len(pages)} Pages.")
    logger.debug(f"Sanity {len(list(filter(None, pages)))}")
    return list(filter(None, pages))


def cleanup_code(content: str):
    """Automatically removes code blocks from the code."""
    # remove ```py\n```
    if content.startswith('```') and content.endswith('```'):
        return '\n'.join(content.split('\n')[1:-1])

    # remove `foo`
    return content.strip('` \n')

