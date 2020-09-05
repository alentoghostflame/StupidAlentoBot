from alento_bot.storage_module import guild_data_transformer, StorageManager, user_data_transformer
from discord.ext import commands
from alento_bot.core_cog import text
import logging
import random


logger = logging.getLogger("main_bot")


class CoreCog(commands.Cog, name="Core"):
    def __init__(self, storage: StorageManager):
        self.storage = storage
        self.storage.guilds.register_data_name("patreon_test", PatreonTest)
        self.storage.users.register_data_name("patreon_user_test", UserPatreonTest)

    @commands.command(name="patreon", brief="Posts the Patreon link.")
    async def patreon(self, context: commands.Context):
        guild_data: PatreonTest = self.storage.guilds.get(context.guild.id, "patreon_test")
        guild_data.patreon_uses += 1

        user_data: UserPatreonTest = self.storage.users.get(context.author.id, "patreon_user_test")
        user_data.patreon_users += 1

        patreon_link = "https://www.patreon.com/AlentoGhostflame"
        await context.send(random.sample(text.PATREON_MESSAGES, 1)[0].format(patreon_link))


@guild_data_transformer(name="patreon_test")
class PatreonTest:
    def __init__(self):
        self.patreon_uses: int = 0


@user_data_transformer(name="patreon_user_test")
class UserPatreonTest:
    def __init__(self):
        self.patreon_users: int = 0
