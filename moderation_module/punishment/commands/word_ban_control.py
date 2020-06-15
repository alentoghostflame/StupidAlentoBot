from moderation_module.storage import WordBanConfig
from moderation_module.punishment.commands import text
from discord.ext import commands
import logging
import discord


logger = logging.getLogger("main_bot")


async def word_ban_control(ban_config: WordBanConfig, context: commands.Context, arg1, *args):
    arg2 = " ".join(args)
    if arg1 not in ("list", "toggle", "add", "remove", "rm"):
        await context.send(text.WORD_BAN_CONTROL_MISSING_ARG_1)
    elif arg1 == "list":
        await send_list_embed(ban_config, context)
    elif not context.author.guild_permissions.administrator:
        raise commands.MissingPermissions
    elif not args:
        await context.send(text.WORD_BAN_CONTROL_MISSING_ARG_2.format(arg1))
    elif arg1 == "toggle":
        await toggle_word_ban(ban_config, context, arg2)
    elif arg1 == "add":
        await add_word_to_ban(ban_config, context, arg2)
    elif arg1 in ("remove", "rm"):
        await remove_word_from_ban(ban_config, context, arg2)
    else:
        await context.send(f"WORD_BAN_CONTROL: ALL ELIFS PASSED, YOU HAVE A HOLE SOMEWHERE! \"{arg1}\", "
                           f"\"{arg2}\". SEND THIS TO ALENTO GHOSTFLAME!")


async def send_list_embed(ban_config: WordBanConfig, context: commands.Context):
    embed = discord.Embed(title="WordBan List")
    embed.add_field(name="Enabled", value=str(ban_config.toggled_on))
    if ban_config.banned_words:
        banned_words = ""
        for banned_word in ban_config.banned_words:
            banned_words += f"{banned_word}\n"
        embed.add_field(name="Banned Words", value=f"||{banned_words}||")
    else:
        embed.add_field(name="Banned Words", value="N/A")
    await context.send(embed=embed)


async def toggle_word_ban(ban_config: WordBanConfig, context: commands.Context, arg: str):
    if arg.lower() in ("true", "on", "enable", "online"):
        if ban_config.toggled_on:
            await context.send(text.WORD_BAN_CONTROL_TOGGLE_ALREADY_ENABLED)
        else:
            ban_config.toggled_on = True
            await context.send(text.WORD_BAN_CONTROL_TOGGLE_ENABLED)
    elif arg.lower() in ("false", "off", "disable", "offline"):
        if ban_config.toggled_on:
            ban_config.toggled_on = False
            await context.send(text.WORD_BAN_CONTROL_TOGGLE_DISABLED)
        else:
            await context.send(text.WORD_BAN_CONTROL_TOGGLE_ALREADY_DISABLED)
    else:
        await context.send(text.WORD_BAN_CONTROL_TOGGLE_MISSING_ARG)


async def add_word_to_ban(ban_config: WordBanConfig, context: commands.Context, arg: str):
    ban_config.banned_words.add(arg.lower())
    await context.send(text.WORD_BAN_CONTROL_WORD_ADDED_TO_BAN.format(arg.lower()))


async def remove_word_from_ban(ban_config: WordBanConfig, context: commands.Context, arg: str):
    if arg in ban_config.banned_words:
        ban_config.banned_words.remove(arg.lower())
        await context.send(text.WORD_BAN_CONTROL_WORD_REMOVED_FROM_BAN.format(arg.lower()))
    else:
        await context.send(text.WORD_BAN_CONTROL_WORD_NOT_BANNED.format(arg.lower()))
