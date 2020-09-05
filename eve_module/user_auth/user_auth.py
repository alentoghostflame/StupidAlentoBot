from eve_module.user_auth import text
from alento_bot import StorageManager
from eve_module.storage import EVEUserAuthManager
from eve_module.user_auth import eve_auth
from discord.ext import commands
import logging
# import discord


logger = logging.getLogger("main_bot")


async def not_in_guild(context: commands.Context):
    if context.guild:
        return False
    else:
        return True


class EVEAuthCog(commands.Cog, name="EVE Auth"):
    def __init__(self, storage: StorageManager, user_auth: EVEUserAuthManager):
        self.storage: StorageManager = storage
        self.user_auth: EVEUserAuthManager = user_auth

    @commands.group(name="auth", brief=text.EVE_AUTH_CONTROL_BRIEF)
    @commands.check(not_in_guild)
    async def eve_auth_group(self, context: commands.Context):
        if context.invoked_subcommand is None:
            if context.message.content.strip() == f"{context.prefix}{context.command.name}":
                await eve_auth.send_help_embed(context)
            else:
                await context.send(text.EVE_AUTH_CONTROL_COMMAND_NOT_FOUND)

    @eve_auth_group.command(name="list")
    async def eve_auth_list(self, context: commands.Context, character_id=None):
        if character_id:
            await eve_auth.send_character_info_embed(self.user_auth, context, character_id)
        else:
            await eve_auth.send_auth_list_embed(self.user_auth, context)

    @eve_auth_group.command(name="create")
    async def eve_auth_create(self, context: commands.Context):
        await context.send(text.EVE_AUTH_CONTROL_CREATE_TEXT.format(self.user_auth.get_basic_eve_auth_url()))

    @eve_auth_group.command(name="delete")
    async def eve_auth_delete(self, context: commands.Context, character_id=None):
        await eve_auth.delete_character(self.user_auth, context, character_id)

    @eve_auth_group.command(name="select")
    async def eve_auth_select(self, context: commands.Context, character_id=None):
        await eve_auth.select_character(self.user_auth, context, character_id)

    @eve_auth_group.command(name="update")
    async def eve_auth_update(self, context: commands.Context, arg1=None):
        await eve_auth.send_update_url(self.user_auth, context, arg1)

    @eve_auth_group.command(name="token")
    async def eve_auth_token(self, context: commands.Context, authorization_url=None):
        await eve_auth.register_token(self.user_auth, context, authorization_url)

    @eve_auth_group.command(name="gat")
    async def eve_auth_gat(self, context: commands):
        await eve_auth.get_access_token(self.user_auth, context)

    @eve_auth_group.error
    async def on_guild_check_error(self, context: commands.Context, error: Exception):
        if isinstance(error, commands.CheckFailure):
            await context.send(text.EVE_AUTH_CONTROL_CONTEXT_HAS_GUILD)
