from self_roles_module.storage import RoleSelfAssignData
from self_roles_module import text
from discord.ext import commands
import logging
import discord
import typing
import re


logger = logging.getLogger("main_bot")


async def send_help_embed(context: commands.Context):
    embed = discord.Embed(title="Self Assigned Roles", color=0x800080)

    embed.add_field(name="Description", value=text.ROLE_HELP_DESCRIPTION, inline=False)
    embed.add_field(name="Usage", value=text.ROLE_HELP_USAGE, inline=False)
    embed.add_field(name="Editing", value=text.ROLE_HELP_EDITING, inline=False)
    embed.add_field(name="Information", value=text.ROLE_HELP_INFORMATION, inline=False)

    await context.send(embed=embed)


async def send_list_embed(guild_data: RoleSelfAssignData, context: commands.Context, role_keyword: str):
    if not role_keyword:
        await send_list_embed_no_role(guild_data, context)
    elif role_keyword.lower() not in guild_data.roles:
        await context.send(text.ROLE_KEYWORD_NOT_FOUND.format(role_keyword.lower()))
    else:
        role = context.guild.get_role(guild_data.roles[role_keyword.lower()])
        if role:
            await send_list_embed_role(context, role)
        else:
            await context.send(text.ROLE_NO_LONGER_IN_GUILD)


async def send_list_embed_no_role(guild_data: RoleSelfAssignData, context: commands.Context):
    embed = discord.Embed(title="Role Info")
    guild: discord.Guild = context.guild

    if guild_data.roles:
        temp_string = ""
        for role_keyword in guild_data.roles:
            role = guild.get_role(guild_data.roles[role_keyword])
            if role:
                temp_string += f"{role_keyword} | {role.mention}\n"
            else:
                temp_string += f"{role_keyword} | {guild_data.roles[role_keyword]}\n"
        embed.add_field(name="Keyword | Role", value=temp_string, inline=False)
    else:
        embed.add_field(name="Keyword | Role", value="None | None", inline=False)

    await context.send(embed=embed)


async def send_list_embed_role(context: commands.Context, role: discord.Role):
    embed = discord.Embed(title=f"{role.name}")

    if role.members:
        member_text = ""
        for member in role.members:
            member_text += f"{member.mention}\n"
        embed.add_field(name=f"Count: {len(role.members)}", value=member_text, inline=False)
    else:
        embed.add_field(name="Count: 0", value="None", inline=False)

    await context.send(embed=embed)


async def toggle_user_role(guild_data: RoleSelfAssignData, context: commands.Context, role_keyword: str):
    role_id = guild_data.roles[role_keyword.lower()]
    role = context.guild.get_role(role_id)
    if role:
        if role in context.author.roles:
            await context.author.remove_roles(role, reason="They asked for it, really!")
            await context.send(text.ROLE_TOGGLE_REMOVED)
        else:
            await context.author.add_roles(role, reason="They asked for it.")
            await context.send(text.ROLE_TOGGLE_ADDED)
    else:
        await context.send(text.ROLE_NO_LONGER_IN_GUILD)


async def add_role(guild_data: RoleSelfAssignData, context: commands.Context, role_keyword: str,
                   role_mention: discord.Role):
    if not role_keyword or not role_mention:
        await context.send(text.ROLE_ADD_MISSING_ARGS)
    else:
        guild_data.roles[role_keyword.lower()] = role_mention.id
        await context.send(text.ROLE_ADD_SUCCESS.format(role_keyword.lower(), role_mention.name))


async def remove_self_role(guild_data: RoleSelfAssignData, context: commands, role_keyword: str):
    if not role_keyword:
        await context.send(text.ROLE_REMOVE_MISSING_ARGS)
    elif role_keyword not in guild_data.roles:
        await context.send(text.ROLE_KEYWORD_NOT_FOUND.format(role_keyword.lower()))
    else:
        guild_data.roles.pop(role_keyword.lower())
        await context.send(text.ROLE_REMOVE_SUCCESS.format(role_keyword.lower()))


def get_numbers(string: str) -> typing.Optional[int]:
    if string:
        comp = re.compile("(\\d+)")
        num_list = comp.findall(string)

        if num_list:
            return int("".join(num_list))
    return None
