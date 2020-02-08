from stupid_utils import DataSync, default_server_data
from discord.ext import commands
import discord
import typing


class InformationalCog(commands.Cog, name="Information Module"):
    def __init__(self, data_sync: DataSync, bot_data: typing.Dict[str, dict]):
        super().__init__()
        self.data_sync = data_sync
        self.bot_data = bot_data

    @commands.Cog.listener()
    async def on_ready(self):
        print("Information Module Ready.")

    @commands.Cog.listener()
    async def on_message(self, message):
        self.data_sync.messages_read += 1
        if message.author.id == self.data_sync.bot.user.id:
            self.data_sync.messages_sent += 1

    @commands.command(name="status", brief="Show status of bot.")
    async def get_bot_status(self, context):
        server = context.guild.id
        if server not in self.bot_data:
            self.bot_data[server] = default_server_data()

        embed = discord.Embed(title="Server Info", color=0xffff00)
        embed.add_field(name="Messages Read", value=str(self.data_sync.messages_read), inline=True)
        embed.add_field(name="Messages Sent", value=str(self.data_sync.messages_sent), inline=True)

        embed.add_field(name="Callout Delete", value=str(self.bot_data[server]["callout_delete_enabled"])
                        , inline=True)
        await context.send(embed=embed)

    @commands.command(name="server_info", brief="Show information about the server.")
    async def get_server_info(self, context):
        guild = context.message.guild
        embed = discord.Embed(title="Server Info", color=0xffff00)
        embed.set_thumbnail(url=guild.icon_url)
        embed.add_field(name="Name", value=guild.name, inline=True)
        embed.add_field(name="Emojis", value="{} Count: {}".format(emoji_tuple_to_string(guild.emojis),
                                                                   len(guild.emojis)), inline=True)
        embed.add_field(name="Region", value=str(guild.region), inline=True)
        embed.add_field(name="AFK Timeout", value=str(guild.afk_timeout), inline=True)
        embed.add_field(name="AFK Channel", value=str(guild.afk_channel), inline=True)
        embed.add_field(name="ID", value=str(guild.id), inline=True)
        embed.add_field(name="Max Presences", value=str(guild.max_presences), inline=True)
        embed.add_field(name="Max Members", value=str(guild.max_members), inline=True)
        embed.add_field(name="Description", value=str(guild.description), inline=True)
        embed.add_field(name="MFA Level", value=str(guild.mfa_level), inline=True)
        embed.add_field(name="Verification Level", value=str(guild.verification_level), inline=True)
        embed.add_field(name="Explicit Content Filter", value=str(guild.explicit_content_filter), inline=True)
        embed.add_field(name="Default Notifications", value=str(guild.default_notifications), inline=True)
        embed.add_field(name="Features", value=str(guild.features), inline=True)
        embed.add_field(name="Boost Tier", value=str(guild.premium_tier), inline=True)
        embed.add_field(name="User Boost Count", value=str(guild.premium_subscription_count), inline=True)
        embed.add_field(name="Preferred Locale", value=str(guild.preferred_locale), inline=True)
        # guild.channels
        embed.add_field(name="Is Large", value=str(guild.large), inline=True)
        # guild.voice_channels
        # guild.me
        # guild.voice_client
        # guild.text_channels
        # guild.categories
        embed.add_field(name="System Channel", value=str(guild.system_channel), inline=True)
        embed.add_field(name="Rules Channel", value=str(guild.rules_channel), inline=True)
        embed.add_field(name="Emoji Limit", value=str(guild.emoji_limit), inline=True)
        embed.add_field(name="Bitrate Limit", value=str(guild.bitrate_limit), inline=True)
        embed.add_field(name="File Size Limit", value=str(guild.filesize_limit), inline=True)
        # guild.members
        # guild.premium_subscribers
        # guild.roles
        embed.add_field(name="Owner", value=str(guild.owner), inline=True)
        embed.add_field(name="Is Icon Animated", value=str(guild.is_icon_animated()), inline=True)
        embed.add_field(name="Member Count", value=str(guild.member_count), inline=True)
        embed.add_field(name="Created At", value=str(guild.created_at), inline=True)
        await context.send(embed=embed)


def emoji_tuple_to_string(emoji_tuple: tuple) -> str:
    output = str()
    for emoji in emoji_tuple:
        output += str(emoji)
    return output
