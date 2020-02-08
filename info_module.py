from discord.ext import commands
import stupid_utils
import logging
import discord
import typing
import sys
import re


logger = logging.getLogger("Main")
sys.excepthook = stupid_utils.log_exception_handler


class InfoCog(commands.Cog, name="Info Module"):
    def __init__(self, data_sync: stupid_utils.DataSync, bot_data: typing.Dict[str, dict]):
        super().__init__()
        self.data_sync = data_sync
        self.bot_data = bot_data

        self.enable_phrases: set = stupid_utils.ENABLE_PHRASES
        self.disable_phrases: set = stupid_utils.DISABLE_PHRASES

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Info Module Ready.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot_data[message.guild.id]["info_braces_enabled"]:
            await self.info(message)

    @commands.command(name="info", usage="<enable, disable>", brief="Enable or disable")
    async def info_toggle(self, context, arg=None):
        server = context.guild.id
        if server not in self.bot_data:
            self.bot_data[server] = stupid_utils.default_server_data()

        self.bot_data[server]["info_braces_enabled"], message = stupid_utils.toggle_feature(arg, "info", self.enable_phrases, self.disable_phrases, self.bot_data[server]["info_braces_enabled"])
        await context.send(message)

    # @commands.has_permissions(administrator=True)
    # @commands.command(name="info_admin", usage="<create, delete, edit, list>", brief="Create, delete, or edit keywords.")
    # async def info_admin(self, context, arg1=None, arg2=None, *args):
    #     server = context.guild.id
    #     if server not in self.bot_data:
    #         self.bot_data[server] = stupid_utils.default_server_data()
    #
    #     if not arg1 or not arg2:
    #         await context.send("You need to specify at least 2 arguments.")
    #     elif arg1 == "create":
    #         flag = False
    #         if arg2 in self.bot_data[server]["info"]:
    #             flag = True
    #         self.bot_data[server]["info"][arg2] = " ".join(args)
    #         if flag:
    #             await context.send("Success, overwrote previous entry.")
    #         else:
    #             await context.send("Created \"{}\"".format(arg2))
    #     elif arg1 == "delete":
    #         flag = self.bot_data[server]["info"].pop(arg2, None)
    #         if flag:
    #             await context.send("Success, entry deleted.")
    #         else:
    #             await context.send("Entry not found?")
    #     elif arg1 == "edit":
    #         await context.send("Not really implemented, create overrides anyways.")
    #     elif arg1 == "list":
    #         await context.send("List of all valid keywords: {}".format(list(self.bot_data[server]["info"].keys())))
    #     else:
    #         await context.send("Invalid first argument.")
    @commands.has_permissions(administrator=True)
    @commands.command(name="info_admin", usage="<create, delete, list> (\"arg2\") (\"arg3\")",
                      brief="Create, delete, or list keywords.")
    async def info_admin(self, context, arg1=None, arg2=None, arg3=None, *args):
        server = context.guild.id
        if server not in self.bot_data:
            self.bot_data[server] = stupid_utils.default_server_data()

        flag = False

        if not arg1:
            await context.send("You need at least 1 argument")
        elif arg1 == "list":
            await context.send("List of keywords: {}".format(list(self.bot_data[server]["info"])))
        elif args:
            await context.send("There seems to be more than 3 arguments. Did you wrap them in quotes (\")?")
        elif not arg2:
            await context.send("You need at least 2 arguments for that.")
        elif arg1 == "delete":
            flag = self.bot_data[server]["info"].pop(arg2, False)
            if flag:
                await context.send("Deleted keyword \"{}\"".format(arg2))
            else:
                await context.send("Couldn't find keyword \"{}\"".format(arg2))
        elif not arg3:
            await context.send("You need at least 3 arguments for that.")
        elif arg1 == "create":
            if arg2 in self.bot_data[server]["info"]:
                flag = True
            self.bot_data[server]["info"][arg2] = arg3
            if flag:
                await context.send("Overwrote keyword \"{}\".".format(arg2))
            else:
                await context.send("Created keyword \"{}\"".format(arg2))

    async def info(self, message):
        server = message.guild.id
        if server not in self.bot_data:
            self.bot_data[server] = stupid_utils.default_server_data()

        comp = re.compile("{(.+?)}")
        keywords = comp.findall(message.content)
        if keywords:
            embed = discord.Embed(title="Info Requested", color=0xffff00)
            for keyword in keywords:
                if keyword in self.bot_data[server]["info"]:
                    embed.add_field(name=keyword, value=self.bot_data[server]["info"][keyword], inline=True)
            if embed.fields:
                await message.channel.send(embed=embed)

    @info_admin.error
    async def administrator_permission_error(self, context, error):
        if isinstance(error, commands.MissingPermissions):
            await context.send("You lack the administrator permission.")
