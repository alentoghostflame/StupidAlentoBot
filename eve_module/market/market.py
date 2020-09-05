from eve_module.market import text, pricecheck
from eve_module.storage import MarketManager
from evelib import EVEManager
from discord.ext import commands, tasks
from alento_bot import StorageManager
from typing import Dict, List, Optional
import asyncio
import logging


logger = logging.getLogger("main_bot")


class EVEMarketCog(commands.Cog, name="EVEMarket"):
    def __init__(self, storage: StorageManager, eve_manager: EVEManager, market: MarketManager):
        self.storage: StorageManager = storage
        self.eve_manager: EVEManager = eve_manager
        self.market: MarketManager = market

        self.auto_complete_cache: Dict[str, Optional[List[int]]] = dict()

    @commands.command(name="pricecheck", brief=text.PRICECHECK_BRIEF, aliases=["pc", ], usage=text.PRICECHECK_USAGE)
    async def pricecheck_command(self, context: commands.Context, *args):
        await pricecheck.pricecheck(self.eve_manager, self.market, self.auto_complete_cache, context, *args)

    async def start_tasks(self):
        logger.debug("Starting refresh_structure_info task.")
        self.market_refresh_structure_info.start()
        await asyncio.sleep(5)
        logger.debug("Starting refresh_orders task.")
        self.market_refresh_orders.start()

    def cog_unload(self):
        self.market_refresh_structure_info.cancel()
        self.market_refresh_orders.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        logger.debug("Starting EVE Market background task loops.")
        await self.start_tasks()

    @tasks.loop(hours=24)
    async def market_refresh_structure_info(self):
        await self.market.refresh_structure_info()

    @tasks.loop(hours=1)
    async def market_refresh_orders(self):
        await self.market.refresh_structure_market_orders()

    @pricecheck_command.error
    async def on_pricecheck_error(self, context: commands.Context, error: Exception):
        await context.send(f"AN ERROR HAS OCCURRED: {type(error)}, {error}")
        raise error
