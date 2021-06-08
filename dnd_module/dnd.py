from alento_bot import StorageManager, BaseModule, universal_text, error_handler
from dnd_module.commands import currency, inventory
from dnd_module.dnd_data import DndUserData, DnDCharData
from discord.ext import commands
from typing import Tuple, Union
import discord
import random


class DnDModule(BaseModule):
    def __init__(self, *args):
        BaseModule.__init__(self, *args)
        self.storage.users.register_data_name("dnd_data", DndUserData)
        self.add_cog(DnDCog(self.storage))


class DnDCog(commands.Cog, name="D&D"):
    def __init__(self, storage: StorageManager):
        self.storage = storage

    @commands.group(name="dnd", brief="D&D management.", invoke_without_command=True)
    async def dnd(self, context: commands.Context, *subcommand):
        if not subcommand:
            await context.send_help(context.command)
        else:
            await context.send(universal_text.INVALID_SUBCOMMAND)

    @dnd.command(name="create", brief="Create a new character.")
    async def dnd_create(self, context: commands.Context, *char_name: str):
        name = " ".join(char_name)
        data: DndUserData = self.storage.users.get(context.author.id, "dnd_data")
        if not name:
            await context.send("...how did you get here? dnd_create, `if not name` is `True`, but error_handler "
                               "should take over if no reasonable argument is given?")
        elif name.lower() in data.chars:
            await context.send("You already have a character with that name!")
        else:
            data.create_character(name)
            await context.send(f"Character with name `{name}` created!")

    @dnd.command(name="select", brief="Selects a character to view or edit.")
    async def dnd_select(self, context: commands.Context, *char_name: str):
        name = " ".join(char_name)
        data: DndUserData = self.storage.users.get(context.author.id, "dnd_data")
        if name.lower() in data.chars:
            data.selected_char = name.lower()
            await context.send(f"Character `{data.chars[data.selected_char].name}` selected.")
        else:
            await context.send("No character by that name found.")

    @dnd.command(name="rm", brief="Permanently delete a character.")
    async def dnd_remove(self, context: commands.Context, *char_name: str):
        name = " ".join(char_name)
        data: DndUserData = self.storage.users.get(context.author.id, "dnd_data")
        if name.lower() in data.chars:
            data.chars.pop(name.lower())
            await context.send("Character deleted.")
        else:
            await context.send("No character by that name found.")

    @dnd.command(name="sheet", brief="Displays your character sheet.")
    async def dnd_sheet(self, context: commands.Context):
        data: DndUserData = self.storage.users.get(context.author.id, "dnd_data")
        if data.selected_char and (char_data := data.chars.get(data.selected_char, None)):
            await context.send(embed=get_sheet_embed(char_data))
        else:
            await context.send("Selected character is either None or invalid.")

    @dnd.command(name="info", brief="Show information about your characters and which you have selected.")
    async def dnd_info(self, context: commands.Context):
        embed = discord.Embed(title="D&D Info")
        data: DndUserData = self.storage.users.get(context.author.id, "dnd_data")
        if data.chars:
            char_text = ""
            for char_name in data.chars:
                char_text += f"{data.chars[char_name].name} | {data.chars[char_name].basic.level}\n"
        else:
            char_text = "None"
        embed.add_field(name="Characters", value=char_text)
        if data.selected_char:
            embed.add_field(name="Selected", value=f"`{data.selected_char}`")
        else:
            embed.add_field(name="Selected", value="None")
        await context.send(embed=embed)

    @dnd.group(name="inv", brief="Controls the inventory of the selected character.", invoke_without_command=True)
    async def dnd_inv(self, context: commands.Context, *subcommand):
        if not subcommand:
            await context.send_help(context.command)
        else:
            await context.send(universal_text.INVALID_SUBCOMMAND)

    @dnd_inv.command(name="info", brief="Shows inventory.")
    async def dnd_inv_info(self, context: commands.Context):
        data: DndUserData = self.storage.users.get(context.author.id, "dnd_data")
        if data.selected_char and (char_data := data.chars.get(data.selected_char, None)):
            embed = discord.Embed(title=char_data.name)
            embed.add_field(name="Inventory", value=char_data.inv.text())
            await context.send(embed=embed)
        else:
            await context.send("Selected character is either None or invalid.")

    @dnd_inv.command(name="add", brief="Add an item with a name, quantity, and weight.")
    async def dnd_inv_add(self, context: commands.Context, item: Union[int, str], quantity: int, weight: float = None):
        await inventory.add(self.storage, context, item, quantity, weight)

    @dnd_inv.command(name="rm", brief="Remove a given quantity of an item from your inventory.")
    async def dnd_inv_rm(self, context: commands.Context, item: Union[int, str], quantity: int):
        await inventory.rm(self.storage, context, item, quantity)

    @dnd_inv.command(name="del", brief="Deletes an item from your inventory.")
    async def dnd_inv_del(self, context: commands.Context, item: Union[int, str]):
        await inventory.del_item(self.storage, context, item)

    @dnd_inv.command(name="swap", brief="Swaps the position of items in your inventory.")
    async def dnd_inv_swap(self, context: commands.Context, item1: Union[int, str], item2: Union[int, str]):
        await inventory.swap(self.storage, context, item1, item2)

    @dnd_inv.group(name="cp", brief="Edit Copper Piece count.", invoke_without_command=True)
    async def dnd_inv_cp(self, context: commands.Context, *subcommand):
        if not subcommand:
            await context.send_help(context.command)
        else:
            await context.send(universal_text.INVALID_SUBCOMMAND)

    @dnd_inv_cp.command(name="add", brief="Add to Copper Piece count.")
    async def dnd_inv_cp_add(self, context: commands.Context, amount: int):
        await currency.cp_add(self.storage, context, amount)

    @dnd_inv_cp.command(name="rm", brief="Remove from Copper Piece count.")
    async def dnd_inv_cp_rm(self, context: commands.Context, amount: int):
        await currency.cp_rm(self.storage, context, amount)

    @dnd_inv_cp.command(name="set", brief="Set your Copper Piece count.")
    async def dnd_inv_cp_set(self, context: commands.Context, amount: int):
        await currency.cp_set(self.storage, context, amount)

    @dnd_inv.group(name="sp", brief="Edit Silver Piece count.", invoke_without_command=True)
    async def dnd_inv_sp(self, context: commands.Context, *subcommand):
        if not subcommand:
            await context.send_help(context.command)
        else:
            await context.send(universal_text.INVALID_SUBCOMMAND)

    @dnd_inv_sp.command(name="add", brief="Add to Silver Piece count.")
    async def dnd_inv_sp_add(self, context: commands.Context, amount: int):
        await currency.sp_add(self.storage, context, amount)

    @dnd_inv_sp.command(name="rm", brief="Remove from Silver Piece count.")
    async def dnd_inv_sp_rm(self, context: commands.Context, amount: int):
        await currency.sp_rm(self.storage, context, amount)

    @dnd_inv_sp.command(name="set", brief="Set your Silver Piece count.")
    async def dnd_inv_sp_set(self, context: commands.Context, amount: int):
        await currency.sp_set(self.storage, context, amount)

    @dnd_inv.group(name="ep", brief="Edit Electrum Piece count.", invoke_without_command=True)
    async def dnd_inv_ep(self, context: commands.Context, *subcommand):
        if not subcommand:
            await context.send_help(context.command)
        else:
            await context.send(universal_text.INVALID_SUBCOMMAND)

    @dnd_inv_ep.command(name="add", brief="Add to Electrum Piece count.")
    async def dnd_inv_ep_add(self, context: commands.Context, amount: int):
        await currency.ep_add(self.storage, context, amount)

    @dnd_inv_ep.command(name="rm", brief="Remove from Electrum Piece count.")
    async def dnd_inv_ep_rm(self, context: commands.Context, amount: int):
        await currency.ep_rm(self.storage, context, amount)

    @dnd_inv_ep.command(name="set", brief="Set your Electrum Piece count.")
    async def dnd_inv_ep_set(self, context: commands.Context, amount: int):
        await currency.ep_set(self.storage, context, amount)

    @dnd_inv.group(name="gp", brief="Edit Gold Piece count.", invoke_without_command=True)
    async def dnd_inv_gp(self, context: commands.Context, *subcommand):
        if not subcommand:
            await context.send_help(context.command)
        else:
            await context.send(universal_text.INVALID_SUBCOMMAND)

    @dnd_inv_gp.command(name="add", brief="Add to Gold Piece count.")
    async def dnd_inv_gp_add(self, context: commands.Context, amount: int):
        await currency.gp_add(self.storage, context, amount)

    @dnd_inv_gp.command(name="rm", brief="Remove from Gold Piece count.")
    async def dnd_inv_gp_rm(self, context: commands.Context, amount: int):
        await currency.gp_rm(self.storage, context, amount)

    @dnd_inv_gp.command(name="set", brief="Set your Gold Piece count.")
    async def dnd_inv_gp_set(self, context: commands.Context, amount: int):
        await currency.gp_set(self.storage, context, amount)

    @dnd_inv.group(name="pp", brief="Edit Platinum Piece count.", invoke_without_command=True)
    async def dnd_inv_pp(self, context: commands.Context, *subcommand):
        if not subcommand:
            await context.send_help(context.command)
        else:
            await context.send(universal_text.INVALID_SUBCOMMAND)

    @dnd_inv_pp.command(name="add", brief="Add to Platinum Piece count.")
    async def dnd_inv_pp_add(self, context: commands.Context, amount: int):
        await currency.pp_add(self.storage, context, amount)

    @dnd_inv_pp.command(name="rm", brief="Remove from Platinum Piece count.")
    async def dnd_inv_pp_rm(self, context: commands.Context, amount: int):
        await currency.pp_rm(self.storage, context, amount)

    @dnd_inv_pp.command(name="set", brief="Set your Platinum Piece count.")
    async def dnd_inv_pp_set(self, context: commands.Context, amount: int):
        await currency.pp_set(self.storage, context, amount)

    @commands.command(name="roll", brief="Allows you to quickly roll lots of die",
                      description="Allows you to quickly roll lots of die, with the following format: "
                                  "`roll countDsides`, like `roll 5D20` to roll five D20's. Maximum of 25 different "
                                  "sets of rolls, and 9999 die in a single roll.")
    async def roll(self, context: commands.Context, *rolls: str):
        if not rolls:
            await context.send_help(context.command)
        elif len(rolls) > 25:
            await context.send("Can't handle more than 25 different rolls, sorry!")
        else:
            await context.send(embed=process_rolls_get_embed(rolls))

    @dnd.error
    @dnd_create.error
    @dnd_select.error
    @dnd_remove.error
    @dnd_info.error
    @dnd_sheet.error
    @dnd_inv.error
    @dnd_inv_info.error
    @dnd_inv_add.error
    @dnd_inv_cp.error
    @dnd_inv_cp_add.error
    @dnd_inv_cp_rm.error
    @dnd_inv_cp_set.error
    @dnd_inv_sp.error
    @dnd_inv_sp_add.error
    @dnd_inv_sp_rm.error
    @dnd_inv_sp_set.error
    @dnd_inv_ep.error
    @dnd_inv_ep_add.error
    @dnd_inv_ep_rm.error
    @dnd_inv_ep_set.error
    @dnd_inv_gp.error
    @dnd_inv_gp_add.error
    @dnd_inv_gp_rm.error
    @dnd_inv_gp_set.error
    @dnd_inv_pp.error
    @dnd_inv_pp_add.error
    @dnd_inv_pp_rm.error
    @dnd_inv_pp_set.error
    @roll.error
    async def dnd_error_handler(self, context: commands.Context, exception: Exception):
        await error_handler(context, exception)


def valid_roll(count: str, value: str) -> bool:
    if count.isdigit() and value.isdigit() and (count_int := int(count)) > 0 and (value_int := int(value)) > 0 and \
            count_int <= 9999:
        return True
    return False


def process_rolls_get_embed(rolls: Tuple[str]) -> discord.Embed:
    embed = discord.Embed(title="Rolls")
    for roll_str in rolls:
        if len(split_roll := roll_str.lower().split("d")) == 2 and valid_roll(split_roll[0], split_roll[1]):
            numbers = [random.randint(1, int(split_roll[1])) for x in range(int(split_roll[0]))]
            value_string = ""
            if len(numbers) <= 10:
                value_string += f"Numbers: {', '.join(str(x) for x in numbers)}.\n"
            value_sum = sum(numbers)
            value_string += f"Sum: {value_sum}, Average: {(value_sum / len(numbers)):.2f}"
            embed.add_field(name=roll_str, value=value_string, inline=True)
        else:
            embed.add_field(name=roll_str, value="Invalid roll string.", inline=True)
    return embed


def get_sheet_embed(char: DnDCharData) -> discord.Embed:
    embed = discord.Embed(title=char.name)
    embed.add_field(name="Basic", value=char.basic.text(), inline=False)
    embed.add_field(name="Stats", value=char.stats.text(), inline=True)
    embed.add_field(name="Inventory", value=char.inv.text(), inline=False)

    return embed
