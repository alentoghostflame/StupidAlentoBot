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

        embed = discord.Embed(title=f"{char_data.name}'s Status")

        embed.add_field(name="Values", value=f"```{char_data.stats.hp.get_display(regen=True)}\n"
                                             f"{char_data.stats.mp.get_display(2, regen=True)}\n"
                                             f"{char_data.stats.xp.get_display(4)}```", inline=False)
        embed.add_field(name="Attack", value=f"Physical: {char_data.stats.attack.physical} "
                                             f"Magical: {char_data.stats.attack.magical}")
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
        elif char_class.min_level > char_data.stats.xp.level:
            await context.send(text.MMO_CLASS_DONT_MEET_LEVEL)
        elif context.author.id in cooldowns and datetime.utcnow() < cooldowns[context.author.id]:
            await context.send(text.MMO_CLASS_ON_COOLDOWN.format(datetime.utcnow() - cooldowns[context.author.id]))
        else:
            char_data.char_class = char_class
            cooldowns[context.author.id] = datetime.utcnow() + timedelta(hours=2)
            await context.send(text.MMO_CLASS_CHOSEN.format(char_data.name, char_class.name))
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
            if char_data.stats.xp.level < level_threshold:
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


async def set_character_name(mmo_server: MMOServer, context: commands.Context, new_name: str):
    if mmo_server.user.enabled(context.author.id):
        char_data = mmo_server.user.get(context.author.id)
        char_data.name = new_name
        await context.send(text.MMO_NAME_SET.format(char_data.name))
    else:
        await context.send(text.MMO_CURRENTLY_DISABLED)


async def set_default_attack(mmo_server: MMOServer, context: commands.Context, spell_name: str):
    if mmo_server.user.enabled(context.author.id):
        char_data = mmo_server.user.get(context.author.id)
        found_spell = False
        for spell in char_data.char_class.spells:
            if spell_name.lower() == spell.name.lower():
                found_spell = True
                char_data.default_spell = spell
                break
        if found_spell:
            await context.send(text.MMO_DEFAULT_SPELL_SET.format(char_data.default_spell.name))
        else:
            await context.send(text.MMO_DEFAULT_SPELL_BAD.format(spell_name))
    else:
        await context.send(text.MMO_CURRENTLY_DISABLED)


async def send_ability_display(mmo_server: MMOServer, context: commands.Context):
    if mmo_server.user.enabled(context.author.id):
        char_data = mmo_server.user.get(context.author.id)
        embed = discord.Embed(title="Spells", color=0x00ccff)
        spell_text = ""
        for spell in char_data.char_class.spells:
            spell_text += f"{spell.name} : {spell.mana_cost} MP : {spell.brief}\n"
        embed.add_field(name="Available", value=spell_text, inline=False)
        default_spell_text = f"{char_data.default_spell.name} : {char_data.default_spell.mana_cost}"
        embed.add_field(name="Default", value=default_spell_text, inline=False)

        await context.send(embed=embed)
    else:
        await context.send(text.MMO_CURRENTLY_DISABLED)
