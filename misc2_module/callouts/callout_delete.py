from misc2_module.callouts.callout_data import CalloutGuildConfig
from misc2_module.callouts import text
from discord.ext import commands
from datetime import datetime, timedelta
import discord
import random


async def send_help_embed(context: commands.Context):
    embed = discord.Embed(title="Authorization Manager", color=0x79d26b)

    embed.add_field(name="Description", value=text.CALLOUT_DELETE_HELP_DESCRIPTION, inline=False)
    embed.add_field(name="Usage", value=text.CALLOUT_DELETE_HELP_USAGE, inline=False)

    await context.send(embed=embed)


async def callout_delete(callout_config: CalloutGuildConfig, message: discord.Message):
    try:
        if not message.author.bot and await check_audit_message_delete(message, message.author):
            await message.channel.send(random.sample(text.CALLOUT_DELETE_PHRASES, 1)[0].format(message.content,
                                                                                               message.author.mention))
    except discord.errors.Forbidden as ex:
        if ex.code == 50013:
            callout_config.deletes = False
            await message.channel.send(text.CALLOUT_DELETE_MISSING_AUDIT_PERMISSION)


async def toggle_on(callout_config: CalloutGuildConfig, context: commands.Context):
    if callout_config.deletes:
        await context.send(text.CALLOUT_DELETE_ALREADY_ENABLED)
    else:
        callout_config.deletes = True
        await context.send(text.CALLOUT_DELETE_ENABLED)


async def toggle_off(callout_config: CalloutGuildConfig, context: commands.Context):
    if callout_config.deletes:
        callout_config.deletes = False
        await context.send(text.CALLOUT_DELETE_DISABLED)
    else:
        await context.send(text.CALLOUT_DELETE_ALREADY_DISABLED)


async def check_audit_message_delete(message: discord.Message, user: discord.User):
    audit_logs = message.guild.audit_logs(limit=1, action=discord.AuditLogAction.message_delete,
                                          after=message.created_at - timedelta(minutes=1))
    async for audit in audit_logs:
        if audit.target.id == user.id:
            return False
    return True
