from eve_module.storage import EVEUserAuthManager
from alento_bot import universal_text
from evelib import EVEManager
from eve_module.industry_jobs import text
from eve_module.industry_jobs import industry_job_cmds
from discord.ext import commands
import logging
from aiohttp.client_exceptions import ClientOSError


logger = logging.getLogger("main_bot")


class AuthNoSelected(commands.CheckFailure):
    pass


class AuthScopeMissing(commands.CheckFailure):
    pass


class EVEIndustryJobCog(commands.Cog, name="EVE Industry"):
    def __init__(self, user_auth: EVEUserAuthManager, eve_manager: EVEManager):
        self.user_auth: EVEUserAuthManager = user_auth
        self.eve_manager: EVEManager = eve_manager

    # @commands.group(name="industry", brief=text.INDUSTRY_JOBS_BRIEF)
    # async def industry_job_group(self, context: commands.Context):
    #     if context.invoked_subcommand is None:
    #         if context.message.content.strip() == f"{context.prefix}{context.command.name}":
    #             await industry_job_cmds.send_help_embed(context)
    #         else:
    #             await context.send(text.INDUSTRY_JOBS_INVALID_SUBCOMMAND)
    #     elif not self.user_auth.get_selected_scopes(context.author.id):
    #         raise AuthNoSelected
    @commands.group(name="industry", brief=text.INDUSTRY_BRIEF, invoke_without_command=True)
    async def industry(self, context: commands.Context, *subcommand):
        if subcommand:
            await context.send(universal_text.INVALID_SUBCOMMAND)
        else:
            await context.send_help(context.command)

    @industry.command(name="enable", brief=text.INDUSTRY_ENABLE_BRIEF)
    async def industry_enable(self, context: commands.Context):
        await industry_job_cmds.enable_industry(self.user_auth, context)

    @industry.command(name="disable", brief=text.INDUSTRY_DISABLE_BRIEF)
    async def industry_disable(self, context: commands.Context):
        await industry_job_cmds.disable_industry(self.user_auth, context)

    @industry.command("info", brief=text.INDUSTRY_INFO_BRIEF)
    async def industry_info(self, context: commands.Context):
        if (scopes := self.user_auth.get_selected_scopes(context.author.id)) and \
                scopes.get("esi-industry.read_character_jobs.v1", None):
            await industry_job_cmds.send_industry_info(self.eve_manager, self.user_auth, context)
        else:
            raise AuthScopeMissing

    @industry.error
    @industry_info.error
    @industry_enable.error
    @industry_disable.error
    async def on_error(self, context: commands.Context, error: Exception):
        if isinstance(error, AuthNoSelected):
            await context.send(text.NO_AUTH_SELECTED_CHARACTER)
        elif isinstance(error, ClientOSError):
            await context.send(text.CLIENTOSERROR)
        elif isinstance(error, commands.MissingRequiredArgument):
            await context.send_help(context.command)
        elif isinstance(error, AuthScopeMissing):
            await context.send(text.INDUSTRY_AUTH_SCOPE_FALSE)
        else:
            await context.send(f"A critical error occurred: {type(error)}: {error}\nSEND THIS TO ALENTO/SOMBRA "
                               f"GHOSTFLAME!")
            raise error
