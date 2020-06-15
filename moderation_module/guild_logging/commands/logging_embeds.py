from moderation_module.guild_logging.commands import text
from moderation_module.storage import GuildLoggingConfig
import moderation_module.text
import logging
import discord


logger = logging.getLogger("main_bot")


async def send_delete_embed(log_config: GuildLoggingConfig, message: discord.Message):
    # embed = discord.Embed(title=f"{message.author.name}", color=0xffff00)
    embed = discord.Embed(color=0xff0000)
    # embed.set_thumbnail(url=message.author.avatar_url)

    embed.set_author(name=f"{message.author.name}#{message.author.discriminator}", icon_url=message.author.avatar_url)
    embed.description = text.SEND_DELETE_EMBED_DESCRIPTION.format(message.author.display_name, message.channel.mention)
    embed.set_footer(text=text.SEND_EMBED_MESSAGE_ID_FOOTER.format(message.id))
    embed.timestamp = message.created_at
    if message.content:
        embed.add_field(name="Message", value=message.content)
    else:
        embed.add_field(name="Message", value="<Message content was blank?>")

    channel = message.guild.get_channel(log_config.log_channel_id)
    if channel:
        await channel.send(embed=embed)


async def send_edit_embed(log_config: GuildLoggingConfig, before: discord.Message, after: discord.Message):
    embed = discord.Embed(color=0xffff00)

    embed.set_author(name=f"{after.author.name}#{after.author.discriminator}", icon_url=after.author.avatar_url)

    embed.description = text.SEND_EDIT_EMBED_DESCRIPTION.format(after.author.display_name, after.jump_url,
                                                                after.channel.mention)
    embed.set_footer(text=text.SEND_EMBED_MESSAGE_ID_FOOTER.format(after.id))
    embed.timestamp = after.created_at

    embed.add_field(name="Before", value=before.content)
    embed.add_field(name="After", value=after.content)

    channel = after.guild.get_channel(log_config.log_channel_id)
    if channel:
        await channel.send(embed=embed)


async def send_joined_embed(log_config: GuildLoggingConfig, member: discord.Member):
    embed = discord.Embed(color=0xffff00)

    embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member.avatar_url)
    embed.description = text.SEND_JOINED_EMBED_DESCRIPTION.format(member.display_name)
    embed.set_footer(text=text.SEND_EMBED_MEMBER_ID_FOOTER.format(member.id))
    embed.timestamp = member.joined_at

    channel = member.guild.get_channel(log_config.log_channel_id)
    if channel:
        await channel.send(embed=embed)


async def send_remove_embed(log_config: GuildLoggingConfig, member: discord.Member):
    embed = discord.Embed(color=0xffff00)

    embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member.avatar_url)
    embed.description = text.SEND_REMOVE_EMBED_DESCRIPTION.format(member.display_name)
    embed.set_footer(text=text.SEND_EMBED_MEMBER_ID_FOOTER.format(member.id))

    channel = member.guild.get_channel(log_config.log_channel_id)
    if channel:
        await channel.send(embed=embed)
