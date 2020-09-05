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
    async def loot_history_command(self, context: commands.Context, arg1=None, arg2=None, arg3="jita", arg4=1.0,
                                   arg5=1.0):
        await lh.loot_history(self.eve_manager, self.market, context, arg1, arg2, arg3, arg4, arg5)

    @loot_history_command.error
    async def on_error(self, context: commands.Context, error: CommandInvokeError):
        if isinstance(error.original, UnicodeDecodeError):
            await context.send(text.LOOT_HISTORY_UNICODE_DECODE_ERROR)
        else:
            await context.send(f"```{type(error)}\n {error}```")
            raise error
