from eve_module.storage import MarketManager
from evelib import EVEManager
from discord.ext.commands.errors import CommandInvokeError
from eve_module.loot_history import text
from eve_module.loot_history import lh
from discord.ext import commands
import logging


logger = logging.getLogger("main_bot")


class LootHistoryCog(commands.Cog, name="EVELH"):
    def __init__(self, eve_manager: EVEManager, market: MarketManager):
        self.eve_manager: EVEManager = eve_manager
        self.market: MarketManager = market

    @commands.command(name="loot_history", aliases=["lh", ])
    async def loot_history_command(self, context: commands.Context, filter_mode=None, display_mode=None,
                                   location="jita", payout_percent=1.0, quantity_percent=1.0):
        await lh.loot_history(self.eve_manager, self.market, context, filter_mode, display_mode, location,
                              payout_percent, quantity_percent)

    @loot_history_command.error
    async def on_error(self, context: commands.Context, error: CommandInvokeError):
        if isinstance(error.original, UnicodeDecodeError):
            await context.send(text.LOOT_HISTORY_UNICODE_DECODE_ERROR)
        else:
            await context.send(f"```{type(error)}\n {error}```")
            raise error
