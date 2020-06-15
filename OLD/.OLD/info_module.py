from discord.ext import commands
from OLD.universal_module import utils
import logging
import discord
import typing
import sys
import re


logger = logging.getLogger("Main")
sys.excepthook = utils.log_exception_handler


class InfoCog(commands.Cog, name="Info Module"):
    def __init__(self, data_sync: utils.DataSync, bot_data: typing.Dict[str, dict]):
        super().__init__()
        self.data_sync = data_sync
        self.bot_data = bot_data

        self.enable_phrases: set = utils.ENABLE_PHRASES
        self.disable_phrases: set = utils.DISABLE_PHRASES

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Info Module Ready.")

    @commands.Cog.listener()
    async def on_message(self, message):
        server = message.guild.id
        if server not in self.bot_data:
            self.bot_data[server] = utils.default_server_data()

        if self.bot_data[message.guild.id]["info_braces_enabled"] and not message.author.bot and not message.content.startswith(";"):
            await self.info(message)

    @commands.command(name="info", usage="<enable, disable>", brief="Enable or disable")
    async def info_toggle(self, context, arg=None):
        server = context.guild.id
        if server not in self.bot_data:
            self.bot_data[server] = utils.default_server_data()

        self.bot_data[server]["info_braces_enabled"], message = utils.toggle_feature(arg, "info", self.enable_phrases, self.disable_phrases, self.bot_data[server]["info_braces_enabled"])
        await context.send(message)

    @commands.has_permissions(administrator=True)
    @commands.command(name="info_admin", usage="<create, delete, list> (\"arg2\") (\"arg3\")",
                      brief="Create, delete, or list keywords.")
    async def info_admin(self, context, arg1=None, arg2=None, arg3=None, *args):
        server = context.guild.id
        if server not in self.bot_data:
            self.bot_data[server] = utils.default_server_data()

        flag = False

        if not arg1:
            await context.send("You need to specify an argument.")
        elif args:
            await context.send("You sent too many arguments. Did you forget to wrap them in quotes (\"example\")?")

        elif arg1 == "create" and arg2 and arg3:
            if arg2 in self.bot_data[server]["info"]:
                flag = True
            self.bot_data[server]["info"][arg2] = arg3
            if flag:
                await context.send("Overwrote keyword \"{}\".".format(arg2))
            else:
                await context.send("Created keyword \"{}\"".format(arg2))

        elif arg1 == "delete" and arg2:
            flag = self.bot_data[server]["info"].pop(arg2, False)
            if flag:
                await context.send("Deleted keyword \"{}\"".format(arg2))
            else:
                await context.send("Couldn't find keyword \"{}\"".format(arg2))

        elif arg1 == "list":
            await context.send("List of keywords: {}".format(list(self.bot_data[server]["info"])))

        else:
            await context.send("Argument(s) invalid or missing.")

    async def info(self, message):
        server = message.guild.id

        embed = discord.Embed(title="Info Requested", color=0xffff00)
        found_keys = set()

        self.info_resursive(message.content, embed, found_keys, server)

        if embed.fields:
            await message.channel.send(embed=embed)

    def info_resursive(self, message_content: str, embed: discord.Embed, found_keys: set = None, server_id=None):
        comp = re.compile("{(.+?)}")
        keywords = comp.findall(message_content)
        for keyword in keywords:
            if keyword in self.bot_data[server_id]["info"] and keyword not in found_keys:
                found_keys.add(keyword)
                embed.add_field(name=keyword, value=self.bot_data[server_id]["info"][keyword], inline=True)
                logger.debug("Found keyword {}, already have found {}".format(keyword, found_keys))
                self.info_resursive(self.bot_data[server_id]["info"][keyword], embed, found_keys, server_id)

    @info_admin.error
    async def administrator_permission_error(self, context, error):
        if isinstance(error, commands.MissingPermissions):
            await context.send("You lack the administrator permission.")
