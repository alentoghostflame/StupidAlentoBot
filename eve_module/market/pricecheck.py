from eve_module.storage import MarketManager
from evelib import EVEManager, UniverseManager, RegionData, SolarSystemData, TypeData
from typing import Dict, List, Tuple, Optional
from eve_module.market import text
from discord.ext import commands
import discord
import logging


logger = logging.getLogger("main_bot")
MAX_AUTOCOMPLETE: int = 20


async def pricecheck(eve_manager: EVEManager, market: MarketManager,
                     auto_complete_cache: Dict[str, Optional[List[int]]], context: commands.Context, *args):
    location_data = None
    args_in_name: int = 0
    item_data = None
    auto_complete_failed_flag: bool = False

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
        await context.send(text.PRICECHECK_HELP)
    elif not location_data:
        await context.send("Location not found in universe.")
    elif not args[args_in_name:]:
        await context.send(f"{location_data.id} : {location_data.name}")
    elif not item_data:
        await context.send("Item not found in database.")
    else:
        if isinstance(location_data, RegionData):
            buy_orders, sell_orders = await market.get_item_orders(location_data.id, item_data.id)
            embed = create_embed(buy_orders, sell_orders, item_data, location_data)
            await context.send(embed=embed)
        elif isinstance(location_data, SolarSystemData):
            region_data = eve_manager.universe.get_any(location_data.region)
            buy_orders, sell_orders = await market.get_item_orders(region_data.id, item_data.id, location_data.id)
            embed = create_embed(buy_orders, sell_orders, item_data, location_data)
            await context.send(embed=embed)
        else:
            await context.send("PRICECHECK.PY/PRICECHECK, DM TO ALENTO/SOMBRA \"{}\"".format(type(location_data)))


def get_location_data_from_list(universe: UniverseManager, string_list: Tuple[str, ...]):
    name_arg_counter = 0
    for i in range(len(string_list)):
        name_arg_counter += 1
        location_data = universe.get_any(" ".join(string_list[:i + 1]))
        if location_data:
            return location_data, name_arg_counter
    return None, 0


def create_embed(buy_orders: List[dict], sell_orders: List[dict], item_data: TypeData, location_data):
    embed = discord.Embed(title="{}: {}".format(location_data.name, item_data.name), color=0xffff00)

    seller_text = ""
    x = 0
    while x < 5 and x < len(sell_orders):
        seller_text += "{}) {} for {} ISK\n".format(x + 1, human_format(sell_orders[x]["volume_remain"], small_dec=0),
                                                    human_format(sell_orders[x]["price"]))
        x += 1
    if not seller_text:
        seller_text = "None"
    embed.add_field(name="{} Sell Orders".format(len(sell_orders)), value=seller_text, inline=True)

    buyer_text = ""
    x = 0
    while x < 5 and x < len(buy_orders):
        buyer_text += "{}) {} for {} ISK\n".format(x + 1, human_format(buy_orders[x]["volume_remain"], small_dec=0),
                                                   human_format(buy_orders[x]["price"]))
        x += 1
    if not buyer_text:
        buyer_text = "None"
    embed.add_field(name="{} Buy Orders".format(len(buy_orders)), value=buyer_text, inline=True)

    if len(sell_orders) > 0:
        if len(buy_orders) > 0 and sell_orders[0]["price"] * 0.9 <= buy_orders[0]["price"]:
            suggestion_text = "Suggested sell price: {} ISK (highest buy price)".format(human_format(buy_orders[0]["price"]))
        else:
            suggestion_text = "Suggested sell price: {} ISK (90% of lowest sell)".format(human_format(sell_orders[0]["price"] * 0.9))
    else:
        suggestion_text = "Not enough data."

    embed.add_field(name="Sell For", value=suggestion_text, inline=False)
    return embed


async def send_multiple_autocomplete(eve_manager: EVEManager, item_ids: List[int], context: commands.Context):
    if item_ids:
        names_string = ""
        for item_id in item_ids:
            item_data = eve_manager.types.get_type(item_id)
            if item_data:
                names_string += f"{item_data.name}\n"
            else:
                names_string += f"ERROR: {item_id}\n"
        await context.send(text.PRICECHECK_MULTIPLE_AUTOCOMPLETES.format(names_string))
    else:
        await context.send(text.PRICECHECK_AUTOCOMPLETE_EMPTY)


def get_autocomplete_items(auto_complete_cache: Dict[str, Optional[List[int]]], item_dict: Dict[str, int],
                           item_name: str) -> List[int]:
    if item_name.lower() not in auto_complete_cache:
        output_list = list()
        for key_name in item_dict:
            split_key_name = key_name.lower().split(" ")
            for i in range(len(split_key_name)):
                if " ".join(split_key_name[-i - 1::]).startswith(item_name):
                    output_list.append(item_dict[key_name])
                    break
            if len(output_list) > MAX_AUTOCOMPLETE:
                break

        auto_complete_cache[item_name.lower()] = output_list

    return auto_complete_cache[item_name.lower()]


def human_format(number: int, dec: int = 2, small_dec: int = 2):
    units = ["", "K", "M", "B", "T", "Q"]
    temp_num = number
    magnitude = 0
    while temp_num > 10000 and not (magnitude == 0 and temp_num < 100000):
        temp_num /= 1000
        magnitude += 1
    if magnitude == 0:
        return "{:,.{}f}{}".format(temp_num, small_dec, units[magnitude])
    elif len("{:.0f}".format(temp_num)) > 3:
        return "{:,.0f}{}".format(temp_num, units[magnitude])
    else:
        return "{:,.{}f}{}".format(temp_num, dec, units[magnitude])
