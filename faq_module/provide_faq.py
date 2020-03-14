import universal_module.utils
import logging
import discord
import typing
import sys
import re


logger = logging.getLogger("Main")
sys.excepthook = universal_module.utils.log_exception_handler


async def provide_info(faq_phrases: typing.Dict[str, str], message: discord.Message):
    embed = discord.Embed(title="Info Requested", color=0xffff00)
    found_keys = set()

    provide_info_recursive(faq_phrases, message.content, embed, found_keys)

    if embed.fields or embed.image:
        await message.channel.send(embed=embed)


def provide_info_recursive(faq_phrases: typing.Dict[str, str], message_content, embed: discord.Embed, found_keys: set):
    comp = re.compile("{(.+?)}")
    keywords = comp.findall(message_content)
    for keyword in keywords:
        if keyword in faq_phrases and keyword not in found_keys:
            if universal_module.utils.is_image_url(faq_phrases[keyword]):
                found_keys.add(keyword)
                embed.set_image(url=faq_phrases[keyword])
                logger.debug("Found image keyword {} with value {}".format(keyword, faq_phrases[keyword]))
            else:
                found_keys.add(keyword)
                embed.add_field(name=keyword, value=faq_phrases[keyword], inline=False)
                logger.debug("Found keyword {} with value {}".format(keyword, faq_phrases[keyword]))
                provide_info_recursive(faq_phrases, faq_phrases[keyword], embed, found_keys)
