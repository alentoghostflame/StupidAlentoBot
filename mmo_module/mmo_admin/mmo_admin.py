from mmo_module.mmo_controller import MMOServer
from mmo_module.mmo_data import GuildMMOConfig
from mmo_module.mmo_admin import text
from discord.ext import commands
import discord


async def enable(mmo_server: MMOServer, context: commands.Context):
    if mmo_server.guild.add(context.guild.id):
        await context.send(text.MMO_ADMIN_ENABLE)
    else:
        await context.send(text.MMO_ADMIN_ALREADY_ENABLED)
    # if mmo_config.enabled:
    #     await context.send(text.MMO_ADMIN_ALREADY_ENABLED)
    # else:
    #     mmo_config.enabled = True
    #     await context.send(text.MMO_ADMIN_ENABLE)


async def disable(mmo_server: MMOServer, context: commands.Context):
    if mmo_server.guild.remove(context.guild.id):
        await context.send(text.MMO_ADMIN_DISABLE)
    else:
        await context.send(text.MMO_ADMIN_ALREADY_DISABLED)
    # if mmo_config.enabled:
    #     mmo_config.enabled = False
    #     await context.send(text.MMO_ADMIN_DISABLE)
    # else:
    #     await context.send(text.MMO_ADMIN_ALREADY_DISABLED)

