from evelib import EVEManager, RegionData, MarketHistory, MarketHistoryData
from eve_module.market.pricecheck import human_format, get_autocomplete_items, send_multiple_autocomplete, \
    get_location_data_from_list
from typing import Dict, List, Optional, Tuple
from eve_module.market import text
from discord.ext import commands
from datetime import datetime, timedelta
import discord
import logging


logger = logging.getLogger("main_bot")
MAX_AUTOCOMPLETE: int = 20


async def price_history(eve_manager: EVEManager, auto_complete_cache: Dict[str, Optional[List[int]]],
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
        market_history = await eve_manager.esi.market.get_region_history(location_data, item_data)
        await context.send(embed=create_embed(market_history))


# def create_embed(mh: MarketHistory) -> discord.Embed:
#     embed = discord.Embed(title=f"History of {mh.location.name}: {mh.item.name}", color=0xffff00)
#
#     newest_text = f"Average: {human_format(mh.newest.average)} ISK\nHighest: {human_format(mh.newest.highest)} ISK\n" \
#                   f"Lowest: {human_format(mh.newest.lowest)} ISK\nOrders: {human_format(mh.newest.order_count, 0, 0)}" \
#                   f"\nVolume: {human_format(mh.newest.volume)} m3\n" \
#                   f"Quantity: {human_format(mh.newest.volume // mh.item.volume, small_dec=0)}\n" \
#                   f"Date: `{mh.newest.date.strftime('%Y-%m-%d')}`"
#     embed.add_field(name="Newest", value=newest_text, inline=True)
#     oldest_text = f"Average: {human_format(mh.oldest.average)} ISK\nHighest: {human_format(mh.oldest.highest)} ISK\n" \
#                   f"Lowest: {human_format(mh.oldest.lowest)} ISK\n" \
#                   f"Orders: {human_format(mh.oldest.order_count, 0, 0)}\n" \
#                   f"Volume: {human_format(mh.oldest.volume)} m3\n" \
#                   f"Quantity: {human_format(mh.oldest.volume // mh.item.volume, small_dec=0)}\n" \
#                   f"Date: `{mh.oldest.date.strftime('%Y-%m-%d')}`"
#     embed.add_field(name="Oldest", value=oldest_text, inline=True)
#     total_text = f"Average: {human_format(mh.average)} ISK\nHighest: {human_format(mh.highest)} ISK\n" \
#                  f"Lowest: {human_format(mh.lowest)} ISK\nTotal Orders: {human_format(mh.order_count, 0, 0)}\n" \
#                  f"Total Volume: {human_format(mh.volume)} m3\n" \
#                  f"Total Quantity: {human_format(mh.volume // mh.item.volume, small_dec=0)}"
#     embed.add_field(name="Stats", value=total_text, inline=False)
#     thirty_text = get_30_day_stats(mh)
#     embed.add_field(name="30 Day Stats", value=thirty_text, inline=True)
#
#     return embed


def create_embed(history: MarketHistory):
    embed = discord.Embed(title=f"History of {history.region.name}: {history.item.name}", color=0xffff00)

    newest, oldest = get_newest_oldest_data(history)
    avg_all, hi_all, low_all, isk_all, qty_all = get_all_stats(history)
    avg_90, hi_90, low_90, isk_90, qty_90 = get_x_day_stats(history, 90)
    avg_30, hi_30, low_30, isk_30, qty_30 = get_x_day_stats(history, 30)

    overall_str = f"{len(history.orders)} days of data from {oldest.date_str} to {newest.date_str}.\n" \
                  f"Low: {human_format(low_all)}, High: {human_format(hi_all)}, Average: {human_format(avg_all)}\n" \
                  f"Total Quantity: {human_format(qty_all, small_dec=0)}, Total ISK: {human_format(isk_all)}"
    embed.add_field(name="Overall", value=overall_str, inline=False)
    day_90_str = f"Low: {human_format(low_90)}, High: {human_format(hi_90)}, Average: {human_format(avg_90)}"
    embed.add_field(name="Last 90 Days", value=day_90_str, inline=False)
    day_30_str = f"Low: {human_format(low_30)}, High: {human_format(hi_30)}, Average: {human_format(avg_30)}"
    embed.add_field(name="Last 30 Days", value=day_30_str, inline=False)

    return embed


# def get_30_day_stats(mh: MarketHistory) -> str:
#     total_isk_amount = 0
#     total_volume_amount = 0
#     for data in mh:
#         if data.date > datetime.utcnow() - timedelta(days=30):
#             total_isk_amount += data.average * data.order_count
#             total_volume_amount += data.volume
#
#     output_str = f"Total ISK: {human_format(total_isk_amount)}\n" \
#                  f"Total Volume: {human_format(total_volume_amount)} m3\n" \
#                  f"Total Quantity: {human_format(total_volume_amount // mh.item.volume, small_dec=0)}"
#     return output_str


def get_all_stats(history: MarketHistory) -> Tuple[float, float, float, float, int]:
    average_sum = 0
    highest_isk = 0
    lowest_isk = 0
    total_isk = 0
    total_quantity = 0
    for day in history.orders:
        total_isk += day.average * day.quantity
        total_quantity += day.quantity
        average_sum += day.average
        if not highest_isk or highest_isk < day.highest:
            highest_isk = day.highest
        if not lowest_isk or day.lowest < lowest_isk:
            lowest_isk = day.lowest
    return average_sum / len(history.orders), highest_isk, lowest_isk, total_isk, total_quantity


def get_x_day_stats(history: MarketHistory, days: int) -> Tuple[float, float, float, float, int]:
    average_sum = 0
    highest_isk = 0
    lowest_isk = 0
    total_isk = 0
    total_quantity = 0
    counted_days = 0
    cutoff_time = datetime.utcnow() - timedelta(days=days, seconds=1)
    for day in history.orders:
        if cutoff_time < day.date:
            total_isk += day.average * day.quantity
            total_quantity += day.quantity
            average_sum += day.average
            if not highest_isk or highest_isk < day.highest:
                highest_isk = day.highest
            if not lowest_isk or day.lowest < lowest_isk:
                lowest_isk = day.lowest
            counted_days += 1
    if counted_days:
        return average_sum / counted_days, highest_isk, lowest_isk, total_isk, total_quantity
    else:
        return 0, highest_isk, lowest_isk, total_isk, total_quantity


def get_newest_oldest_data(history: MarketHistory) -> Tuple[MarketHistoryData, MarketHistoryData]:
    newest = None
    oldest = None
    for day in history.orders:
        if not newest or newest.date < day.date:
            newest = day
        if not oldest or day.date < oldest.date:
            oldest = day
    return newest, oldest



