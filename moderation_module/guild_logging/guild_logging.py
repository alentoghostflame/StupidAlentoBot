from moderation_module.guild_logging.commands import guild_logging_control, send_delete_embed, send_edit_embed, \
    send_joined_embed, send_remove_embed
from moderation_module.storage import GuildLoggingConfig
from alento_bot import StorageManager
from discord.ext import commands
import moderation_module.text
import logging
import discord


logger = logging.getLogger("main_bot")


class GuildLoggingCog(commands.Cog, name="Logging"):
    def __init__(self, storage: StorageManager):
        self.storage: StorageManager = storage
        self.storage.guilds.register_data_name("guild_logging_config", GuildLoggingConfig)

    @commands.has_permissions(administrator=True)
    @commands.command(name="guild_logging_control", aliases=["logging", ])
    async def guild_logging_control(self, context: commands.Context, arg1=None, arg2=None):
        logging_config = self.storage.guilds.get(context.guild.id, "guild_logging_config")
        await guild_logging_control(logging_config, context, arg1, arg2)

    @guild_logging_control.error
    async def missing_permissions_error(self, context, error: Exception):
        if isinstance(error, commands.MissingPermissions):
            await context.send(moderation_module.text.MISSING_PERMISSIONS)
        else:
            await context.send(f"ERROR:\nType: {type(error)}\n{error}")
            raise error

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        logging_config: GuildLoggingConfig = self.storage.guilds.get(message.guild.id, "guild_logging_config")

        if logging_config.toggled_on and logging_config.log_channel_id and \
                message.channel.id not in logging_config.exempt_channels and \
                (logging_config.log_bots or (not logging_config.log_bots and not message.author.bot)):
            await send_delete_embed(logging_config, message)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        logging_config: GuildLoggingConfig = self.storage.guilds.get(after.guild.id, "guild_logging_config")
        if logging_config.toggled_on and logging_config.log_channel_id and \
                after.channel.id not in logging_config.exempt_channels and \
                (logging_config.log_bots or (not logging_config.log_bots and not after.author.bot)) and \
                before.content != after.content:
            await send_edit_embed(logging_config, before, after)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        logging_config: GuildLoggingConfig = self.storage.guilds.get(member.guild.id, "guild_logging_config")
        if logging_config.toggled_on and logging_config.log_channel_id:
            await send_joined_embed(logging_config, member)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        logging_config: GuildLoggingConfig = self.storage.guilds.get(member.guild.id, "guild_logging_config")
        if logging_config.toggled_on and logging_config.log_channel_id:
            await send_remove_embed(logging_config, member)
