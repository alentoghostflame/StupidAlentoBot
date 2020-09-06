from alento_bot import BaseModule
from discord.ext import commands


class ExampleModule(BaseModule):
    def __init__(self, bot, storage):
        BaseModule.__init__(self, bot, storage)
        self.add_cog(ExampleCog())


class ExampleCog(commands.Cog):
    def __init__(self):
        pass

    @commands.command(name="example")
    async def example_command(self, context: commands.Context, *args):
        if args:
            await context.send(f"You gave: {', '.join(args)}.")
        else:
            await context.send("Hi there!")

