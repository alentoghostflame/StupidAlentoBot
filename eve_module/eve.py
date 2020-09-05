from alento_bot import DiscordBot
from evelib import EVEManager
from eve_module.storage import EVEAuthManager, EVEConfig, MarketManager, \
    EVEUserAuthManager, PlanetIntManager
from eve_module.planetary_integration import EVEPlanetaryIntegrationCog
from eve_module.industry_jobs import EVEIndustryJobCog
from eve_module.loot_history import LootHistoryCog
from eve_module.user_auth import EVEAuthCog
from eve_module.market import EVEMarketCog
from eve_module.misc import EVEMiscCog
import logging
import aiohttp
import asyncio


logger = logging.getLogger("main_bot")


class EVEModule:
    def __init__(self, discord_bot: DiscordBot):
        self.discord_bot: DiscordBot = discord_bot

        self.session = aiohttp.ClientSession()

        # noinspection PyArgumentList
        self.eve_config: EVEConfig = EVEConfig(self.discord_bot.storage.config)
        self.discord_bot.storage.caches.register_cache(self.eve_config, "eve_config")

        eve_manager_cache_location = f"{self.discord_bot.storage.config.data_folder_path}/cache"
        self.eve_manager = EVEManager(sde_path=self.eve_config.sde_location, cache_location=eve_manager_cache_location,
                                      use_aiohttp=True, session=self.session)

        self.auth: EVEAuthManager = EVEAuthManager(self.discord_bot.storage)
        self.user_auth: EVEUserAuthManager = EVEUserAuthManager(self.discord_bot.storage, self.session)
        self.market = MarketManager(self.eve_config, self.auth, self.eve_manager)
        self.planet_int = PlanetIntManager(self.discord_bot.storage, self.eve_config, self.user_auth, self.eve_manager,
                                           self.session)

    def register_cogs(self, discord_bot: DiscordBot):
        logger.info("Registering cogs for EVE")
        discord_bot.add_cog(EVEMiscCog())
        discord_bot.add_cog(EVEMarketCog(self.discord_bot.storage, self.eve_manager, self.market))
        discord_bot.add_cog(EVEAuthCog(self.discord_bot.storage, self.user_auth))
        discord_bot.add_cog(EVEPlanetaryIntegrationCog(self.user_auth, self.eve_manager, self.planet_int))
        discord_bot.add_cog(EVEIndustryJobCog(self.user_auth, self.eve_manager))
        discord_bot.add_cog(LootHistoryCog(self.eve_manager, self.market))

    def load(self):
        self.auth.load()
        self.eve_manager.load()
        self.planet_int.load()

    def save(self):
        self.eve_manager.save()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.close_session())
        loop.close()

    async def close_session(self):
        await self.session.close()
