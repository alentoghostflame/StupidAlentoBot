from eve_module.storage import MarketManager
from evelib import EVEManager, SolarSystemData, RegionData, TypeData
from eve_module.loot_history import text
from discord.ext import commands
from datetime import datetime
import logging
from typing import Dict, List, Optional, Union
from io import StringIO
import discord
# import yaml
import csv


logger = logging.getLogger("main_bot")


class ItemLootHistory:
    def __init__(self, type_data: TypeData, quantity: int, time: datetime, price_per_unit: float):
        self.type_data = type_data
        self.name: str = self.type_data.name
        self.quantity: int = quantity
        self.price_per_unit: float = price_per_unit
        self.volume_per_unit: float = self.type_data.volume
        self.time: datetime = time

    def get_price(self, percent: float = 1.0) -> float:
        return self.quantity * self.price_per_unit * percent

    def get_volume(self, percent: float = 1.0) -> float:
        return self.quantity * self.volume_per_unit * percent


class PlayerLootHistory:
    def __init__(self, name: str):
        self.name: str = name
        self.item_loot: List[ItemLootHistory] = list()
        self.time_started: Optional[datetime] = None
        self.time_ended: Optional[datetime] = None

    def add_item(self, item_loot: ItemLootHistory):
        if self.time_started is None or self.time_started > item_loot.time:
            self.time_started = item_loot.time
        if self.time_ended is None or self.time_ended < item_loot.time:
            self.time_ended = item_loot.time

        self.item_loot.append(item_loot)


async def loot_history(eve_manager: EVEManager, market: MarketManager, context: commands.Context, filter_mode: str,
                       display_mode: str, location_name: str = "jita", payout_percent: float = 1.0,
                       quantity_percent: float = 1.0):
    location_data = eve_manager.universe.get_any(location_name)
    if not filter_mode:
        await send_help_embed(context)
    elif not context.message.attachments:
        await context.send(text.LOOT_HISTORY_NO_ATTACHMENT)
    elif filter_mode not in {"all", "ore"}:
        await context.send(text.LOOT_HISTORY_INVALID_FILTER)
    elif display_mode not in {"display", "tsv", "yaml", "yaml_full"}:
        await context.send(text.LOOT_HISTORY_INVALID_OUTPUT)
    elif not location_data:
        await context.send(text.LOOT_HISTORY_INVALID_LOCATION)
    elif display_mode == "display":
        await display_loot_history(eve_manager, market, context, filter_mode, location_data, payout_percent,
                                   quantity_percent)
    elif display_mode == "tsv":
        await send_loot_history_tsv(eve_manager, market, context, filter_mode, location_data, payout_percent,
                                    quantity_percent)
    elif display_mode == "yaml":
        # await send_loot_history_yaml(eve_manager, market, context, filter_mode, location_data, payout_percent,
        #                              full=False)
        await context.send("Unsupported at this time.")
    elif display_mode == "yaml_full":
        # await send_loot_history_yaml(eve_manager, market, context, filter_mode, location_data, payout_percent,
        #                              full=True)
        await context.send("Unsupported at this time.")
    else:
        await context.send(f"LOOT_HISTORY: ALL ELIFS PASSED, YOU HAVE A HOLE SOMEWHERE! \"{filter_mode}\", "
                           f"\"{display_mode}\". SEND THIS TO ALENTO/SOMBRA GHOSTFLAME!")
    """
    Ideal command layout:
    ;lh all|ore display|tsv
    If no attachment, error.
    """


async def send_help_embed(context: commands.Context):
    embed = discord.Embed(title="Loot History", color=0xF1F1D4)

    embed.add_field(name="Description", value=text.LOOT_HISTORY_HELP_DESCRIPTION, inline=False)
    embed.add_field(name="Usage", value=text.LOOT_HISTORY_HELP_USAGE, inline=False)
    embed.add_field(name="Options", value=text.LOOT_HISTORY_HELP_OPTIONS, inline=False)

    await context.send(embed=embed)


async def display_loot_history(eve_manager: EVEManager, market: MarketManager, context: commands.Context,
                               filter_mode: str, location_data: Union[RegionData, SolarSystemData],
                               payout_percent: float = 1.0, quantity_percent: float = 1.0):
    bot_message = await context.send(text.LOOT_HISTORY_DISPLAY_LOOT_HISTORY_WAIT)
    loot_data = await attachment_to_filtered_list(eve_manager, market, context.message.attachments[0], filter_mode,
                                                  location_data)
    if loot_data:
        item_name_list = list()
        item_data_list = list()
        data_rows = list()

        for character_name in loot_data:
            player_dict = {"player_name": character_name}
            player_payout = 0
            for looted_item in loot_data[character_name].item_loot:
                if looted_item.name not in item_name_list:
                    item_name_list.append(looted_item.name)
                    item_data_list.append(looted_item)
                # player_dict[looted_item.name] = looted_item.quantity * quantity_percent
                if looted_item.name in player_dict:
                    player_dict[looted_item.name] += looted_item.quantity * quantity_percent
                else:
                    player_dict[looted_item.name] = looted_item.quantity * quantity_percent
                player_payout += looted_item.get_price(payout_percent) * quantity_percent
            player_dict["payout"] = player_payout
            data_rows.append(player_dict)

        price_unit_row = {"player_name": "price_per_unit"}
        for item_data in item_data_list:
            price_unit_row[item_data.name] = f"{item_data.price_per_unit * payout_percent:,.2f}"
        data_rows.append(price_unit_row)

        output_string = "Player Name\t" + "\t".join(item_name_list)
        for row in data_rows:
            output_string += f"\n{row['player_name']}"
            for item_name in item_name_list:
                output_string += f"\t{row.get(item_name, 0)}"
            if "payout" in row:
                output_string += f"\t{row['payout']:,.2f} ISK"

        await bot_message.edit(content=f"Calculated using market prices from "
                                       f"{location_data.name} at {payout_percent * 100}% ISK and "
                                       f"{quantity_percent * 100}% quantity payout.\n{output_string}")

    else:
        await bot_message.edit(content=text.LOOT_HISTORY_NOTHING_TO_SHOW)


async def send_loot_history_tsv(eve_manager: EVEManager, market: MarketManager, context: commands.Context,
                                filter_mode: str, location_data: Union[RegionData, SolarSystemData],
                                payout_percent: float = 1.0, quantity_percent: float = 1.0):
    bot_message = await context.send(text.LOOT_HISTORY_DISPLAY_LOOT_HISTORY_WAIT)
    loot_data = await attachment_to_filtered_list(eve_manager, market, context.message.attachments[0], filter_mode,
                                                  location_data)

    if loot_data:
        item_name_list = list()
        item_data_list = list()
        data_rows = list()

        for character_name in loot_data:
            player_dict = {"player_name": character_name}
            player_payout = 0
            for looted_item in loot_data[character_name].item_loot:
                if looted_item.name not in item_name_list:
                    item_name_list.append(looted_item.name)
                    item_data_list.append(looted_item)
                if looted_item.name in player_dict:
                    player_dict[looted_item.name] += looted_item.quantity * quantity_percent
                else:
                    player_dict[looted_item.name] = looted_item.quantity * quantity_percent
                player_payout += looted_item.get_price(payout_percent) * quantity_percent
            player_dict["payout"] = player_payout
            data_rows.append(player_dict)

        price_unit_row = {"player_name": "price_per_unit"}
        for item_data in item_data_list:
            price_unit_row[item_data.name] = item_data.price_per_unit * payout_percent
        data_rows.append(price_unit_row)

        fake_file = StringIO()
        field_name_list = ["player_name"] + item_name_list + ["payout"]
        csv_writer = csv.DictWriter(fake_file, field_name_list, dialect="excel-tab")
        csv_writer.writeheader()
        csv_writer.writerows(data_rows)
        fake_file.seek(0)

        await bot_message.edit(content=text.LOOT_HISTORY_LOOT_HISTORY_FILE_SUCCESS.
                               format(f"Calculated using market prices from {location_data.name} at "
                                      f"{payout_percent * 100}% ISK and {quantity_percent * 100}% quantity payout."))
        await context.send(file=discord.File(fake_file, filename=f"Loot-Processed-{datetime.utcnow()}.tsv"))
    else:
        await bot_message.edit(content=text.LOOT_HISTORY_NOTHING_TO_SHOW)


async def attachment_to_filtered_list(eve_manager: EVEManager, market: MarketManager, attachment: discord.Attachment,
                                      filter_mode: str, location_data: Union[RegionData, SolarSystemData]) \
        -> Optional[Dict[str, PlayerLootHistory]]:
    bytes_content: bytes = await attachment.read()
    fake_file = StringIO(bytes_content.decode("utf8"))
    csv_reader = csv.DictReader(fake_file, dialect="excel-tab")
    loot_history_list = list(csv_reader)
    if loot_history_verifier(loot_history_list):
        output_dict: Dict[str, PlayerLootHistory] = dict()
        for row in loot_history_list:
            item_data = eve_manager.types.get_type(row["Item Type"])

            if filter_mode == "all" or \
                    (filter_mode == "ore" and item_data.group.category_id == 25):  # Asteroid

                if row["Character"] not in output_dict:
                    output_dict[row["Character"]] = PlayerLootHistory(row["Character"])
                player_data = output_dict[row["Character"]]

                item_loot_time = datetime.strptime(row["Time"], "%Y.%m.%d %H:%M")
                if isinstance(location_data, RegionData):
                    price_per_unit = await get_price_per_unit_average(market, item_data.id, location_data.id)
                else:
                    price_per_unit = await get_price_per_unit_average(market, item_data.id, location_data.region,
                                                                      location_data.id)

                item_loot_data = ItemLootHistory(item_data, int(row["Quantity"]), item_loot_time, price_per_unit)
                player_data.add_item(item_loot_data)
        return output_dict
    else:
        return None


async def get_price_per_unit_average(market: MarketManager, item_id: int, region_id: int,
                                     solar_system_id: int = None) -> float:
    if solar_system_id:
        buy_orders, sell_orders = await market.get_item_orders(region_id, item_id, solar_system_id)
    else:
        buy_orders, sell_orders = await market.get_item_orders(region_id, item_id)
    price_sum = 0.0
    count = 0
    for i in range(min(len(sell_orders), 3)):
        price_sum += sell_orders[i]["price"]
        count = i + 1
    if count:
        return price_sum / count
    else:
        return 0


def loot_history_verifier(full_loot_history: list) -> bool:

    if not full_loot_history:
        return False

    for row in full_loot_history:
        if not row.get("Time", None) or not row.get("Character", None) or not row.get("Item Type", None) or not \
                row.get("Quantity", None) or not row.get("Item Group", None):
            return False
    return True
