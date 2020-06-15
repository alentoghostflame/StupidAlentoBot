from faq_module.commands import faq_control, faq_on_message
from faq_module.storage import FAQManager, FAQConfig
from alento_bot import DiscordBot, StorageManager
from discord.ext import commands
import logging
import discord


logger = logging.getLogger("main_bot")


class FAQModule:
    def __init__(self, discord_bot: DiscordBot):
        self.discord_bot: DiscordBot = discord_bot
        self.discord_bot.storage.guilds.register_data_name("faq_config", FAQConfig)
        self.faq_manager: FAQManager = FAQManager(self.discord_bot.storage)

    def register_cogs(self):
        logger.info("Registering cogs for FAQ.")
        self.discord_bot.add_cog(FAQCog(self.discord_bot.storage, self.faq_manager, self.discord_bot.bot))


class FAQCog(commands.Cog, name="FAQ"):
    def __init__(self, storage: StorageManager, faq_manager: FAQManager, bot: commands.Bot):
        self.storage: StorageManager = storage
        self.faq_manager: FAQManager = faq_manager
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild:
            faq_config: FAQConfig = self.storage.guilds.get(message.guild.id, "faq_config")
            if faq_config.enabled and not message.author.bot:
                context: commands.Context = await self.bot.get_context(message)
                if not context.valid:
                    await faq_on_message(self.faq_manager, message)

    @commands.command("faq_control", aliases=["faq", ])
    async def faq_control(self, context: commands.Context, arg1=None, arg2=None, arg3=None, arg4=None, *args):
        faq_config = self.storage.guilds.get(context.guild.id, "faq_config")
        await faq_control(self.faq_manager, faq_config, context, arg1, arg2, arg3, arg4, *args)
