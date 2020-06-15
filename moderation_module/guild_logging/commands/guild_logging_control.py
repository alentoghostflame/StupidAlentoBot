from moderation_module.guild_logging.commands import text
from moderation_module.storage import GuildLoggingConfig
from discord.ext import commands
import moderation_module.text
import logging
import discord
import typing
import re


logger = logging.getLogger("main_bot")


async def guild_logging_control(log_config: GuildLoggingConfig, context: commands.Context, arg1, arg2):
    if arg1 not in ("list", "toggle", "bots", "readd", "remove", "rm", "set"):
        await context.send(text.GUILD_LOGGING_CONTROL_TOGGLE_MISSING_ARG_1)
    elif arg1 == "list":
        await send_list_embed(log_config, context)
    elif not context.author.guild_permissions.administrator:
        raise commands.MissingPermissions
    elif arg1 == "toggle":
        await toggle_guild_logging(log_config, context, arg2)
    elif arg1 == "bots":
        await toggle_bot_logging(log_config, context, arg2)
    elif arg1 == "readd":
        await readd_channel_to_logging(log_config, context, arg2)
    elif arg1 in ("remove", "rm"):
        await remove_channel_from_logging(log_config, context, arg2)
    elif arg1 == "set":
        await set_logging_channel(log_config, context, arg2)
    else:
        await context.send(f"WORD_BAN_CONTROL: ALL ELIFS PASSED, YOU HAVE A HOLE SOMEWHERE! \"{arg1}\", "
                           f"\"{arg2}\". SEND THIS TO ALENTO GHOSTFLAME!")


async def send_list_embed(log_config: GuildLoggingConfig, context: commands.Context):
    embed = discord.Embed(name="Logging Info")
    embed.add_field(name="Logging Enabled", value=str(log_config.toggled_on))
    embed.add_field(name="Log Bot Activity", value=str(log_config.log_bots))
    if log_config.log_channel_id:
        channel = context.guild.get_channel(log_config.log_channel_id)
        if channel:
            embed.add_field(name="Logging Channel", value=channel.mention)
        else:
            embed.add_field(name="Logging Channel", value=str(log_config.log_channel_id))
    else:
        embed.add_field(name="Logging channel", value="None")
    if log_config.exempt_channels:
        exempt_string = ""
        for channel_id in log_config.exempt_channels:
            channel: discord.TextChannel = context.guild.get_channel(channel_id)
            if channel:
                exempt_string += f"{channel.mention}\n"
            else:
                exempt_string += f"{channel_id}\n"
        embed.add_field(name="Exempt Channels", value=exempt_string)
    else:
        embed.add_field(name="Exempt Channels", value="None")
    await context.send(embed=embed)


async def toggle_guild_logging(log_config: GuildLoggingConfig, context: commands.Context, arg: str):
    if arg.lower() in ("true", "on", "enable", "online"):
        if log_config.toggled_on:
            await context.send(text.GUILD_LOGGING_CONTROL_TOGGLE_ALREADY_ENABLED)
        else:
            log_config.toggled_on = True
            await context.send(text.GUILD_LOGGING_CONTROL_TOGGLE_ENABLED)
    elif arg.lower() in ("false", "off", "disable", "offline"):
        if log_config.toggled_on:
            log_config.toggled_on = False
            await context.send(text.GUILD_LOGGING_CONTROL_TOGGLE_DISABLED)
        else:
            await context.send(text.GUILD_LOGGING_CONTROL_TOGGLE_ALREADY_DISABLED)
    else:
        await context.send(text.GUILD_LOGGING_CONTROL_TOGGLE_MISSING_ARG)


async def toggle_bot_logging(log_config: GuildLoggingConfig, context: commands.Context, arg: str):
    if arg.lower() in ("true", "on", "enable", "online"):
        if log_config.log_bots:
            await context.send(text.GUILD_LOGGING_CONTROL_BOTS_ALREADY_ENABLED)
        else:
            log_config.log_bots = True
            await context.send(text.GUILD_LOGGING_CONTROL_BOTS_ENABLED)
    elif arg.lower() in ("false", "off", "disable", "offline"):
        if log_config.log_bots:
            log_config.log_bots = False
            await context.send(text.GUILD_LOGGING_CONTROL_BOTS_DISABLED)
        else:
            await context.send(text.GUILD_LOGGING_CONTROL_BOTS_ALREADY_DISABLED)
    else:
        await context.send(text.GUILD_LOGGING_CONTROL_BOTS_MISSING_ARG)


async def readd_channel_to_logging(log_config: GuildLoggingConfig, context: commands.Context, arg: str):
    mention_id = get_numbers(arg)
    if mention_id in log_config.exempt_channels:
        log_config.exempt_channels.remove(mention_id)
        channel = context.guild.get_channel(mention_id)
        if channel:
            await context.send(text.GUILD_LOGGING_CONTROL_READD_SUCCESS.format(channel.mention))
        else:
            await context.send(text.GUILD_LOGGING_CONTROL_READD_SUCCESS.format(mention_id))
    else:
        await context.send(text.GUILD_LOGGING_CONTROL_READD_NOT_IN)


async def remove_channel_from_logging(log_config: GuildLoggingConfig, context: commands.Context, arg: str):
    mention_id = get_numbers(arg)
    channel = context.guild.get_channel(mention_id)
    if channel:
        if channel.id in log_config.exempt_channels:
            await context.send(text.GUILD_LOGGING_CONTROL_REMOVE_ALREADY.format(channel.mention))
        else:
            log_config.exempt_channels.add(channel.id)
            await context.send(text.GUILD_LOGGING_CONTROL_REMOVE_SUCCESS.format(channel.mention))
    else:
        await context.send(moderation_module.text.INVALID_CHANNEL)


async def set_logging_channel(log_config: GuildLoggingConfig, context: commands.Context, arg: str):
    mention_id = get_numbers(arg)
    channel = context.guild.get_channel(mention_id)
    if channel:
        log_config.log_channel_id = channel.id
        await context.send(text.GUILD_LOGGING_CONTROL_SET_SUCCESS.format(channel.mention))
    else:
        await context.send(moderation_module.text.INVALID_CHANNEL)


def get_numbers(string: str) -> typing.Optional[int]:
    if string:
        comp = re.compile("(\\d+)")
        num_list = comp.findall(string)

        if num_list:
            return int("".join(num_list))
    return None
