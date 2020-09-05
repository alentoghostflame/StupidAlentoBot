from discord.ext import commands, tasks
import logging
import discord

logger = logging.getLogger("main_bot")


class ActivityCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.presence = "blank"

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.refresh_activity.is_running():
            await self.refresh_activity.start()

    def cog_unload(self):
        self.refresh_activity.cancel()

    @tasks.loop(seconds=30)
    async def refresh_activity(self):
        # author: discord.User = self.bot.get_user(self.bot.owner_id)
        pancake_guild: discord.Guild = self.bot.get_guild(549109597076717568)
        # author: discord.Member = pancake_guild.get_member(self.bot.owner_id)
        author = pancake_guild.get_member(106524898700066816)

        found_activity = False
        if author.activities:
            for activity in author.activities:
                if isinstance(activity, discord.Spotify):
                    bot_activity = discord.Activity(type=discord.ActivityType.listening, name=activity.title)
                    await self.bot.change_presence(activity=bot_activity)
                    self.presence = "spotify"
                    found_activity = True
            if not found_activity and self.presence is not None:
                await self.bot.change_presence(activity=None)
                self.presence = None
        else:
            if self.presence is not None:
                await self.bot.change_presence(activity=None)
                self.presence = None
