from OLD.storage_module.server_data import DiskServerData
from OLD.storage_module.ram_storage import RAMStorage
from discord.ext import commands
import OLD.misc_module.text as text
import OLD.universal_module.utils
import discord
import logging
import sys

logger = logging.getLogger("Main")
sys.excepthook = OLD.universal_module.utils.log_exception_handler


async def bot_status(server_data: DiskServerData, ram_storage: RAMStorage, context: commands.Context):
    embed = discord.Embed(title="Bot Status", color=0xffff00)
    embed.add_field(name="Messaging", value=text.STATUS_MESSAGE_MESSAGE.format(ram_storage.total_messages_read,
                                                                               ram_storage.total_messages_sent),
                    inline=False)
    embed.add_field(name="Toggles", value=text.STATUS_TOGGLE_MESSAGE.format(server_data.callout_delete_enabled,
                                                                            server_data.faq_enabled,
                                                                            server_data.welcome_enabled), inline=False)
    await context.send(embed=embed)

