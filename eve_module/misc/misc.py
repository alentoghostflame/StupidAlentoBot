from discord.ext import commands
import requests
import logging
import discord


logger = logging.getLogger("main_bot")


class EVEMiscCog(commands.Cog, name="EVEMisc"):
    def __init__(self):
        pass

    @commands.command(name="ping", brief="Quick command to test the bot.")
    async def ping(self, context):
        await context.send("Pong!")

    @commands.command(name="github", brief="Quick command to link the github URL.")
    async def github(self, context):
        await context.send("EVE Bot code: <https://github.com/alentoghostflame/StupidEveAppraisalBot>\n"
                           "EVE Library code: <https://github.com/alentoghostflame/EVE-Python-Library>")

    @commands.command(name="eve_status", brief="Get status about eve servers.")
    async def eve_status(self, context):
        base_url = "https://esi.evetech.net/latest/status"
        data: dict = requests.get(base_url).json()
        embed = discord.Embed(title="EVE Server Status.")
        embed.add_field(name="Player Count", value=data.get("players", "N/A"))
        embed.add_field(name="Server Version", value=data.get("server_version", "N/A"))
        embed.add_field(name="Start Time", value=data.get("start_time", "N/A"))
        await context.send(embed=embed)
