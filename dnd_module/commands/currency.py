from dnd_module.dnd_data import DndUserData
from alento_bot import StorageManager
from discord.ext import commands


async def cp_add(storage: StorageManager, context: commands.Context, amount: int):
    data: DndUserData = storage.users.get(context.author.id, "dnd_data")
    if data.selected_char and (char_data := data.chars.get(data.selected_char, None)):
        temp = char_data.inv.money.cp
        char_data.inv.money.cp += amount
        await context.send(f"Copper: `{temp}` -> `{char_data.inv.money.cp}`")
    else:
        await context.send("Selected character is either None or invalid.")


async def cp_rm(storage: StorageManager, context: commands.Context, amount: int):
    data: DndUserData = storage.users.get(context.author.id, "dnd_data")
    if data.selected_char and (char_data := data.chars.get(data.selected_char, None)):
        temp = char_data.inv.money.cp
        char_data.inv.money.cp = max(0, char_data.inv.money.cp - amount)
        await context.send(f"Copper: `{temp}` -> `{char_data.inv.money.cp}`")
    else:
        await context.send("Selected character is either None or invalid.")


async def cp_set(storage: StorageManager, context: commands.Context, amount: int):
    data: DndUserData = storage.users.get(context.author.id, "dnd_data")
    if data.selected_char and (char_data := data.chars.get(data.selected_char, None)):
        temp = char_data.inv.money.cp
        char_data.inv.money.cp = max(0, amount)
        await context.send(f"Copper: `{temp}` -> `{char_data.inv.money.cp}`")
    else:
        await context.send("Selected character is either None or invalid.")


async def sp_add(storage: StorageManager, context: commands.Context, amount: int):
    data: DndUserData = storage.users.get(context.author.id, "dnd_data")
    if data.selected_char and (char_data := data.chars.get(data.selected_char, None)):
        temp = char_data.inv.money.sp
        char_data.inv.money.sp += amount
        await context.send(f"Silver: `{temp}` -> `{char_data.inv.money.sp}`")
    else:
        await context.send("Selected character is either None or invalid.")


async def sp_rm(storage: StorageManager, context: commands.Context, amount: int):
    data: DndUserData = storage.users.get(context.author.id, "dnd_data")
    if data.selected_char and (char_data := data.chars.get(data.selected_char, None)):
        temp = char_data.inv.money.sp
        char_data.inv.money.sp = max(0, char_data.inv.money.sp - amount)
        await context.send(f"Silver: `{temp}` -> `{char_data.inv.money.sp}`")
    else:
        await context.send("Selected character is either None or invalid.")


async def sp_set(storage: StorageManager, context: commands.Context, amount: int):
    data: DndUserData = storage.users.get(context.author.id, "dnd_data")
    if data.selected_char and (char_data := data.chars.get(data.selected_char, None)):
        temp = char_data.inv.money.sp
        char_data.inv.money.sp = max(0, amount)
        await context.send(f"Silver: `{temp}` -> `{char_data.inv.money.sp}`")
    else:
        await context.send("Selected character is either None or invalid.")


async def ep_add(storage: StorageManager, context: commands.Context, amount: int):
    data: DndUserData = storage.users.get(context.author.id, "dnd_data")
    if data.selected_char and (char_data := data.chars.get(data.selected_char, None)):
        temp = char_data.inv.money.ep
        char_data.inv.money.ep += amount
        await context.send(f"Electrum: `{temp}` -> `{char_data.inv.money.ep}`")
    else:
        await context.send("Selected character is either None or invalid.")


async def ep_rm(storage: StorageManager, context: commands.Context, amount: int):
    data: DndUserData = storage.users.get(context.author.id, "dnd_data")
    if data.selected_char and (char_data := data.chars.get(data.selected_char, None)):
        temp = char_data.inv.money.ep
        char_data.inv.money.ep = max(0, char_data.inv.money.ep - amount)
        await context.send(f"Electrum: `{temp}` -> `{char_data.inv.money.ep}`")
    else:
        await context.send("Selected character is either None or invalid.")


async def ep_set(storage: StorageManager, context: commands.Context, amount: int):
    data: DndUserData = storage.users.get(context.author.id, "dnd_data")
    if data.selected_char and (char_data := data.chars.get(data.selected_char, None)):
        temp = char_data.inv.money.ep
        char_data.inv.money.ep = max(0, amount)
        await context.send(f"Electrum: `{temp}` -> `{char_data.inv.money.ep}`")
    else:
        await context.send("Selected character is either None or invalid.")


async def gp_add(storage: StorageManager, context: commands.Context, amount: int):
    data: DndUserData = storage.users.get(context.author.id, "dnd_data")
    if data.selected_char and (char_data := data.chars.get(data.selected_char, None)):
        temp = char_data.inv.money.gp
        char_data.inv.money.gp += amount
        await context.send(f"Gold: `{temp}` -> `{char_data.inv.money.gp}`")
    else:
        await context.send("Selected character is either None or invalid.")


async def gp_rm(storage: StorageManager, context: commands.Context, amount: int):
    data: DndUserData = storage.users.get(context.author.id, "dnd_data")
    if data.selected_char and (char_data := data.chars.get(data.selected_char, None)):
        temp = char_data.inv.money.gp
        char_data.inv.money.gp = max(0, char_data.inv.money.gp - amount)
        await context.send(f"Gold: `{temp}` -> `{char_data.inv.money.gp}`")
    else:
        await context.send("Selected character is either None or invalid.")


async def gp_set(storage: StorageManager, context: commands.Context, amount: int):
    data: DndUserData = storage.users.get(context.author.id, "dnd_data")
    if data.selected_char and (char_data := data.chars.get(data.selected_char, None)):
        temp = char_data.inv.money.gp
        char_data.inv.money.gp = max(0, amount)
        await context.send(f"Gold: `{temp}` -> `{char_data.inv.money.gp}`")
    else:
        await context.send("Selected character is either None or invalid.")


async def pp_add(storage: StorageManager, context: commands.Context, amount: int):
    data: DndUserData = storage.users.get(context.author.id, "dnd_data")
    if data.selected_char and (char_data := data.chars.get(data.selected_char, None)):
        temp = char_data.inv.money.pp
        char_data.inv.money.pp += amount
        await context.send(f"Platinum: `{temp}` -> `{char_data.inv.money.pp}`")
    else:
        await context.send("Selected character is either None or invalid.")


async def pp_rm(storage: StorageManager, context: commands.Context, amount: int):
    data: DndUserData = storage.users.get(context.author.id, "dnd_data")
    if data.selected_char and (char_data := data.chars.get(data.selected_char, None)):
        temp = char_data.inv.money.pp
        char_data.inv.money.pp = max(0, char_data.inv.money.pp - amount)
        await context.send(f"Platinum: `{temp}` -> `{char_data.inv.money.pp}`")
    else:
        await context.send("Selected character is either None or invalid.")


async def pp_set(storage: StorageManager, context: commands.Context, amount: int):
    data: DndUserData = storage.users.get(context.author.id, "dnd_data")
    if data.selected_char and (char_data := data.chars.get(data.selected_char, None)):
        temp = char_data.inv.money.pp
        char_data.inv.money.pp = max(0, amount)
        await context.send(f"Platinum: `{temp}` -> `{char_data.inv.money.pp}`")
    else:
        await context.send("Selected character is either None or invalid.")

