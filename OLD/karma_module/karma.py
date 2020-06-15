from OLD.karma_module.karma_info import list_karma, karma_top
from OLD.storage_module.disk_storage import DiskStorage
from OLD.karma_module.edit_karma import edit_karma
from discord.ext import commands
import logging
import discord


logger = logging.getLogger("Main")


class KarmaCog(commands.Cog, name="Karma Module"):
    def __init__(self, disk_storage: DiskStorage):
        super().__init__()
        self.disk_storage = disk_storage

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Karma cog ready.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild:
            await edit_karma(self.disk_storage.get_server(message.guild.id), message)

    @commands.command(name="karma", usage="(object or mention)", brief="Lists your own or someone/thing else's karma.")
    async def list_karma_command(self, context: commands.Context, arg1=None):
        server_data = self.disk_storage.get_server(context.guild.id)
        await list_karma(server_data, context, arg1)

    @commands.command(name="karmatop", brief="Lists the top 10 karma on the server.")
    async def karma_top_command(self, context: commands.Context):
        server_data = self.disk_storage.get_server(context.guild.id)
        await karma_top(server_data, context)


