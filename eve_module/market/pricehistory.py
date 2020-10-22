from evelib import EVEManager, RegionData, MarketHistory
from eve_module.market.pricecheck import human_format, get_autocomplete_items, send_multiple_autocomplete, \
    get_location_data_from_list
from typing import Dict, List, Optional
from eve_module.market import text
from discord.ext import commands
from datetime import datetime, timedelta
import discord
import logging


logger = logging.getLogger("main_bot")
MAX_AUTOCOMPLETE: int = 20


async def pricehistory(eve_manager: EVEManager, auto_complete_cache: Dict[str, Optional[List[int]]],
                       context: commands.Context, *args):
    location_data = None
    args_in_name = 0
    item_data = None
    auto_complete_failed_flag = False

    if args:
        location_data, args_in_name = get_location_data_from_list(eve_manager.universe, args)
        if location_data and args[args_in_name:]:
            item_name = " ".join(args[args_in_name:])
            item_data = eve_manager.types.get_type(item_name)
            if not item_data:
                possible_names = get_autocomplete_items(auto_complete_cache, eve_manager.types.get_names(), item_name)
                if len(possible_names) == 1:
                    item_data = eve_manager.types.get_type(possible_names[0])
                elif len(possible_names) > MAX_AUTOCOMPLETE:
                    await context.send(text.PRICECHECK_AUTOCOMPLETE_TOO_MANY.format(MAX_AUTOCOMPLETE))
                    auto_complete_failed_flag = True
                elif len(possible_names) > 1:
                    await send_multiple_autocomplete(eve_manager, possible_names, context)
                    auto_complete_failed_flag = True

    if auto_complete_failed_flag:
        pass
    elif not args:
        await context.send_help(context.command)
    elif not location_data:
        await context.send("Region not found in universe.")
    elif not isinstance(location_data, RegionData):
        await context.send("Only regions are supported at this time.")
    elif not args[args_in_name:]:
        await context.send(f"{location_data.id} : {location_data.name}")
    elif not item_data:
        await context.send("Item not found in database.")
    else:
        market_history = await eve_manager.esi.market.get_region_history(location_data.id, item_data.id)
        await context.send(embed=create_embed(market_history))


def create_embed(mh: MarketHistory) -> discord.Embed:
    embed = discord.Embed(title=f"History of {mh.location.name}: {mh.item.name}", color=0xffff00)

    newest_text = f"Average: {human_format(mh.newest.average)} ISK\nHighest: {human_format(mh.newest.highest)} ISK\n" \
                  f"Lowest: {human_format(mh.newest.lowest)} ISK\nOrders: {human_format(mh.newest.order_count, 0, 0)}" \
                  f"\nVolume: {human_format(mh.newest.volume)} m3\n" \
                  f"Quantity: {human_format(mh.newest.volume // mh.item.volume, small_dec=0)}\n" \
                  f"Date: `{mh.newest.date.strftime('%Y-%m-%d')}`"
    embed.add_field(name="Newest", value=newest_text, inline=True)
    oldest_text = f"Average: {human_format(mh.oldest.average)} ISK\nHighest: {human_format(mh.oldest.highest)} ISK\n" \
                  f"Lowest: {human_format(mh.oldest.lowest)} ISK\n" \
                  f"Orders: {human_format(mh.oldest.order_count, 0, 0)}\n" \
                  f"Volume: {human_format(mh.oldest.volume)} m3\n" \
                  f"Quantity: {human_format(mh.oldest.volume // mh.item.volume, small_dec=0)}\n" \
                  f"Date: `{mh.oldest.date.strftime('%Y-%m-%d')}`"
    embed.add_field(name="Oldest", value=oldest_text, inline=True)
    total_text = f"Average: {human_format(mh.average)} ISK\nHighest: {human_format(mh.highest)} ISK\n" \
                 f"Lowest: {human_format(mh.lowest)} ISK\nTotal Orders: {human_format(mh.order_count, 0, 0)}\n" \
                 f"Total Volume: {human_format(mh.volume)} m3\n" \
                 f"Total Quantity: {human_format(mh.volume // mh.item.volume, small_dec=0)}"
    embed.add_field(name="Stats", value=total_text, inline=False)
    thirty_text = get_30_day_stats(mh)
    embed.add_field(name="30 Day Stats", value=thirty_text, inline=True)

    return embed


def get_30_day_stats(mh: MarketHistory) -> str:
    total_isk_amount = 0
    total_volume_amount = 0
    for data in mh:
        if data.date > datetime.utcnow() - timedelta(days=30):
            total_isk_amount += data.average * data.order_count
            total_volume_amount += data.volume

    output_str = f"Total ISK: {human_format(total_isk_amount)}\n" \
                 f"Total Volume: {human_format(total_volume_amount)} m3\n" \
                 f"Total Quantity: {human_format(total_volume_amount // mh.item.volume, small_dec=0)}"
    return output_str

