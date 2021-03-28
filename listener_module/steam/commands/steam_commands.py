from listener_module.steam.commands import text
from listener_module.steam.steam_announcement_data import SteamAnnouncementConfig
from discord.ext import commands
import logging
import discord
import typing
import re


logger = logging.getLogger("main_bot")


async def steam_announcement_control(steam_config: SteamAnnouncementConfig, context: commands.Context, arg1: str,
                                     arg2: str):
    if arg1 not in {"list", "toggle", "set", "add", "remove", "rm"}:
        await context.send(text.STEAM_CONTROL_MISSING_ARG_1)
    elif arg1 == "list":
        await send_list_embed(steam_config, context)
    elif arg1 == "toggle":
        await toggle_announcements(steam_config, context)
    elif arg1 == "set":
        await set_announcement_channel(steam_config, context, arg2)
    elif arg1 == "add":
        await add_game_to_track(steam_config, context, arg2)
    elif arg1 in {"remove", "rm"}:
        await remove_game_from_track(steam_config, context, arg2)
    else:
        await context.send(f"STEAM_ANNOUNCEMENT_CONTROL: ALL ELIFS PASSED, YOU HAVE A HOLE SOMEWHERE! \"{arg1}\", "
                           f"\"{arg2}\". SEND THIS TO ALENTO GHOSTFLAME!")


async def send_list_embed(steam_config: SteamAnnouncementConfig, context: commands.Context):
    embed = discord.Embed(title="Steam Announcements", color=0x1b2838)

    embed.add_field(name="Enabled", value=str(steam_config.enabled))

    if steam_config.announcement_channel_id:
        channel: discord.TextChannel = context.guild.get_channel(steam_config.announcement_channel_id)
        if channel:
            embed.add_field(name="Announcement Channel", value=channel.mention)
        else:
            embed.add_field(name="Announcement Channel", value=str(steam_config.announcement_channel_id))
    else:
        embed.add_field(name="Announcement Channel", value="None")

    if steam_config.tracked_game_ids:
        output_ids = ""
        for game_id in steam_config.tracked_game_ids:
            output_ids += f"`{game_id}`, "
        embed.add_field(name="Tracked Game IDs", value=output_ids, inline=False)
    else:
        embed.add_field(name="Tracked Game IDs", value="None")

    await context.send(embed=embed)


async def toggle_announcements(steam_config: SteamAnnouncementConfig, context: commands.Context):
    if steam_config.enabled:
        steam_config.enabled = False
        await context.send(text.STEAM_CONTROL_TOGGLE_OFF)
    else:
        steam_config.enabled = True
        await context.send(text.STEAM_CONTROL_TOGGLE_ON)


async def set_announcement_channel(steam_config: SteamAnnouncementConfig, context: commands.Context, argument: str):
    channel_id = get_numbers(argument)
    channel: discord.TextChannel = context.guild.get_channel(channel_id)
    if channel:
        steam_config.announcement_channel_id = channel.id
        await context.send(text.STEAM_CONTROL_SET_CHANNEL_SUCCESS)
    else:
        await context.send(text.STEAM_CONTROL_SET_CHANNEL_INVALID_ARG)


async def add_game_to_track(steam_config: SteamAnnouncementConfig, context: commands.Context, argument: str):
    steam_id = get_numbers(argument)
    if steam_id:
        if steam_id in steam_config.tracked_game_ids:
            await context.send(text.STEAM_CONTROL_ADD_DUPLICATE)
        else:
            steam_config.tracked_game_ids.add(steam_id)
            await context.send(text.STEAM_CONTROL_ADD_SUCCESS)
    else:
        await context.send(text.STEAM_CONTROL_ADD_INVALID_ARG)


async def remove_game_from_track(steam_config: SteamAnnouncementConfig, context: commands.Context, argument: str):
    steam_id = get_numbers(argument)
    if steam_id in steam_config.tracked_game_ids:
        steam_config.tracked_game_ids.remove(steam_id)
        await context.send(text.STEAM_CONTROL_REMOVE_SUCCESS)
    else:
        await context.send(text.STEAM_CONTROL_REMOVE_INVALID_ARG)


def get_numbers(string: str) -> typing.Optional[int]:
    if string:
        comp = re.compile("(\\d+)")
        num_list = comp.findall(string)

        if num_list:
            return int("".join(num_list))
    return None
