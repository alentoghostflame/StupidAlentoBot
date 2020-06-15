from misc_module.storage import WelcomeConfig
from misc_module.welcomes.commands import text
from discord.ext import commands
import misc_module.text
import logging
import discord
import typing
import re


logger = logging.getLogger("main_bot")


async def welcome_control(welcome_config: WelcomeConfig, context: commands.Context, arg1: str, arg2: str, *args):
    if args:
        await context.send(text.WELCOME_CONTROL_TOO_MANY_ARGS)
    elif arg1 not in {"toggle", "add", "remove", "rm", "list", "set"}:
        await context.send(text.WELCOME_CONTROL_MISSING_ARG_1)
    elif arg1 == "list":
        await send_list_embed(welcome_config, context)
    elif arg1 == "toggle":
        await toggle_welcomes(welcome_config, context)
    elif arg1 == "add":
        await add_welcome(welcome_config, context, arg2)
    elif arg1 in {"remove", "rm"}:
        await remove_welcome(welcome_config, context, arg2)
    elif arg1 == "set":
        await set_welcome_channel(welcome_config, context, arg2)
    else:
        await context.send(f"WELCOME_CONTROL: ALL ELIFS PASSED, YOU HAVE A HOLE SOMEWHERE! \"{arg1}\", "
                           f"\"{arg2}\". SEND THIS TO ALENTO GHOSTFLAME!")


async def send_list_embed(welcome_config: WelcomeConfig, context: commands.Context):
    embed = discord.Embed(title="Welcome Info", color=0x00ff00)

    embed.add_field(name="Enabled", value=str(welcome_config.enabled))

    if welcome_config.welcome_channel_id:
        channel: discord.TextChannel = context.guild.get_channel(welcome_config.welcome_channel_id)
        if channel:
            embed.add_field(name="Channel", value=channel.mention)
        else:
            embed.add_field(name="Channel", value=str(welcome_config.welcome_channel_id))
    else:
        embed.add_field(name="Channel", value="None")

    if welcome_config.messages:
        message_text = ""
        count = 1
        for message in welcome_config.messages:
            message_text += f"{count}) ``{message}`` \n"
            count += 1
        embed.add_field(name="Messages", value=message_text, inline=False)
    else:
        embed.add_field(name="Messages", value="None", inline=False)

    await context.send(embed=embed)


async def toggle_welcomes(welcome_config: WelcomeConfig, context: commands.Context):
    if welcome_config.enabled:
        welcome_config.enabled = False
        await context.send(text.WELCOME_CONTROL_TOGGLE_OFF)
    else:
        welcome_config.enabled = True
        await context.send(text.WELCOME_CONTROL_TOGGLE_ON)


async def add_welcome(welcome_config: WelcomeConfig, context: commands.Context, welcome_string: str):
    if welcome_string:
        welcome_config.messages.append(welcome_string)
        await context.send(text.WELCOME_CONTROL_ADD_SUCCESS.format(welcome_string.replace("```", "``\u200b`")))
    else:
        await context.send(text.WELCOME_CONTROL_ADD_MISSING_ARG)


async def remove_welcome(welcome_config: WelcomeConfig, context: commands.Context, index_string: str):
    if index_string.isdecimal():
        index = int(index_string) - 1
        if index < len(welcome_config.messages):
            welcome_config.messages.pop(index)
            await context.send(text.WELCOME_CONTROL_REMOVE_SUCCESS)
        else:
            await context.send(text.WELCOME_CONTROL_REMOVE_INDEX_OOB)
    else:
        await context.send(text.WELCOME_CONTROL_REMOVE_MISSING_ARG)


async def set_welcome_channel(welcome_config: WelcomeConfig, context: commands.Context, channel_id_string: str):
    channel_id = get_numbers(channel_id_string)
    channel: discord.TextChannel = context.guild.get_channel(channel_id)
    if channel:
        welcome_config.welcome_channel_id = channel.id
        await context.send(text.WELCOME_CONTROL_SET_SUCCESS.format(channel.mention))
    else:
        await context.send(text.WELCOME_CONTROL_SET_INVALID_ARG)


def get_numbers(string: str) -> typing.Optional[int]:
    if string:
        comp = re.compile("(\\d+)")
        num_list = comp.findall(string)

        if num_list:
            return int("".join(num_list))
    return None
