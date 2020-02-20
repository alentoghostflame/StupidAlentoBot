from storage_module.stupid_storage import DiskStorage
from discord.ext import commands
import stupid_utils
import logging
import discord
import random
import sys

logger = logging.getLogger("Main")
sys.excepthook = stupid_utils.log_exception_handler


class MiscCog(commands.Cog, name="Misc Module"):
    def __init__(self, disk_storage: DiskStorage):
        super().__init__()
        self.disk_storage = disk_storage

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Misc module ready.")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        server_data = self.disk_storage.get_server(member.guild.id)
        logger.debug("Member {} joined a server, {}".format(member.display_name, server_data.welcome_enabled))
        if server_data.welcome_enabled:
            await self.send_welcome(member)

    @commands.has_permissions(administrator=True)
    @commands.command(name="welcome", usage="toggle, add, remove, list", brief="Interacts with the welcome system. Use "
                                                                               "each first argument without a second "
                                                                               "argument for a description, except "
                                                                               "list.")
    async def welcome(self, context, arg1=None, arg2=None, *args):
        if not arg1:
            await context.send("You need to specify at least one argument, such as `toggle`, `add`, `remove`, or "
                               "`list`.")
        elif args:
            await context.send("You specified too many arguments. Did you forget to wrap them in quotes (\"example\")?")
        elif arg1 == "toggle":
            await self.toggle_welcome(context, arg2)
        elif arg1 == "add":
            await self.add_welcome(context, arg2)
        elif arg1 == "remove":
            await self.remove_welcome(context, arg2)
        elif arg1 == "list":
            await self.list_welcome(context, arg2)
        else:
            await context.send("Invalid first argument.")

    @commands.has_permissions(administrator=True)
    @commands.command(name="set_welcome_channel", brief="Use in channel to welcome users in.")
    async def set_welcome_channel(self, context):
        server_data = self.disk_storage.get_server(context.guild.id)
        if context.guild.get_channel(context.channel.id):
            # This probably isn't needed, but im paranoid, especially if arguments are added later.
            server_data.welcome_channel_id = context.channel.id
            await context.send("Welcome channel set to the current channel.")
        else:
            await context.send("...this is an invalid channel? HOW?! ***WHAT DID YOU DO???***")

    @commands.has_permissions(administrator=True)
    @commands.command(name="unset_welcome_channel", brief="Unset the channnel to welcome users in.")
    async def unset_welcome_channel(self, context):
        server_data = self.disk_storage.get_server(context.guild.id)
        server_data.welcome_channel_id = 0
        await context.send("Welcome channel set to be non-existent. It's unselected.")

    async def send_welcome(self, member: discord.Member):
        server_data = self.disk_storage.get_server(member.guild.id)
        channel = member.guild.get_channel(server_data.welcome_channel_id)
        if channel and len(server_data.welcome_messages) > 0:
            await channel.send(random.sample(server_data.welcome_messages, 1)[0].format(member.display_name))

    async def toggle_welcome(self, context, arg=None):
        server_data = self.disk_storage.get_server(context.guild.id)
        if not context.guild.get_channel(server_data.welcome_channel_id):
            await context.send("The selected channel to send the welcome messages is non-existent. Fix by using "
                               "`;set_welcome_channel` in the channel for welcomes to be forwarded to. Not enabling "
                               "welcomes.")
        else:
            server_data.welcome_enabled, message = stupid_utils.toggle_feature(arg, "welcome",
                                                                               stupid_utils.ENABLE_PHRASES,
                                                                               stupid_utils.DISABLE_PHRASES,
                                                                               server_data.welcome_enabled)
            await context.send(message)

    async def add_welcome(self, context, arg=None):
        server_data = self.disk_storage.get_server(context.guild.id)
        if not arg:
            await context.send("Adds a welcome message. Wrap the message in quotes, and use \"{0}\" without quotes to "
                               "have the users name be placed there in the message.\n In short, uses Python "
                               "`.format(member.display_name)`")
        else:
            # server_data.welcome_messages.add(arg)
            server_data.welcome_messages.append(arg)
            await context.send("Added welcome message.")

    async def remove_welcome(self, context, arg=None):
        server_data = self.disk_storage.get_server(context.guild.id)

        if not arg:
            await context.send("Removes a welcome message of the given index.")
        else:
            try:
                index = int(arg)
                if -1 * len(server_data.welcome_messages) <= index < len(server_data.welcome_messages):
                    server_data.welcome_messages.pop(index)
                    await context.send("Welcome message removed.")
                else:
                    await context.send("Index out of bounds.")
            except ValueError:
                await context.send("Specify a valid number.")

    async def list_welcome(self, context, arg=None):
        server_data = self.disk_storage.get_server(context.guild.id)
        if arg:
            await context.send("...you don't have to give an argument for this command.")
        else:
            message = ""
            for i in range(0, len(server_data.welcome_messages)):
                message += "{}: {}\n".format(i, server_data.welcome_messages[i])
            await context.send("List of welcomes: \n{}".format(message))

    @welcome.error
    @set_welcome_channel.error
    @unset_welcome_channel.error
    async def administrator_permission_error(self, context, error):
        if isinstance(error, commands.MissingPermissions):
            await context.send("You lack the administrator permission.")
