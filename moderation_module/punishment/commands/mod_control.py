from moderation_module.storage.punishment_data import PunishmentConfig
from moderation_module.punishment.commands import text
from discord.ext import commands
import moderation_module.text
import logging
import discord
import typing
import re


logger = logging.getLogger("main_bot")


async def mod_control(guild_data: PunishmentConfig, context: commands.Context, arg1, arg2, arg3):
    if arg1 not in ("warn", "mute", "list"):
        await context.send(text.MOD_CONTROL_MISSING_ARG_1)
    elif arg1 == "list":
        await send_list_embed(guild_data, context)
    elif arg2 not in ("add", "remove", "rm", "set"):
        await context.send(text.MOD_CONTROL_MISSING_ARG_2.format(arg1))
    elif not get_numbers(arg3):
        await context.send(text.MOD_CONTROL_MISSING_ARG_3.format(arg1, arg2))
    elif arg2 == "add":
        await add_role(guild_data, context, arg1, arg3)
    elif arg2 in ("remove", "rm"):
        await remove_role(guild_data, context, arg1, arg3)
    elif arg2 == "set":
        await set_role(guild_data, context, arg1, arg3)
    else:
        await context.send(f"MOD_CONTROL: ALL ELIFS PASSED, YOU HAVE A HOLE SOMEWHERE! \"{arg1}\", "
                           f"\"{arg2}\", \"{arg3}\". SEND THIS TO ALENTO GHOSTFLAME!")


async def send_list_embed(punish_config: PunishmentConfig, context: commands.Context):
    embed = discord.Embed(title="Info")
    guild: discord.Guild = context.guild

    if punish_config.warner_roles:
        temp_string = ""
        for role_id in punish_config.warner_roles:
            role = guild.get_role(role_id)
            if role:
                temp_string += f"{role.mention}\n"
            else:
                temp_string += f"{role_id}\n"
        embed.add_field(name="Warner Roles", value=temp_string)
    else:
        embed.add_field(name="Warner Roles", value="N/A")

    if punish_config.warn_role_id:
        role = guild.get_role(punish_config.warn_role_id)
        if role:
            embed.add_field(name="Warned Role", value=role.mention)
        else:
            embed.add_field(name="Warned Role", value=str(punish_config.warn_role_id))
    else:
        embed.add_field(name="Warned Role", value="N/A")

    if punish_config.muter_roles:
        temp_string = ""
        for role_id in punish_config.muter_roles:
            role = guild.get_role(role_id)
            if role:
                temp_string += f"{role.mention}\n"
            else:
                temp_string += f"{role_id}\n"
        embed.add_field(name="Muter Roles", value=temp_string)
    else:
        embed.add_field(name="Muter Roles", value="N/A")

    if punish_config.mute_role_id:
        role = guild.get_role(punish_config.mute_role_id)
        if role:
            embed.add_field(name="Muted Role", value=role.mention)
        else:
            embed.add_field(name="Muted Role", value=str(punish_config.mute_role_id))
    else:
        embed.add_field(name="Muted Role", value="N/A")

    await context.send(embed=embed)


# async def add_role(punish_config: PunishmentConfig, context: commands.Context, arg1: str, mention_text: str):
#     mention_id = get_numbers(mention_text)
#     role = context.guild.get_role(mention_id)
async def add_role(punish_config: PunishmentConfig, context: commands.Context, arg1: str, role: discord.Role):
    if role:
        if arg1 == "warn":
            # guild_data.config["warner_roles"].add(role.id)
            punish_config.warner_roles.add(role.id)
            await context.send(text.MOD_CONTROL_ROLE_SET_SUCCESSFULLY.format("Warner"))
        elif arg1 == "mute":
            # guild_data.config["muter_roles"].add(role.id)
            punish_config.muter_roles.add(role.id)
            await context.send(text.MOD_CONTROL_ROLE_SET_SUCCESSFULLY.format("Muter"))
        else:
            await context.send(f"SET_ROLE: SOMEOTHER OTHER THAN PREVIOUS IF/ELIFS GIVEN, \"{arg1}\", SEND TO ALENTO "
                               f"GHOSTFLAME")
    else:
        await context.send(moderation_module.text.INVALID_ROLE)


# async def remove_role(punish_config: PunishmentConfig, context: commands.Context, arg1: str, mention_text: str):
#     mention_id = get_numbers(mention_text)
#     role = context.guild.get_role(mention_id)
async def remove_role(punish_config: PunishmentConfig, context: commands.Context, arg1: str, role: discord.Role):
    if role:
        if arg1 == "warn":
            # if role.id in guild_data.config["warner_roles"]:
            if role.id in punish_config.warner_roles:
                # guild_data.config["warner_roles"].remove(role.id)
                punish_config.warner_roles.remove(role.id)
                await context.send(text.MOD_CONTROL_ROLE_UNSET_SUCCESSFULLY.format("Warner"))
            else:
                await context.send(text.MOD_CONTROL_ROLE_NOT_FOUND_IN_STORAGE)
        elif arg1 == "mute":
            # if role.id in guild_data.config["muter_roles"]:
            if role.id in punish_config.muter_roles:
            #     guild_data.config["muter_roles"].remove(role.id)
                punish_config.muter_roles.remove(role.id)
                await context.send(text.MOD_CONTROL_ROLE_UNSET_SUCCESSFULLY.format("Muter"))
            else:
                await context.send(text.MOD_CONTROL_ROLE_NOT_FOUND_IN_STORAGE)
        else:
            await context.send(f"SET_ROLE: SOMEOTHER OTHER THAN PREVIOUS IF/ELIFS GIVEN, \"{arg1}\", SEND TO ALENTO "
                               f"GHOSTFLAME")
    else:
        await context.send(moderation_module.text.INVALID_ROLE)


# async def set_role(punish_config: PunishmentConfig, context: commands.Context, arg1: str, mention_text: str):
async def set_role(punish_config: PunishmentConfig, context: commands.Context, arg1: str, role: discord.Role):
    # mention_id = get_numbers(mention_text)
    # role = context.guild.get_role(mention_id)
    if role:
        if arg1 == "warn":
            # guild_data.config["warn_role_id"] = role.id
            punish_config.warn_role_id = role.id
            await context.send(text.MOD_CONTROL_ROLE_SET_SUCCESSFULLY.format("Warn"))
        elif arg1 == "mute":
            # guild_data.config["mute_role_id"] = role.id
            punish_config.mute_role_id = role.id
            await context.send(text.MOD_CONTROL_ROLE_SET_SUCCESSFULLY.format("Mute"))
        else:
            await context.send(f"SET_ROLE: SOMEOTHER OTHER THAN PREVIOUS IF/ELIFS GIVEN, \"{arg1}\", SEND TO ALENTO "
                               f"GHOSTFLAME")
    else:
        await context.send(moderation_module.text.INVALID_ROLE)


def get_numbers(string: str) -> typing.Optional[int]:
    if string:
        comp = re.compile("(\\d+)")
        num_list = comp.findall(string)

        if num_list:
            return int("".join(num_list))
    return None
