from storage_module.server_data import FAQPhraseData
import universal_module.utils
import universal_module.text
import logging
import discord
import typing
import sys
import re


logger = logging.getLogger("Main")
sys.excepthook = universal_module.utils.log_exception_handler


async def provide_info(faq_phrases: typing.Dict[str, FAQPhraseData], message: discord.Message):
    embed = discord.Embed(title="Info Requested", color=0xffff00)
    found_keys = set()

    provide_info_recursive(faq_phrases, message.content, embed, found_keys)

    if embed.fields or embed.image:
        await message.channel.send(embed=embed)


def provide_info_recursive(faq_phrases: typing.Dict[str, FAQPhraseData], message_content: str, embed: discord.Embed, found_keys: set):
    for keyword in get_keywords(message_content):
        if keyword in faq_phrases and keyword not in found_keys:
            found_keys.add(keyword)
            if isinstance(faq_phrases[keyword], str):
                migrate_to_class(faq_phrases, keyword)
            phrase_data = faq_phrases[keyword]
            if just_keywords(phrase_data.statement):
                logger.debug("Found keyword {} that links keyword(s) {}".format(keyword, phrase_data.statement))
                provide_info_recursive(faq_phrases, phrase_data.statement, embed, found_keys)
            else:
                embed.add_field(name=keyword, value=phrase_data.statement + universal_module.text.ZERO_WIDTH_SPACE)
                logger.debug("Found keyword {} with value {}".format(keyword, phrase_data.statement))
                if phrase_data.image_url:
                    embed.set_image(url=phrase_data.image_url)
                    logger.debug("Found keyword {} with image url {}".format(keyword, phrase_data.image_url))
                provide_info_recursive(faq_phrases, phrase_data.statement, embed, found_keys)


def migrate_to_class(faq_phrases: typing.Dict[str, FAQPhraseData], keyword: str):
    phrase_data = FAQPhraseData(keyword, str(faq_phrases[keyword]))
    if universal_module.utils.is_image_url(phrase_data.statement):
        phrase_data.image_url = phrase_data.statement
    faq_phrases[keyword] = phrase_data


def get_keywords(input_string: str) -> list:
    comp = re.compile("{(.+?)}")
    return comp.findall(input_string)


def just_keywords(input_string: str) -> bool:
    comp = re.compile("({.+?})")
    keywords = comp.findall(input_string)
    if keywords and len("".join(keywords)) == len("".join(input_string.split())):
        return True
    else:
        return False
