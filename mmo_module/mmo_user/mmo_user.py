from mmo_module.mmo_data import get_class_levels, CHARACTER_CLASSES
from mmo_module.mmo_controller import MMOServer
from datetime import datetime, timedelta
from mmo_module.mmo_user import text
from discord.ext import commands
from typing import Dict
import discord


async def enable(mmo_server: MMOServer, context: commands.Context):
    if mmo_server.user.enable(context.author.id):
        await context.send(text.MMO_USER_ENABLE)
    else:
        await context.send(text.MMO_USER_ALREADY_ENABLED)


async def disable(mmo_server: MMOServer, context: commands.Context):
    if mmo_server.user.disable(context.author.id):
        await context.send(text.MMO_USER_DISABLE)
    else:
        await context.send(text.MMO_USER_ALREADY_DISABLED)


async def status(mmo_server: MMOServer, context: commands.Context):
    if mmo_server.user.enabled(context.author.id):
        char_data = mmo_server.user.get(context.author.id)
        char_data.tick()

        embed = discord.Embed(title=f"{char_data.get_name()} Status")

        embed.add_field(name="Values", value=f"```{char_data.health.get_display(regen=True)}\n"
                                             f"{char_data.mana.get_display(2, regen=True)}\n"
                                             f"{char_data.xp.get_display(4)}```", inline=False)
        embed.add_field(name="Attack", value=f"Physical: {char_data.physical_damage} "
                                             f"Magical: {char_data.magical_damage}")
        embed.add_field(name="Class", value=char_data.char_class.name.capitalize())

        await context.send(embed=embed)
    else:
        await context.send(text.MMO_CURRENTLY_DISABLED)


async def battle(mmo_server: MMOServer, context: commands.Context):
    if mmo_server.user.enabled(context.author.id):
        pass
    else:
        await context.send(text.MMO_CURRENTLY_DISABLED)


async def set_class(mmo_server: MMOServer, cooldowns: Dict[int, datetime], context: commands.Context, class_name: str):
    if mmo_server.user.enabled(context.author.id):
        char_data = mmo_server.user.get(context.author.id)
        char_data.tick()
        char_class = CHARACTER_CLASSES.get(class_name.lower(), None)
        if char_class:
            char_class = char_class()
        if char_class is None:
            await context.send(text.MMO_CLASS_NOT_FOUND)
        elif char_class.min_level > char_data.xp.get_level():
            await context.send(text.MMO_CLASS_DONT_MEET_LEVEL)
        elif context.author.id in cooldowns and datetime.utcnow() < cooldowns[context.author.id]:
            await context.send(text.MMO_CLASS_ON_COOLDOWN.format(datetime.utcnow() - cooldowns[context.author.id]))
        else:
            char_data.set_class(char_class)
            cooldowns[context.author.id] = datetime.utcnow() + timedelta(hours=2)
            await context.send(text.MMO_CLASS_CHOSEN.format(char_data.get_name(), char_class.name))
    else:
        await context.send(text.MMO_CURRENTLY_DISABLED)


async def send_class_display(mmo_server: MMOServer, context: commands.Context):
    if mmo_server.user.enabled(context.author.id):
        char_data = mmo_server.user.get(context.author.id)
        char_data.tick()
        level_thresholds, char_class_dict = get_class_levels()

        available_classes = ""
        unavailable_classes = ""
        for level_threshold in level_thresholds:
            if char_data.xp.get_level() < level_threshold:
                unavailable_classes += f"{level_threshold}: {', '.join(char_class_dict[level_threshold])}\n"
                pass
            else:
                available_classes += f"{level_threshold}: {', '.join(char_class_dict[level_threshold])}\n"

        if not available_classes:
            available_classes = "None"
        if not unavailable_classes:
            unavailable_classes = "None"

        embed = discord.Embed(title="Classes", color=0x29df64)
        embed.add_field(name="Available", value=available_classes, inline=False)
        embed.add_field(name="Unavailable", value=unavailable_classes, inline=False)

        await context.send(embed=embed)
    else:
        await context.send(text.MMO_CURRENTLY_DISABLED)
