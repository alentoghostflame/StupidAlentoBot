from alento_bot import StorageManager
from dnd_module.dnd_data import DndUserData
from discord.ext import commands
from typing import Union


async def add(storage: StorageManager, context: commands.Context, item: Union[str, int], quantity: int, weight: float = None):
    data: DndUserData = storage.users.get(context.author.id, "dnd_data")
    if data.selected_char and (char_data := data.chars.get(data.selected_char, None)):
        if isinstance(item, int):
            if quantity < 1:
                await context.send("You have to specify a positive quantity.")
            else:
                item = char_data.inv.add_item_int(item, quantity)
                if item:
                    await context.send(f"{item.quantity - quantity} -> {item.quantity} x {item.name}")
                else:
                    await context.send("Invalid index given.")
        else:
            if char_data.inv.find_item(item):
                item = char_data.inv.add_item_str(item, quantity, 666.666)
                await context.send(f"{item.quantity - quantity} -> {item.quantity} x {item.name}")
            else:
                if weight is None:
                    await context.send("To create a new item, you must specify the weight.")
                else:
                    item = char_data.inv.add_item_str(item, quantity, weight)
                    await context.send(f"None -> {item.quantity} x {item.name}")
    else:
        await context.send("Selected character is either None or invalid.")


async def rm(storage: StorageManager, context: commands.Context, item: Union[str, int], quantity: int):
    data: DndUserData = storage.users.get(context.author.id, "dnd_data")
    if data.selected_char and (char_data := data.chars.get(data.selected_char, None)):
        if quantity < 1:
            await context.send("You have to specify a positive quantity.")
        else:
            if isinstance(item, int):
                item, rm_quantity = char_data.inv.rm_item_int(item, quantity)
                if item:
                    await context.send(f"{item.quantity + rm_quantity} -> {item.quantity} x {item.name}")
                else:
                    await context.send("Invalid index given.")
            else:
                item, rm_quantity = char_data.inv.rm_item_str(item, quantity)
                if item:
                    await context.send(f"{item.quantity + rm_quantity} -> {item.quantity} x {item.name}")
                else:
                    await context.send("Invalid item name given.")
    else:
        await context.send("Selected character is either None or invalid.")


async def del_item(storage: StorageManager, context: commands.Context, item: Union[int, str]):
    data: DndUserData = storage.users.get(context.author.id, "dnd_data")
    if data.selected_char and (char_data := data.chars.get(data.selected_char, None)):
        if isinstance(item, int):
            item = char_data.inv.del_item_int(item)
        else:
            item = char_data.inv.del_item_str(item)

        if item:
            await context.send(f"{item.quantity} x {item.name} -> Deleted.")
        else:
            await context.send(f"Item not found or Index out of range.")
    else:
        await context.send("Selected character is either None or invalid.")


async def swap(storage: StorageManager, context: commands.Context, item1: Union[int, str], item2: Union[int, str]):
    data: DndUserData = storage.users.get(context.author.id, "dnd_data")
    if data.selected_char and (char_data := data.chars.get(data.selected_char, None)):
        if isinstance(item1, int) and isinstance(item2, int):
            item1, item2 = char_data.inv.swap_item_int(item1, item2)
            if item1 and item2:
                await context.send(f"`{item2.name}` and `{item1.name}` have been swapped.")
            else:
                await context.send("Index('s) not valid.")
        elif isinstance(item1, str) and isinstance(item2, str):
            item1, item2 = char_data.inv.swap_item_str(item1, item2)
            if item1 and item2:
                await context.send(f"`{item2.name}` and `{item1.name}` have been swapped.")
            else:
                await context.send("Item(s) not found in inventory.")
        else:
            await context.send("You can't mix item indexes and names.")
    else:
        await context.send("Selected character is either None or invalid.")
