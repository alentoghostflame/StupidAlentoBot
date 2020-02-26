from storage_module.server_data import DiskServerData
from storage_module.ram_storage import RAMStorage
from discord.ext import commands
import universal_module.utils
import discord
import logging
import sys

logger = logging.getLogger("Main")
sys.excepthook = universal_module.utils.log_exception_handler


async def bot_status(server_data: DiskServerData, ram_storage: RAMStorage, context: commands.Context):
    embed = discord.Embed(title="Bot Status", color=0xffff00)
    message_message = """Messages Read: {}
    Messages Sent: {}""".format(ram_storage.total_messages_read, ram_storage.total_messages_sent)
    embed.add_field(name="Messaging", value=message_message, inline=False)
    toggle_message = """Callout Delete: {}
    FAQ: {}
    Welcomes: {}""".format(server_data.callout_delete_enabled, server_data.faq_enabled, server_data.welcome_enabled)
    embed.add_field(name="Toggles", value=toggle_message, inline=False)
    await context.send(embed=embed)

