from storage_module.server_data import DiskServerData
from discord.ext import commands
import misc_module.text as text
import universal_module.utils
import universal_module.text
import logging
import discord
import random
import sys


REMIND_DELETE_PHRASES: set = {"Hey, I thought I remembered {1} saying \"{0}\"",
                              "Hey {1}, didn't you say something like \"{0}\"?", "\"{0}\" - {1}."}


logger = logging.getLogger("Main")
sys.excepthook = universal_module.utils.log_exception_handler


async def callout_delete(server_data: DiskServerData, message: discord.Message):
    try:
        if not message.author.bot and await check_audit_message_delete(message, message.author):
            await message.channel.send(random.sample(REMIND_DELETE_PHRASES, 1)[0].format(message.content,
                                                                                         message.author.mention))
    except discord.errors.Forbidden as ex:
        if ex.code == 50013:
            server_data.callout_delete_enabled = False
            await message.channel.send(text.CALLOUT_DELETE_MISSING_AUDIT_PERMISSION)


async def callout_delete_admin(server_data: DiskServerData, context: commands.Context, arg1=None, arg2=None, *args):
    if not arg1:
        await context.send(text.CALLOUT_DELETE_ADMIN_HELP)
    elif arg1 == "toggle":
        await toggle(server_data, context, arg2)
    else:
        await context.send(universal_module.text.FIRST_ARGUMENT_INVALID)


async def toggle(server_data: DiskServerData, context: commands.Context, arg=None):
    server_data.callout_delete_enabled, message = \
        universal_module.utils.toggle_feature(arg, "callout_delete", universal_module.utils.ENABLE_PHRASES,
                                              universal_module.utils.DISABLE_PHRASES,
                                              server_data.callout_delete_enabled)
    await context.send(message)


async def check_audit_message_delete(message: discord.Message, user: discord.User):
    audit_logs = message.guild.audit_logs(limit=1, action=discord.AuditLogAction.message_delete)
    async for audit in audit_logs:
        if audit.target.id == user.id:
            return False
    return True
