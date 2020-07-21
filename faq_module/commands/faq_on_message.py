from faq_module.storage import FAQManager  # , FAQConfig, FAQData
# from faq_module.commands import text
# from discord.ext import commands
# import faq_module.text
# import logging
import discord
# import typing
import re


async def faq_on_message(faq_manager: FAQManager, message: discord.Message):
    embed = discord.Embed(title="Info Requested", color=0x00ffff)
    found_keys = set()

    faq_on_recursive(faq_manager, message.content, embed, found_keys, message.guild.id)

    if embed.fields or embed.image:
        await message.channel.send(embed=embed)


def faq_on_recursive(faq_manager: FAQManager, message_content: str, embed: discord.Embed, found_keys: set, guild_id: int):
    for keyword in get_keywords(message_content):
        if keyword.lower() in faq_manager.get_keywords(guild_id):
            found_keys.add(keyword)
            faq_data = faq_manager.get(guild_id, keyword)

            if not just_keywords(faq_data.phrase):
                # \u200b is a zero width space.
                embed.add_field(name=keyword, value=faq_data.phrase + "\u200b")
                if faq_data.image_url:
                    embed.set_image(url=faq_data.image_url)

            faq_on_recursive(faq_manager, faq_data.phrase, embed, found_keys, guild_id)


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
