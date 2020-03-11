from discord.ext import commands
import misc_module.text as text
import universal_module.utils
import universal_module.text
import discord
import logging
# import sys

logger = logging.getLogger("Main")
# sys.excepthook = universal_module.utils.log_exception_handler


async def userinfo(bot: commands.Bot, context: commands.Context, arg=None):
    user_id = int(universal_module.utils.get_numbers_legacy(arg)[0])
    found_user = bot.get_user(user_id)
    if not found_user:
        found_user = await universal_module.utils.safe_fetch_user(bot, user_id)
    guild_member = context.guild.get_member(user_id)
    if not arg:
        await context.send(text.USERINFO_HELP)
    elif not found_user and not guild_member:
        await context.send(universal_module.text.INVALID_MEMBER_ID)
    elif guild_member:
        embed = get_member_info(guild_member)
        await context.send(embed=embed)
    elif found_user:
        embed = bare_bones_get_user_info(found_user)
        await context.send(embed=embed)
    else:
        await context.send(universal_module.text.SHOULD_NOT_ENCOUNTER_THIS)


def get_member_info(member: discord.Member) -> discord.Embed:
    embed = discord.Embed()
    embed.set_thumbnail(url=member.avatar_url)
    embed.add_field(name="Real Name", value=member.name)
    embed.add_field(name="Display Name", value=member.display_name)
    embed.add_field(name="Roles", value=get_mentions_of_list(member.roles))
    embed.add_field(name="Bot", value=member.bot)
    embed.add_field(name="Discord Official", value=member.system)
    embed.add_field(name="Creation Date", value=member.created_at.strftime(text.USERINFO_DATETIME_FORMAT))
    return embed


def bare_bones_get_user_info(user: discord.User) -> discord.Embed:
    embed = discord.Embed()
    embed.set_thumbnail(url=user.avatar_url)
    embed.add_field(name="Name", value=user.name)
    embed.add_field(name="Bot", value=user.bot)
    embed.add_field(name="Discord Official", value=user.system)
    embed.add_field(name="Creation Date", value=user.created_at.strftime(text.USERINFO_DATETIME_FORMAT))

    return embed


def get_mentions_of_list(mention_list: list) -> str:
    output = ""
    for mention in mention_list:
        output += "{} ".format(mention.mention)

    return output
