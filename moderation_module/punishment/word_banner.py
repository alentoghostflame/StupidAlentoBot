from moderation_module.punishment.commands import word_ban_control, delete_message_and_warn
from moderation_module.storage import PunishmentManager, WordBanConfig
from discord.ext import commands
from alento_bot import StorageManager
import moderation_module.text
import logging
import discord


logger = logging.getLogger("main_bot")


class WordBanCog(commands.Cog, name="Word Ban"):
    def __init__(self, storage: StorageManager, punish_manager: PunishmentManager, bot: commands.Bot):
        self.storage: StorageManager = storage
        self.punish_manager: PunishmentManager = punish_manager
        self.bot: commands.Bot = bot

    @commands.command(name="word_ban_control", aliases=["word_ban", "wordban"])
    async def word_ban_control(self, context, arg1=None, *args):
        ban_config = self.storage.guilds.get(context.guild.id, "word_ban_config")
        await word_ban_control(ban_config, context, arg1, *args)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        context = await self.bot.get_context(message)
        if not message.author.bot and not context.valid:
            ban_config: WordBanConfig = self.storage.guilds.get(message.guild.id, "word_ban_config")
            if ban_config.toggled_on:
                split_message = message.content.split()
                for possible_word in split_message:
                    stripped_word = possible_word.strip("_`*~|\\\"").lower()
                    if stripped_word in ban_config.banned_words:
                        punish_config = self.storage.guilds.get(message.guild.id, "punishment_config")
                        await delete_message_and_warn(self.punish_manager, punish_config, message, possible_word)
