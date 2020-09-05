from alento_bot import BaseModule
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


class EVEModule(BaseModule):
    def __init__(self, bot, storage):
        BaseModule.__init__(self, bot, storage)
        self.session = aiohttp.ClientSession()
        # noinspection PyArgumentList
        self.eve_config: EVEConfig = EVEConfig(self.storage.config)
        self.storage.caches.register_cache(self.eve_config, "eve_config")
        eve_manager_cache_location = f"{self.storage.config.data_folder_path}/cache"
        self.eve_manager = EVEManager(sde_path=self.eve_config.sde_location, cache_location=eve_manager_cache_location,
                                      use_aiohttp=True, session=self.session)
        self.auth: EVEAuthManager = EVEAuthManager(self.storage)
        self.user_auth: EVEUserAuthManager = EVEUserAuthManager(self.storage, self.session)
        self.market = MarketManager(self.eve_config, self.auth, self.eve_manager)
        self.planet_int = PlanetIntManager(self.storage, self.eve_config, self.user_auth, self.eve_manager,
                                           self.session)
        self.add_cog(EVEMiscCog())
        self.add_cog(EVEMarketCog(self.storage, self.eve_manager, self.market))
        self.add_cog(EVEAuthCog(self.storage, self.user_auth))
        self.add_cog(EVEPlanetaryIntegrationCog(self.user_auth, self.eve_manager, self.planet_int))
        self.add_cog(EVEIndustryJobCog(self.user_auth, self.eve_manager))
        self.add_cog(LootHistoryCog(self.eve_manager, self.market))

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
