from faq_module.storage import FAQManager, FAQConfig
from faq_module.commands import text
from discord.ext import commands
import faq_module.text
import logging
import discord
import typing
import re


logger = logging.getLogger("main_bot")


async def faq_control(faq_manager: FAQManager, faq_config: FAQConfig, context: commands.Context, arg1: str, arg2: str,
                      arg3: str, arg4: str, *args):
    if args:
        await context.send(text.FAQ_CONTROL_TOO_MANY_ARGS)
    elif arg1 not in ("list", "add", "remove", "rm", "toggle", "role"):
        await context.send(text.FAQ_CONTROL_MISSING_ARG_1)
    elif arg1 == "list":
        await send_list_embed(faq_manager, faq_config, context)
    elif not has_any_role(context.guild, faq_config.edit_roles, context.author) and not \
            context.author.guild_permissions.administrator:
        await context.send(faq_module.text.MISSING_PERMISSIONS)
    elif arg1 == "add":
        await add_keyword(faq_manager, context, arg2, arg3, arg4)
    elif arg1 in {"remove", "rm"}:
        await remove_keyword(faq_manager, context, arg2)
    elif not context.author.guild_permissions.administrator:
        await context.send(faq_module.text.MISSING_PERMISSIONS)
    elif arg1 == "toggle":
        await toggle_faq(faq_config, context)
    elif arg1 == "role":
        if arg2 not in {"add", "remove", "rm"}:
            await context.send(text.FAQ_CONTROL_ROLE_MISSING_ARG_2)
        elif not arg3:
            await context.send(text.FAQ_CONTROL_ROLE_MISSING_ARG_3.format(arg2))
        elif arg2 == "add":
            await add_role(faq_config, context, arg3)
        elif arg2 in {"remove", "rm"}:
            await remove_role(faq_config, context, arg3)
        else:
            await context.send(f"FAQ_CONTROL.ROLE: ALL ELIFS PASSED, YOU HAVE A HOLE SOMEWHERE! \"{arg1}\", "
                               f"\"{arg2}\", \"{arg3}\". SEND THIS TO ALENTO GHOSTFLAME!")
    else:
        await context.send(f"FAQ_CONTROL: ALL ELIFS PASSED, YOU HAVE A HOLE SOMEWHERE! \"{arg1}\", "
                           f"\"{arg2}\", \"{arg3}\". SEND THIS TO ALENTO GHOSTFLAME!")


async def send_list_embed(faq_manager: FAQManager, faq_config: FAQConfig, context: commands.Context):
    embed = discord.Embed(title="FAQ Info", color=0x00ffff)

    embed.add_field(name="Enabled", value=str(faq_config.enabled))

    if faq_config.edit_roles:
        role_string = ""
        for role_id in faq_config.edit_roles:
            role: discord.Role = context.guild.get_role(role_id)
            if role:
                role_string += f"{role.mention}\n"
            else:
                role_string += f"{role_id}\n"
        embed.add_field(name="Edit Roles", value=role_string)
    else:
        embed.add_field(name="Edit Roles", value="None")

    keyword_set = faq_manager.get_keywords(context.guild.id)
    if keyword_set:
        keyword_string = ""
        for keyword in keyword_set:
            keyword_string += f"``{keyword}`` "
        embed.add_field(name="Keywords", value=keyword_string)
    else:
        embed.add_field(name="Keywords", value="None")

    embed.timestamp = context.message.created_at

    await context.send(embed=embed)


async def add_keyword(faq_manager: FAQManager, context: commands.Context, keyword: str, phrase: str, image_url: str):
    if not keyword or not phrase:
        await context.send(text.FAQ_CONTROL_ADD_KEYWORD_MISSING_ARGS)
    else:
        existed = False
        if keyword.lower() in faq_manager.get_keywords(context.guild.id):
            existed = True
        faq_manager.create(context.guild.id, keyword, phrase, image_url=image_url)
        if existed:
            await context.send(text.FAQ_CONTROL_ADD_KEYWORD_OVERWRITTEN.format(keyword))
        else:
            await context.send(text.FAQ_CONTROL_ADD_KEYWORD_SUCCESS.format(keyword))


async def remove_keyword(faq_manager: FAQManager, context: commands.Context, keyword: str):
    if keyword.lower() in faq_manager.get_keywords(context.guild.id):
        faq_manager.remove(context.guild.id, keyword)
        await context.send(text.FAQ_CONTROL_REMOVE_KEYWORD_SUCCESS.format(keyword.lower()))
    else:
        await context.send(text.FAQ_CONTROL_REMOVE_KEYWORD_NOT_FOUND.format(keyword.lower()))


async def toggle_faq(faq_config: FAQConfig, context: commands.Context):
    if faq_config.enabled:
        faq_config.enabled = False
        await context.send(text.FAQ_CONTROL_TOGGLE_DISABLED)
    else:
        faq_config.enabled = True
        await context.send(text.FAQ_CONTROL_TOGGLE_ENABLED)


async def add_role(faq_config: FAQConfig, context: commands.Context, role_argument: str):
    role_id = get_numbers(role_argument)
    role: discord.Role = context.guild.get_role(role_id)
    if role:
        if role.id in faq_config.edit_roles:
            await context.send(text.FAQ_CONTROL_ADD_ROLE_DUPLICATE.format(role.name))
        else:
            faq_config.edit_roles.add(role.id)
            await context.send(text.FAQ_CONTROL_ADD_ROLE_SUCCESS.format(role.name))


async def remove_role(faq_config: FAQConfig, context: commands.Context, role_argument: str):
    role_id = get_numbers(role_argument)
    if role_id in faq_config.edit_roles:
        faq_config.edit_roles.remove(role_id)
        await context.send(text.FAQ_CONTROL_REMOVE_ROLE_SUCCESS)
    else:
        await context.send(text.FAQ_CONTROL_REMOVE_ROLE_MISSING)


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
