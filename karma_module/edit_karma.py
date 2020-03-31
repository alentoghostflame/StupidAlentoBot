from storage_module.server_data import DiskServerData
# from discord.ext import commands
from karma_module import text
import universal_module.utils
import universal_module.text
import logging
import discord
import typing


logger = logging.getLogger("Main")


KARMA_BLACKLIST = ("c++", )


async def edit_karma(server_data: DiskServerData, message: discord.Message):
    split_message_content: typing.List[str] = message.content.split()
    member_id_set = set()
    text_object = ""
    for i in range(len(split_message_content)):
        content_section = split_message_content[i]
        karma_string_length = len(content_section) - len(content_section.rstrip("+-"))

        mention_ids = universal_module.utils.find_mentions(message.guild, content_section)
        if content_section.strip("+-"):
            text_object = content_section.strip("+-")

        if mention_ids:
            logger.debug("Updating mention set with ID(s) {}".format(mention_ids))
            member_id_set.update(mention_ids)
        if content_section.lower() not in KARMA_BLACKLIST and valid_solo_karma_string(content_section[-karma_string_length:]):
            logger.debug("Found valid solo karma string.")
            if member_id_set:
                logger.debug("Giving karma to server member(s).")
                for member_id in member_id_set:
                    await give_karma_type(server_data, message, member_id, content_section[-karma_string_length:])
                member_id_set.clear()
            elif text_object:
                logger.debug("Giving karma to object \"{}\".".format(text_object))
                await give_karma_type(server_data, message, text_object, content_section[-karma_string_length:],
                                      member=False)
                text_object = ""
        elif not mention_ids:
            member_id_set.clear()


async def give_karma_type(server_data: DiskServerData, message: discord.Message, give_karma_to, karma_string: str,
                          member=True):
    if karma_string.endswith("++"):
        await give_karma(server_data, message, give_karma_to, len(karma_string) - 1, member=member)
    elif karma_string.endswith("--"):
        await give_karma(server_data, message, give_karma_to, 1 - len(karma_string), member=member)


async def give_karma(server_data: DiskServerData, message: discord.Message, give_karma_to, karma_amount: int,
                     member=True):
    user_karma = server_data.member_karma.get(give_karma_to, 0)
    server_data.member_karma[give_karma_to] = user_karma + karma_amount
    if member:
        member_display_name = message.guild.get_member(give_karma_to).display_name
    else:
        member_display_name = "\"{}\"".format(give_karma_to)
    if karma_amount > 0:
        await message.channel.send(text.ADDED_KARMA_TO_MEMBER.format(karma_amount, member_display_name,
                                                                     server_data.member_karma[give_karma_to]))
        logger.debug(text.ADDED_KARMA_TO_MEMBER.format(karma_amount, member_display_name,
                                                       server_data.member_karma[give_karma_to]))
    else:
        await message.channel.send(text.REMOVED_KARMA_FROM_MEMBER.format(-karma_amount, member_display_name,
                                                                         server_data.member_karma[give_karma_to]))
        logger.debug(text.REMOVED_KARMA_FROM_MEMBER.format(-karma_amount, member_display_name,
                                                           server_data.member_karma[give_karma_to]))


def possible_karma_message(input_string: str) -> bool:
    if input_string.endswith("++") or input_string.endswith("--"):
        return True
    else:
        return False


def valid_solo_karma_string(karma_string: str) -> bool:
    if possible_karma_message(karma_string) and \
            (karma_string == "+" * len(karma_string) or karma_string == "-" * len(karma_string)):
        return True
    else:
        return False
