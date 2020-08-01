from moderation_module.storage.punishment_data import PunishmentManager, PunishmentConfig
from moderation_module.punishment.commands import text
from datetime import datetime, timedelta
from discord.ext import commands
import moderation_module.text
import logging
import discord
import typing
import re


logger = logging.getLogger("main_bot")


async def warn_cmd(punish_manager: PunishmentManager, punish_config: PunishmentConfig, context: commands.Context,
                   mention: str):
    member: discord.Member = context.guild.get_member(get_numbers(mention))
    warn_role: discord.Role = context.guild.get_role(punish_config.warn_role_id)

    if not has_any_role(context.guild, punish_config.warner_roles, context.author) and not \
            context.author.guild_permissions.administrator:
        await context.send(moderation_module.text.MISSING_PERMISSIONS)
    elif not mention:
        await context.send(text.PUNISH_USE.format("warn"))
    elif not member:
        await context.send(moderation_module.text.INVALID_MEMBER)
    elif has_any_role(context.guild, punish_config.warner_roles, member) or member.guild_permissions.administrator:
        await context.send(text.PUNISH_INVALID_TARGET.format("warn", "warner"))
    elif not warn_role:
        await context.send(text.PUNISH_MISSING_PUNISH_ROLE.format("warning"))
    elif warn_role in member.roles:
        mute_role = context.guild.get_role(punish_config.mute_role_id)
        if mute_role:
            await warn(punish_manager, warn_role, context.guild.id, member)
            await mute(punish_manager, mute_role, context.guild.id, member)
            await context.send(text.PUNISH_DOUBLE_WARN)
        else:
            await context.send(text.PUNISH_MISSING_PUNISH_ROLE.format("muting"))
    else:
        await warn(punish_manager, warn_role, context.guild.id, member)
        await context.send(text.PUNISH_WARN_SUCCESS)


async def mute_cmd(punish_manager: PunishmentManager, punish_config: PunishmentConfig, context: commands.Context,
                   mention: str):
    member: discord.Member = context.guild.get_member(get_numbers(mention))
    mute_role: discord.Role = context.guild.get_role(punish_config.mute_role_id)

    if not has_any_role(context.guild, punish_config.muter_roles, context.author) and not \
            context.author.guild_permissions.administrator:
        await context.send(moderation_module.text.MISSING_PERMISSIONS)
    elif not mention:
        await context.send(text.PUNISH_USE.format("mute"))
    elif not member:
        await context.send(moderation_module.text.INVALID_MEMBER)
    elif has_any_role(context.guild, punish_config.muter_roles, member) or member.guild_permissions.administrator:
        await context.send(text.PUNISH_INVALID_TARGET.format("mute", "muter"))
    elif not mute_role:
        await context.send(text.PUNISH_MISSING_PUNISH_ROLE.format("muting"))
    else:
        await mute(punish_manager, mute_role, context.guild.id, member)
        await context.send(text.PUNISH_MUTE_SUCCESS)


async def delete_message_and_warn(punish_manager: PunishmentManager, punish_config: PunishmentConfig,
                                  message: discord.Message, banned_word: str):
    await message.delete()
    warn_role: discord.Role = message.guild.get_role(punish_config.warn_role_id)
    if warn_role:
        if warn_role in message.author.roles:
            mute_role = message.guild.get_role(punish_config.mute_role_id)
            if mute_role:
                await mute(punish_manager, mute_role, message.guild.id, message.author)
                await message.channel.send(text.WORD_BAN_DELETE_DOUBLE_WARN_SUCCESS.format(banned_word.lower()))
            else:
                await message.channel.send(text.PUNISH_MISSING_PUNISH_ROLE.format("muting"))
        else:
            await warn(punish_manager, warn_role, message.guild.id, message.author)
            await message.channel.send(text.WORD_BAN_DELETE_WARN_SUCCESS.format(banned_word.lower()))
    else:
        await message.channel.send(text.PUNISH_MISSING_PUNISH_ROLE.format("warning"))


async def warn(punish_manager: PunishmentManager, warn_role: discord.Role, guild_id: int, member: discord.Member):
    await member.add_roles(warn_role, reason="Warned by the proper authorities.")
    punish_manager.create_warn(guild_id, member.id, datetime.utcnow(), datetime.utcnow() + timedelta(days=3))


async def mute(punish_manager: PunishmentManager, mute_role: discord.Role, guild_id: int, member: discord.Member):
    await member.add_roles(mute_role, reason="Muted by the proper authorities")
    punish_manager.create_mute(guild_id, member.id, datetime.utcnow(), datetime.utcnow() + timedelta(minutes=20))


def has_any_role(guild: discord.Guild, given_roles: set, member: discord.Member) -> bool:
    for role in given_roles:
        for user_role in member.roles:
            if guild.get_role(role) == user_role:
                return True
    return False


def get_numbers(string: str) -> typing.Optional[int]:
    if string:
        comp = re.compile("(\\d+)")
        num_list = comp.findall(string)

        if num_list:
            return int("".join(num_list))
    return None
