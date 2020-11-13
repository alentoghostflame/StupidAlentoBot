from alento_bot import StorageManager, BaseModule, user_data_transformer
from discord.ext import commands


@user_data_transformer(name="example_user_data")
class ExampleUserData:
    def __init__(self):
        self.example_count = 0


class ExampleModule(BaseModule):
    def __init__(self, bot, storage):
        BaseModule.__init__(self, bot, storage)
        self.storage.users.register_data_name("example_user_data", ExampleUserData)
        self.add_cog(ExampleCog(storage))


class ExampleCog(commands.Cog):
    def __init__(self, storage: StorageManager):
        self.storage = storage

    @commands.command(name="example")
    async def example_command(self, context: commands.Context, *args):
        user_data: ExampleUserData = self.storage.users.get(context.author.id, "example_user_data")
        if args:
            user_data.example_count += 1
            await context.send(f"You gave: {', '.join(args)}.")
        else:
            user_data.example_count += 1
            await context.send("Hi there!")
