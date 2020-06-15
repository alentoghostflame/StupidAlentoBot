from misc_module.welcomes.commands import welcome_control, welcome_on_join
from misc_module.storage import WelcomeConfig
from alento_bot import StorageManager
from discord.ext import commands
import misc_module.text
import logging
import discord


logger = logging.getLogger("main_bot")


class WelcomeCog(commands.Cog, name="Welcome"):
    def __init__(self, storage: StorageManager):
        self.storage: StorageManager = storage

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        welcome_config: WelcomeConfig = self.storage.guilds.get(member.guild.id, "welcome_config")
        if welcome_config.enabled:
            await welcome_on_join(welcome_config, member)

    @commands.has_permissions(administrator=True)
    @commands.command(name="welcome_control", aliases=["welcome", ])
    async def welcome_control(self, context: commands.Context, arg1=None, arg2=None, *args):
        welcome_config: WelcomeConfig = self.storage.guilds.get(context.guild.id, "welcome_config")
        await welcome_control(welcome_config, context, arg1, arg2, *args)

    @welcome_control.error
    async def admin_error(self, context: commands.Context, error: Exception):
        if isinstance(error, commands.MissingPermissions):
            await context.send(misc_module.text.MISSING_PERMISSIONS)
