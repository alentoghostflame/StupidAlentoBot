from storage_module.stupid_storage import DiskStorage
from contextlib import redirect_stdout
from discord.ext import commands
# import stupid_utils
import traceback
import textwrap
import io


class EvalCog(commands.Cog, name="Eval Module"):
    def __init__(self, bot, disk_storage: DiskStorage):
        super().__init__()
        self.bot = bot
        self.disk_storage = disk_storage

    @commands.is_owner()
    @commands.command(name="eval")
    async def owner_eval(self, context, *, body):
        env = {
            'context': context,
            'bot': self.bot,
            'channel': context.channel,
            'author': context.author,
            'guild': context.guild,
            'message': context.message,
            # 'source': context.getsource
        }

        def cleanup_code(content):
            """Automatically removes code blocks from the code."""
            # remove ```py\n```
            if content.startswith('```') and content.endswith('```'):
                return '\n'.join(content.split('\n')[1:-1])

            # remove `foo`
            return content.strip('` \n')

        env.update(globals())

        body = cleanup_code(body)
        stdout = io.StringIO()
        err = out = None

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        def paginate(text: str):
            '''Simple generator that paginates text.'''
            last = 0
            pages = []
            for curr in range(0, len(text)):
                if curr % 1980 == 0:
                    pages.append(text[last:curr])
                    last = curr
                    appd_index = curr
            if appd_index != len(text) - 1:
                pages.append(text[last:curr])
            return list(filter(lambda a: a != '', pages))

        try:
            exec(to_compile, env)
        except Exception as e:
            err = await context.send(f'```py\n{e.__class__.__name__}: {e}\n```')
            return await context.message.add_reaction('\u2049')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            err = await context.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            if ret is None:
                if value:
                    try:

                        out = await context.send(f'```py\n{value}\n```')
                    except:
                        paginated_text = paginate(value)
                        for page in paginated_text:
                            if page == paginated_text[-1]:
                                out = await context.send(f'```py\n{page}\n```')
                                break
                            await context.send(f'```py\n{page}\n```')
            else:
                try:
                    out = await context.send(f'```py\n{value}{ret}\n```')
                except:
                    paginated_text = paginate(f"{value}{ret}")
                    for page in paginated_text:
                        if page == paginated_text[-1]:
                            out = await context.send(f'```py\n{page}\n```')
                            break
                        await context.send(f'```py\n{page}\n```')

        if out:
            await context.message.add_reaction('\u2705')  # tick
        elif err:
            await context.message.add_reaction('\u2049')  # x
        else:
            await context.message.add_reaction('\u2705')

    @owner_eval.error
    async def not_owner(self, context, error):
        if isinstance(error, commands.NotOwner):
            await context.send("You are not him.")
        else:
            raise error

