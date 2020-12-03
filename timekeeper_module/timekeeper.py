from alento_bot import StorageManager, BaseModule, TimerManager, error_handler, user_data_transformer, cache_transformer
from discord.ext import commands
from datetime import datetime, timedelta
from typing import Dict, Optional, Set, List
import logging
import discord
import re


RE_PROPER_TIME = re.compile("^[:\\d]+$")
TIMERKEEPER_UUID = "TimerKeeper_"
LARGE_TIME_FORMAT = "%a %b %m %Y, %I:%M:%S %p %Z"
COMPACT_TIME_FORMAT = "%d/%M/%Y %H:%M:S"


logger = logging.getLogger("main_bot")


@cache_transformer(name="timekeeper_cache")
class TimeKeeperCache:
    def __init__(self):
        self.tracked_users: Set[int] = set()


@user_data_transformer(name="timekeeper_data")
class TimerUserData:
    def __init__(self):
        self.timers: Dict[datetime, str] = dict()

    def get_timestrfmt_list(self, time_format: str = None) -> List[str]:
        if time_format:
            return [timer_time.strftime(time_format) for timer_time in self.timers]
        else:
            return list(str(timer_time) for timer_time in self.timers)


class TimekeeperModule(BaseModule):
    def __init__(self, *args):
        BaseModule.__init__(self, *args)
        self.cache: TimeKeeperCache = self.storage.caches.register_cache("timekeeper_cache", TimeKeeperCache)
        self.storage.users.register_data_name("timekeeper_data", TimerUserData)
        self.add_cog(TimekeeperCog(self.bot, self.storage, self.timer, self.cache))


class TimekeeperCog(commands.Cog, name="Timekeeper"):
    def __init__(self, bot: commands.Bot, storage: StorageManager, timer: TimerManager, cache: TimeKeeperCache):
        self.bot = bot
        self.storage = storage
        self.timer = timer
        self.cache: TimeKeeperCache = cache
        self.first_on_ready: bool = True

    @commands.Cog.listener()
    async def on_ready(self):
        if self.first_on_ready:
            self.first_on_ready = False
            for user_id in self.cache.tracked_users:
                user_data: TimerUserData = self.storage.users.get(user_id, "timekeeper_data")
                for timer_time in user_data.timers:
                    self.timer.add_timer(TIMERKEEPER_UUID + str(timer_time), timer_time,
                                         self.on_timer_finish(user_id, timer_time))

    @commands.command(name="time", brief="Gives current time in the bot time.")
    async def time(self, context: commands.Context):
        await context.send(f"Bot Time: {datetime.now().strftime(LARGE_TIME_FORMAT)}")

    @commands.command(name="timeutc", brief="Gives current time in UTC.")
    async def timeutc(self, context: commands.Context):
        await context.send(f"{datetime.utcnow().strftime(LARGE_TIME_FORMAT)}")

    @commands.group(name="timer", brief="Creates and shows information about timers.", invoke_without_command=True)
    async def timer(self, context: commands.Context, time: str = None, *message):
        if not time and not message:
            await context.send_help(context.command)
        elif timer_time := time_string_to_datetime(time):
            if message:
                message_text = " ".join(message)
            else:
                message_text = "No message given."

            self.cache.tracked_users.add(context.author.id)
            user_data: TimerUserData = self.storage.users.get(context.author.id, "timekeeper_data")
            user_data.timers[timer_time] = message_text
            self.timer.add_timer(TIMERKEEPER_UUID + str(timer_time), timer_time,
                                 self.on_timer_finish(context.author.id, timer_time))

            await context.send(f"Timer set for {timer_time.strftime(LARGE_TIME_FORMAT)} with message "
                               f"\"{message_text}\"")
        else:
            await context.send("Invalid time format, should be `days:hours:minutes` but with numbers.")

    @timer.command("info", brief="Shows information about your timekeeper setup.")
    async def timer_info(self, context: commands.Context):
        embed = discord.Embed(title="Timekeeper Info", color=0x23395D,
                              description="Keep in mind that all times listed are in UTC.")
        user_data: TimerUserData = self.storage.users.get(context.author.id, "timekeeper_data")

        if timer_times := user_data.get_timestrfmt_list(COMPACT_TIME_FORMAT):
            embed.add_field(name="Timers", value="\n".join(timer_times))
        else:
            embed.add_field(name="Timers", value="None")

        await context.send(embed=embed)

    @timer.error
    async def on_error(self, context: commands.Context, exception: Exception):
        await error_handler(context, exception)

    async def on_timer_finish(self, user_id: int, timer_time: datetime):
        user_data: TimerUserData = self.storage.users.get(user_id, "timekeeper_data")
        if (timer_message := user_data.timers.pop(timer_time, None)) is None:
            logger.warning(f"Desync, user {user_id} had a timer start for them, but it isn't in their data? "
                           f"What's going on?")
        else:
            if user := self.bot.get_user(user_id):
                if not (channel := user.dm_channel):
                    channel = await user.create_dm()
                await channel.send(f"Timer Expired: {timer_message}")

            else:
                logger.debug(f"Timer for user ID {user_id} finished, but couldn't get user.")
        if not user_data.timers:
            if user_id in self.cache.tracked_users:
                self.cache.tracked_users.remove(user_id)
            else:
                logger.warning(f"Desync, tried to remove user {user_id} from tracked cache, but they aren't in it?"
                               f"What's going on?")


def time_string_to_datetime(time_string: str) -> Optional[datetime]:
    if re.match(RE_PROPER_TIME, time_string) and (split_time := time_string.split(":")):
        minutes = 0
        hours = 0
        days = 0
        # noinspection PyUnboundLocalVariable
        if len(split_time) > 3:
            return None
        if len(split_time) >= 3 and split_time[-3].isdigit():
            days = int(split_time[-3])
        if len(split_time) >= 2 and split_time[-2].isdigit():
            hours = int(split_time[-2])
        if len(split_time) >= 1 and split_time[-1].isdigit():
            minutes = int(split_time[-1])

        return datetime.utcnow() + timedelta(days=days, hours=hours, minutes=minutes)
    else:
        return None
