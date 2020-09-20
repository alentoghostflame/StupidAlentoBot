from alento_bot import StorageManager
from misc2_module.callouts.callout_data import CalloutGuildConfig
from misc2_module.callouts import text, callout_func, callout_delete, callout_fistbump
from discord.ext import commands
import logging
import discord


logger = logging.getLogger("main_bot")


class CalloutCog(commands.Cog, name="Misc Module"):
    def __init__(self, storage: StorageManager):
        self._storage: StorageManager = storage
        self._storage.guilds.register_data_name("callout_guild_config", CalloutGuildConfig)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        await callout_fistbump.callout_fistbump(message)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        callout_config = self._storage.guilds.get(message.guild.id, "callout_guild_config")
        if callout_config.deletes:
            await callout_delete.callout_delete(callout_config, message)

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.group(name="callout", brief=text.CALLOUT_BRIEF, invoke_without_command=True)
    async def callout_group(self, context: commands.Context):
        if context.invoked_subcommand is None:
            if context.message.content.strip() == f"{context.prefix}{context.command.name}":
                await context.send_help(context.command)
            else:
                await context.send(text.CALLOUT_COMMAND_NOT_FOUND)

    @callout_group.group(name="delete", brief=text.CALLOUT_DELETE_BRIEF, invoke_without_command=True)
    async def callout_delete_group(self, context: commands.Context):
        if context.invoked_subcommand is None:
            if context.message.content.strip() == f"{context.prefix}callout {context.command.name}":
                await callout_delete.send_help_embed(context)
            else:
                await context.send(text.CALLOUT_DELETE_COMMAND_NOT_FOUND)

    @callout_delete_group.command(name="enable", brief=text.CALLOUT_DELETE_ENABLE_BRIEF)
    async def callout_delete_enable(self, context: commands.Context):
        callout_config = self._storage.guilds.get(context.guild.id, "callout_guild_config")
        await callout_delete.toggle_on(callout_config, context)

    @callout_delete_group.command(name="disable", brief=text.CALLOUT_DELETE_DISABLE_BRIEF)
    async def callout_delete_disable(self, context: commands.Context):
        callout_config = self._storage.guilds.get(context.guild.id, "callout_guild_config")
        await callout_delete.toggle_off(callout_config, context)

    @callout_group.group(name="fistbump", brief=text.CALLOUT_FISTBUMP_BRIEF, invoke_without_command=True)
    async def callout_fistbump(self, context: commands.Context):
        if context.invoked_subcommand is None:
            if context.message.content.strip() == f"{context.prefix}callout {context.command.name}":
                await context.send_help(context.command)
            else:
                await context.send(text.CALLOUT_COMMAND_NOT_FOUND)

    @callout_fistbump.command(name="enable", brief=text.CALLOUT_FISTBUMP_ENABLE_BRIEF)
    async def callout_fistbump_enable(self, context: commands.Context):
        callout_config = self._storage.guilds.get(context.guild.id, "callout_guild_config")
        await callout_fistbump.enable(callout_config, context)

    @callout_fistbump.command(name="disable", brief=text.CALLOUT_FISTBUMP_ENABLE_BRIEF)
    async def callout_fistbump_disable(self, context: commands.Context):
        callout_config = self._storage.guilds.get(context.guild.id, "callout_guild_config")
        await callout_fistbump.disable(callout_config, context)

    @callout_group.error
    async def missing_permissions_error(self, context, error: Exception):
        if isinstance(error, commands.MissingPermissions):
            await context.send(text.USER_MISSING_PERMISSIONS)
        elif isinstance(error, commands.BadArgument) or isinstance(error, commands.MissingRequiredArgument):
            await context.send_help(context.command)
        else:
            await context.send(f"ERROR:\nType: {type(error)}\n{error}")
            raise error
