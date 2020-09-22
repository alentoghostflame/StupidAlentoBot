from mmo_module.mmo_controller import MMOServer
from mmo_module.mmo_user import text
from discord.ext import commands
import discord


async def enable(mmo_server: MMOServer, context: commands.Context):
    if mmo_server.user.enable(context.author.id):
        await context.send(text.MMO_USER_ENABLE)
    else:
        await context.send(text.MMO_USER_ALREADY_ENABLED)


async def disable(mmo_server: MMOServer, context: commands.Context):
    if mmo_server.user.disable(context.author.id):
        await context.send(text.MMO_USER_DISABLE)
    else:
        await context.send(text.MMO_USER_ALREADY_DISABLED)


async def status(mmo_server: MMOServer, context: commands.Context):
    if mmo_server.user.enabled(context.author.id):
        char_data = mmo_server.user.get(context.author.id)
        char_data.tick()

        embed = discord.Embed(title="Character Status")
        embed.add_field(name="Values", value=f"```{char_data.health.get_display(regen=True)}\n"
                                             f"{char_data.mana.get_display(2, regen=True)}\n"
                                             f"{char_data.xp.get_display(4)}```")
        embed.add_field(name="Attack", value=f"Physical: {char_data.physical_damage} "
                                             f"Magical: {char_data.magical_damage}", inline=False)

        await context.send(embed=embed)
    else:
        await context.send(text.MMO_CURRENTLY_DISABLED)


async def battle(mmo_server: MMOServer, context: commands.Context):
    if mmo_server.user.enabled(context.author.id):
        pass
    else:
        await context.send(text.MMO_CURRENTLY_DISABLED)
