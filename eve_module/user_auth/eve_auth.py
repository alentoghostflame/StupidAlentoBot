from eve_module.user_auth import text
from eve_module.storage import EVEUserAuthManager, ESIUnauthorized, ESIInvalidAuthCode
from discord.ext import commands
import urllib.parse
import logging
import discord
import typing
import re


logger = logging.getLogger("main_bot")


async def send_help_embed(context: commands.Context):
    embed = discord.Embed(title="Authorization Manager", color=0x121A1D)

    embed.add_field(name="Description", value=text.EVE_AUTH_CONTROL_HELP_DESCRIPTION, inline=False)
    embed.add_field(name="Authorizing", value=text.EVE_AUTH_CONTROL_HELP_AUTHORIZING, inline=False)
    embed.add_field(name="Utility", value=text.EVE_AUTH_CONTROL_HELP_UTILITY, inline=False)
    embed.add_field(name="Information", value=text.EVE_AUTH_CONTROL_HELP_INFORMATION, inline=False)

    await context.send(embed=embed)


async def get_access_token(user_auth: EVEUserAuthManager, context: commands.Context):
    """
    THIS IS DEBUG STUFF, REMOVE WHEN DONE!
    :param user_auth:
    :param context:
    :return:
    """
    selected_id = user_auth.get_selected(context.author.id)
    if selected_id:
        await context.send(f"`{await user_auth.get_access_token(context.author.id, selected_id)}`")
    else:
        await context.send("You don't seem to have a selected character.")


async def send_list_embed(user_auth: EVEUserAuthManager, context: commands.Context, id_string: str = None):
    if id_string:
        await send_character_info_embed(user_auth, context, id_string)
    else:
        await send_auth_list_embed(user_auth, context)


async def send_auth_list_embed(user_auth: EVEUserAuthManager, context: commands.Context):
    embed = discord.Embed(title="Auth Info", color=0x121A1D)

    char_ids, char_names = user_auth.get_all_names(context.author.id)

    if char_ids:
        character_text = ""
        for i in range(len(char_ids)):
            character_text += f"{char_ids[i]} | {char_names[i]}\n"
        embed.add_field(name="Characters", value=character_text)
    else:
        embed.add_field(name="Characters", value="None")

    selected_id = user_auth.get_selected(context.author.id)
    if selected_id:
        selected_name = user_auth.get_name(context.author.id, selected_id)
        embed.add_field(name="Selected", value=f"{selected_id} | {selected_name}")
    else:
        embed.add_field(name="Selected", value="None")

    await context.send(embed=embed)


async def delete_character(user_auth: EVEUserAuthManager, context: commands.Context, id_string: str):
    character_id = get_numbers(id_string)
    if character_id:
        if character_id == user_auth.get_selected(context.author.id):
            user_auth.set_selected(context.author.id, 0)

        if user_auth.delete_character(context.author.id, character_id):
            await context.send(text.EVE_AUTH_CONTROL_DELETE_SUCCESS)
        else:
            await context.send(text.CHARACTER_ID_NOT_FOUND)
    else:
        await context.send(text.EVE_AUTH_CONTROL_DELETE_MISSING_ARG)


async def select_character(user_auth: EVEUserAuthManager, context: commands.Context, id_string: str):
    character_id = get_numbers(id_string)
    if character_id:
        character_name = user_auth.get_name(context.author.id, character_id)
        if character_name:
            user_auth.set_selected(context.author.id, character_id)
            await context.send(text.EVE_AUTH_CONTROL_SELECT_SUCCESS.format(character_name))
        else:
            await context.send(text.CHARACTER_ID_NOT_FOUND)
    else:
        await context.send(text.EVE_AUTH_CONTROL_SELECT_MISSING_ARG)


async def send_character_info_embed(user_auth: EVEUserAuthManager, context: commands, id_string: str):
    character_id = get_numbers(id_string)
    if character_id:
        character_name = user_auth.get_name(context.author.id, character_id)
        if character_name:
            embed = discord.Embed(title="Character Info", color=0x121A1D)
            embed.set_author(name=character_name)
            embed.add_field(name="ID", value=f"`{character_id}`")

            permission_text = ""
            permission_dict = user_auth.get_current_scopes(context.author.id, character_id)
            for permission in permission_dict:
                permission_text += f"{permission}: {str(permission_dict[permission])}\n"
            embed.add_field(name="Permission Nodes", value=f"```yaml\n{permission_text}```")

            await context.send(embed=embed)
        else:
            await context.send(text.CHARACTER_ID_NOT_FOUND)
    else:
        await context.send(text.EVE_AUTH_CONTROL_INFO_MISSING_ARG)


async def send_update_url(user_auth: EVEUserAuthManager, context: commands.Context, arg: str):
    selected_id = user_auth.get_selected(context.author.id)
    if not selected_id:
        await context.send(text.NO_AUTH_SELECTED_CHARACTER)
    elif user_auth.get_selected_scopes(context.author.id) != user_auth.get_selected_desired_scopes(context.author.id) \
            or (arg and arg.lower() == "force"):
        await context.send(text.EVE_AUTH_CONTROL_UPDATE_SUCCESS.format(user_auth.get_desired_eve_auth_url(
            context.author.id, selected_id)))
    elif arg and arg.lower() != "force":
        await context.send(text.EVE_AUTH_CONTROL_UPDATE_ARG_NOT_FORCE)
    elif user_auth.get_selected_scopes(context.author.id) == user_auth.get_selected_desired_scopes(context.author.id):
        await context.send(text.EVE_AUTH_CONTROL_UPDATE_CURRENT_DESIRED_EQUAL)
    else:
        await context.send(f"SEND_UPDATE_URL: ALL ELIFS PASSED, YOU HAVE A HOLE SOMEWHERE! \"{arg}\". "
                           f"SEND THIS TO ALENTO/SOMBRA GHOSTFLAME!")


async def register_token(user_auth: EVEUserAuthManager, context: commands.Context, url_string: str):
    if url_string:
        url_split = url_string.split("?")
        if len(url_split) > 1:
            queries = urllib.parse.parse_qs(url_split[1])
            if queries.get("code", None):
                try:
                    character_name = await user_auth.register_refresh_token(context.author.id, queries["code"][0])
                    if character_name:
                        await context.send(text.EVE_AUTH_CONTROL_REGISTER_SUCCESS.format(character_name))
                    else:
                        await context.send(text.EVE_AUTH_CONTROL_REGISTER_TOKEN_INVALID)
                except ESIInvalidAuthCode:
                    await context.send(text.EVE_AUTH_CONTROL_REGISTER_TOKEN_INVALID)
            else:
                await context.send(text.EVE_AUTH_CONTROL_REGISTER_TOKEN_INVALID)
        else:
            await context.send(text.EVE_AUTH_CONTROL_REGISTER_TOKEN_INVALID)
    else:
        await context.send(text.EVE_AUTH_CONTROL_REGISTER_TOKEN_MISSING_ARG)


def get_numbers(string: str) -> typing.Optional[int]:
    if string:
        comp = re.compile("(\\d+)")
        num_list = comp.findall(string)

        if num_list:
            return int("".join(num_list))
    return None

