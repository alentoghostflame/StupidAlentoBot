from eve_module.storage import EVEUserAuthManager, PlanetIntManager
from evelib import EVEManager, esi
from eve_module.planetary_integration import pi_control
from eve_module.planetary_integration import text
from discord.ext import commands
import logging
from aiohttp.client_exceptions import ClientOSError


logger = logging.getLogger("main_bot")


class AuthNoSelected(commands.CheckFailure):
    pass


class AuthScopeMissing(commands.CheckFailure):
    pass


class EVEPlanetaryIntegrationCog(commands.Cog, name="EVEPI"):
    def __init__(self, user_auth: EVEUserAuthManager, eve_manager: EVEManager, planet_int: PlanetIntManager):
        self.user_auth: EVEUserAuthManager = user_auth
        self.eve_manager: EVEManager = eve_manager
        self.planet_int = planet_int

    @commands.group(name="pi", brief=text.PI_BRIEF)
    async def pi_group(self, context: commands.Context):
        if not self.user_auth.get_selected_scopes(context.author.id):
            raise AuthNoSelected
        elif context.invoked_subcommand is None:
            if context.message.content.strip() == f"{context.prefix}{context.command.name}":
                await pi_control.send_help_embed(context)
            else:
                await context.send(text.PI_INVALID_SUBCOMMAND)

    @pi_group.command(name="enable", brief=text.PI_ENABLE_BRIEF)
    async def pi_enable(self, context: commands.Context):
        await pi_control.enable_pi(self.user_auth, context)

    @pi_group.command(name="disable", brief=text.PI_DISABLE_BRIEF)
    async def pi_disable(self, context: commands.Context):
        await pi_control.disable_pi(self.user_auth, context)

    @pi_group.group(name="update", brief=text.PI_UPDATE_BRIEF, invoke_without_command=True)
    async def pi_update_group(self, context: commands.Context, planet_id_str=None):
        if context.invoked_subcommand is None:
            if planet_id_str:
                await pi_control.update_planet(self.user_auth, self.planet_int, context, planet_id_str)
            elif context.message.content.strip() == f"{context.prefix}pi {context.command.name}":
                await pi_control.send_update_help_embed(context)
            else:
                await context.send(text.PI_UPDATE_INVALID_SUBCOMMAND)

    @pi_update_group.command(name="basic", brief=text.PI_UPDATE_BASIC_BRIEF)
    async def pi_update_basic(self, context: commands.Context):
        if self.user_auth.get_selected_scopes(context.author.id).get("esi-planets.manage_planets.v1", None):
            await pi_control.update_basic(self.user_auth, self.planet_int, context)
        else:
            raise AuthScopeMissing

    @pi_update_group.command(name="full", brief=text.PI_UPDATE_FULL_BRIEF)
    async def pi_update_full(self, context: commands.Context):
        if self.user_auth.get_selected_scopes(context.author.id).get("esi-planets.manage_planets.v1", None):
            await pi_control.update_full(self.user_auth, self.planet_int, context)
        else:
            raise AuthScopeMissing

    @pi_group.command(name="info", brief=text.PI_INFO_BRIEF)
    async def pi_info(self, context: commands.Context, arg2=None):
        if self.user_auth.get_selected_scopes(context.author.id).get("esi-planets.manage_planets.v1", None):
            await pi_control.send_info_embed(self.user_auth, self.planet_int, context, arg2)
        else:
            raise AuthScopeMissing

    @pi_group.error
    @pi_update_full.error
    @pi_update_basic.error
    @pi_info.error
    async def on_pi_error(self, context: commands.Context, error: Exception):
        if isinstance(error, AuthNoSelected):
            await context.send(text.NO_AUTH_SELECTED_CHARACTER)
        elif isinstance(error, ClientOSError):
            await context.send(text.CLIENTOSERROR)
        elif isinstance(error, AuthScopeMissing):
            await context.send(text.PI_AUTH_SCOPE_FALSE)
        elif isinstance(error, esi.ESIServiceUnavailable):
            await context.send(text.PI_SERVICE_UNAVAILABLE)
        else:
            await context.send(f"A critical error occurred: {type(error)}: {error}\nSEND THIS TO ALENTO/SOMBRA "
                               f"GHOSTFLAME!")
            raise error


    async def on_auth_scope_missing_error(self, context: commands.Context, error: Exception):
        if isinstance(error, AuthScopeMissing):
            await context.send(text.PI_AUTH_SCOPE_FALSE)
        else:
            await context.send(f"A critical error occurred: {type(error)}: {error}\nSEND THIS TO ALENTO/SOMBRA "
                               f"GHOSTFLAME!")
            raise error
