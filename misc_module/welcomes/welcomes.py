from misc_module.welcomes.commands import welcome_control, welcome_on_join
from misc_module.storage import WelcomeConfig
from alento_bot import StorageManager, universal_text
from discord.ext import commands
from misc_module.welcomes import text
import logging
import discord


logger = logging.getLogger("main_bot")


class WelcomeCog(commands.Cog, name="Welcome"):
    def __init__(self, storage: StorageManager):
        self.storage: StorageManager = storage

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        welcome_config: WelcomeConfig = self.storage.guilds.get(member.guild.id, "welcome_config")
        if welcome_config.enabled:
            await welcome_on_join(welcome_config, member)

    @commands.guild_only()
    @commands.group(name="welcome", description=text.WELCOME_DESCRIPTION, brief=text.WELCOME_BRIEF,
                    invoke_without_command=True)
    async def welcome(self, context: commands.Context, *subcommand: str):
        if subcommand:
            await context.send(universal_text.INVALID_SUBCOMMAND)
        else:
            await context.send_help(context.command)

    @commands.guild_only()
    @welcome.command(name="info", brief=text.WELCOME_INFO_BRIEF)
    async def welcome_info(self, context: commands.Context):
        welcome_config: WelcomeConfig = self.storage.guilds.get(context.guild.id, "welcome_config")
        await welcome_control.send_list_embed(welcome_config, context)

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @welcome.command(name="enable", brief=text.WELCOME_ENABLE_BRIEF)
    async def welcome_enable(self, context: commands.Context):
        welcome_config: WelcomeConfig = self.storage.guilds.get(context.guild.id, "welcome_config")
        if welcome_config.enabled:
            await context.send(text.WELCOME_ENABLED_ALREADY)
        else:
            welcome_config.enabled = True
            await context.send(text.WELCOME_ENABLED)
            if not welcome_config.welcome_channel_id:
                await context.send(text.WELCOME_ENABLED_NO_CHANNEL_SET)

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @welcome.command(name="disable", brief=text.WELCOME_DISABLE_BRIEF)
    async def welcome_disable(self, context: commands.Context):
        welcome_config: WelcomeConfig = self.storage.guilds.get(context.guild.id, "welcome_config")
        if welcome_config.enabled:
            welcome_config.enabled = False
            await context.send(text.WELCOME_DISABLED)
        else:
            await context.send(text.WELCOME_DISABLED_ALREADY)

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @welcome.command(name="add", description=text.WELCOME_ADD_DESCRIPTION, brief=text.WELCOME_BRIEF,
                     require_var_positional=True)
    async def welcome_add(self, context: commands.Context, *welcome_message: str):
        welcome_config: WelcomeConfig = self.storage.guilds.get(context.guild.id, "welcome_config")
        await welcome_control.add_welcome(welcome_config, context, " ".join(welcome_message))

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @welcome.command(name="remove", aliases=["rm", ], description=text.WELCOME_REMOVE_DESCRIPTION,
                     brief=text.WELCOME_REMOVE_BRIEF)
    async def welcome_remove(self, context: commands.Context, index: int):
        welcome_config: WelcomeConfig = self.storage.guilds.get(context.guild.id, "welcome_config")
        if index > 0:
            modified_index = index - 1
        else:
            modified_index = index
        await welcome_control.remove_welcome(welcome_config, context, modified_index)

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @welcome.command(name="set", brief=text.WELCOME_SET_BRIEF)
    async def welcome_set(self, context: commands.Context):
        welcome_config: WelcomeConfig = self.storage.guilds.get(context.guild.id, "welcome_config")
        welcome_config.welcome_channel_id = context.channel.id
        await context.send(text.WELCOME_SET_CHANNEL)

    @welcome.error
    @welcome_info.error
    @welcome_enable.error
    @welcome_disable.error
    @welcome_add.error
    @welcome_remove.error
    @welcome_set.error
    async def welcome_error(self, context: commands.Context, exception: Exception):
        if isinstance(exception, commands.MissingPermissions):
            await context.send(universal_text.ERROR_MISSING_PERMISSION)
        elif isinstance(exception, commands.NoPrivateMessage):
            await context.send(universal_text.ERROR_GUILD_ONLY)
        elif isinstance(exception, commands.MissingRequiredArgument):
            await context.send_help(context.command)
        elif isinstance(exception, commands.BadArgument):
            await context.send(universal_text.ERROR_BAD_ARGUMENT_NUMBERS)
        else:
            await context.send(f"a critical error has occurred. send this message to alento ghostflame.\n"
                               f"{type(exception)}\n{exception}")
            raise exception
