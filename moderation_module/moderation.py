# from moderation_module.punishment import PunishmentCog, WordBanCog
from moderation_module.guild_logging import GuildLoggingCog
# from moderation_module.storage import PunishmentManager
from alento_bot import BaseModule, StorageManager, TimerManager, error_handler, guild_data_transformer, \
    cache_transformer, universal_text
from typing import Set, List, Dict, Optional, Union, Tuple, Coroutine, Iterable
from datetime import datetime, timedelta
from discord.ext import commands
import discord
import logging
import re


logger = logging.getLogger("main_bot")


RE_PROPER_TIME = re.compile("^[:\\d]+$")


WARN_TIMER_MODE_RESET = "Reset"
WARN_TIMER_MODE_ADD = "Additive"
WARN_TIMER_MODE_STACK = "Stack"

WARN_MAX_MODE_KEEP = "Keep"
WARN_MAX_MODE_RESET = "Reset"


TIMER_WARN_UUID = "ModerationWarn_{}_{}"
TIMER_MUTE_UUID = "ModerationMute_{}_{}"


@cache_transformer(name="moderation_data")
class ModerationGlobalData:
    def __init__(self):
        self.tracked_guilds: Set[int] = set()


@guild_data_transformer(name="moderation_settings")
class ModerationGuildSettings:
    def __init__(self):
        self.warn_enabled: bool = False
        self.warn_role: int = 0
        self.warner_roles: List[int] = list()
        self.warn_duration: str = "1:00:00"
        self.warn_max: int = 3
        self.warn_timer_mode = WARN_TIMER_MODE_RESET
        self.warn_max_mode = WARN_MAX_MODE_KEEP
        self.mute_enabled: bool = False
        self.mute_role: int = 0
        self.muter_roles: List[int] = list()
        self.mute_duration: str = "30"


@guild_data_transformer(name="moderation_data")
class ModerationGuildData:
    def __init__(self):
        self.warns: Dict[int, List[dict]] = dict()
        self.mutes: Dict[int, datetime] = dict()

    async def add_warn(self, context: commands.Context, cache: ModerationGlobalData, timer: TimerManager,
                       config: ModerationGuildSettings, guild: discord.Guild, member: discord.Member,
                       warn_role: discord.Role):
        time_now = datetime.utcnow()
        if member.id not in self.warns:
            self.warns[member.id] = list()

        if len(self.warns[member.id]) < config.warn_max:
            warn_data = {"start": time_now, "end": time_now + time_string_to_timedelta(config.warn_duration)}
            await member.add_roles(warn_role, reason="Warn given by the proper authorities.")
            self.warns[member.id].append(warn_data)
            logger.debug(f"Running apply warn for user {member.id}")
            await self.apply_warn(cache, timer, config, guild, member, warn_role)
            await context.send("Warn given.")
        else:
            logger.debug(f"Max warns ({config.warn_max}) hit, applying mute to user {member.id}")
            await self.add_max_warn_mute(context, cache, timer, config, guild, member)

    async def apply_warn(self, cache: ModerationGlobalData, timer: TimerManager,
                         config: ModerationGuildSettings, guild: discord.Guild, member: discord.Member,
                         warn_role: discord.Role):
        timer.rm_timer(TIMER_WARN_UUID.format(guild.id, member.id))
        if self.warns[member.id]:
            if config.warn_timer_mode == WARN_TIMER_MODE_RESET:
                warn_end_time = self.get_warn_end_time_reset_mode(member.id)
            elif config.warn_timer_mode == WARN_TIMER_MODE_ADD:
                warn_end_time = self.get_warn_end_time_add_mode(member.id)
            elif config.warn_timer_mode == WARN_TIMER_MODE_STACK:
                warn_end_time = self.get_warn_end_time_stack_mode(member.id)
            else:
                logger.warning(
                    f"Warn timer mode is unhandled value, \"{config.warn_timer_mode}\", defaulting to stack!")
                warn_end_time = self.get_warn_end_time_stack_mode(member.id)
            cache.tracked_guilds.add(guild.id)
            timer.add_timer(TIMER_WARN_UUID.format(guild.id, member.id), warn_end_time,
                            self.after_warn(cache, timer, config, guild, member, warn_role))
        else:
            logger.warning("Ran on user without a list? What is going on?")

    async def after_warn(self, cache: ModerationGlobalData, timer: TimerManager, config: ModerationGuildSettings,
                         guild: discord.Guild, member: discord.Member, warn_role: discord.Role):
        if self.warns[member.id]:
            self.clean_warns(config.warn_timer_mode)
        if warn_role.id != config.warn_role:
            warn_role = guild.get_role(config.warn_role)

        if warn_role:
            if self.warns[member.id]:
                logger.debug("Starting timer for apply role.")
                await self.apply_warn(cache, timer, config, guild, member, warn_role)
            else:
                logger.debug("Removing warn role from user.")
                await member.remove_roles(warn_role, reason="Warn expired.")
        if not self.warns:
            logger.debug("Server has no warns, discarding from tracked_guilds.")
            cache.tracked_guilds.discard(guild.id)

    def get_warn_end_time_stack_mode(self, user_id: int) -> Optional[datetime]:
        first_warn = None
        for warn_data in self.warns.get(user_id, list()):
            if first_warn:
                if warn_data["end"] < first_warn["end"]:
                    first_warn = warn_data
            else:
                first_warn = warn_data
        return first_warn["end"]

    def get_warn_end_time_reset_mode(self, user_id: int) -> Optional[datetime]:
        if warn_list := self.warns.get(user_id):
            latest_warn = None
            for warn_data in warn_list:
                if latest_warn:
                    if latest_warn["end"] < warn_data["end"]:
                        latest_warn = warn_data
                else:
                    latest_warn = warn_data
            return latest_warn["end"]
        else:
            return None

    def get_warn_end_time_add_mode(self, user_id: int) -> Optional[datetime]:
        if warn_list := self.warns.get(user_id):
            delta_sum = None
            first_datetime = None
            for warn_data in warn_list:
                if delta_sum:
                    delta_sum += warn_data["end"] - warn_data["start"]
                else:
                    delta_sum = warn_data["end"] - warn_data["start"]
                if first_datetime:
                    if warn_data["start"] < first_datetime:
                        first_datetime = warn_data["start"]
                else:
                    first_datetime = warn_data["start"]
            return first_datetime["start"] + delta_sum
        else:
            return None

    async def add_max_warn_mute(self, context: commands.Context, cache: ModerationGlobalData, timer: TimerManager,
                                config: ModerationGuildSettings, guild: discord.Guild, member: discord.Member):
        if config.mute_enabled:
            if config.mute_role and (mute_role := guild.get_role(config.mute_role)):
                await self.add_mute(context, cache, timer, config, guild, member, mute_role, False)
                if config.warn_max_mode == WARN_MAX_MODE_KEEP:
                    pass
                    await context.send("Max warns hit, mute given.")
                elif config.warn_max_mode == WARN_MAX_MODE_RESET:
                    timer.rm_timer(TIMER_WARN_UUID.format(guild.id, member.id))
                    self.warns[member.id].clear()
                    await context.send("Max warns hit, removing warns and mute given.")
                else:
                    logger.warning(f"Warn max mode is unhandled value \"{config.warn_max_mode}\", defaulting to keep!")
                    await context.send(f"Warn max mode is unhandled value \"{config.warn_max_mode}\", defaulting to keep!")
                    await context.send("Max warns hit, mute given.")
                    pass
            else:
                logger.debug("Tried to mute, but mute_role missing or invalid.")
                await context.send("Max warns hit, tried to mute but the mute role is either invalid or not specified, "
                                   "please configure it.")
        else:
            logger.debug("Tried to mute, but mutes are disabled.")

    async def add_mute(self, context: commands.Context, cache: ModerationGlobalData, timer: TimerManager,
                       config: ModerationGuildSettings, guild: discord.Guild, member: discord.Member,
                       mute_role: discord.Role, say_message: bool = True):
        timer.rm_timer(TIMER_MUTE_UUID.format(guild.id, member.id))
        mute_time = datetime.utcnow() + time_string_to_timedelta(config.mute_duration)
        await member.add_roles(mute_role, reason="Mute given by the proper authorities.")
        self.mutes[member.id] = mute_time
        cache.tracked_guilds.add(guild.id)
        timer.add_timer(TIMER_MUTE_UUID.format(guild.id, member.id), mute_time,
                        self.crappy_after_mute(cache, guild.id, member.id,
                                               member.remove_roles(mute_role, reason="Mute timer expired.")))
        if say_message:
            await context.send("Mute given.")

    async def crappy_after_mute(self, cache: ModerationGlobalData, guild_id: int,
                                member_id: int, coroutine: Coroutine):
        # TODO: Figure out why this is crappy? Probably because it wraps member.remove_roles
        logger.debug("Cleaning up mute.")
        self.mutes.pop(member_id)
        if not self.mutes:
            cache.tracked_guilds.remove(guild_id)
        await coroutine

    def clean_warns(self, mode: str) -> Set[int]:
        logger.debug("Cleaning warns.")
        unwarned_users = set()
        time_now = datetime.utcnow()
        for user_id in self.warns:
            if mode == WARN_TIMER_MODE_STACK:
                for warn_data in self.warns[user_id].copy():
                    if warn_data["end"] < time_now:
                        logger.debug(f"Removing warn: {warn_data}")
                        self.warns[user_id].remove(warn_data)
                        unwarned_users.add(user_id)
            elif mode == WARN_TIMER_MODE_RESET:
                warn_end = self.get_warn_end_time_reset_mode(user_id)
                if warn_end < time_now:
                    logger.debug(f"Removing warns")
                    self.warns[user_id].clear()
                    unwarned_users.add(user_id)
            elif mode == WARN_TIMER_MODE_ADD:
                warn_end = self.get_warn_end_time_add_mode(user_id)
                if warn_end < time_now:
                    self.warns[user_id].clear()
                    logger.debug(f"Removing warns.")
                    unwarned_users.add(user_id)
            else:
                logger.debug("Timer mode is in an unhandled state, I ain't cleaning warn timers!")
        return unwarned_users

    def clean_mutes(self) -> Set[int]:
        logger.debug("Cleaning mutes.")
        unmuted_users = set()
        time_now = datetime.utcnow()
        for user_id in self.mutes.copy():
            if self.mutes[user_id] < time_now:
                logger.debug(f"Removing mute for user {user_id}")
                self.mutes.pop(user_id)
                unmuted_users.add(user_id)
        return unmuted_users

    def clean(self, warn_mode: str) -> Tuple[Set[int], Set[int]]:
        return self.clean_warns(warn_mode), self.clean_mutes()

    def add_all_warn_timers(self, timer: TimerManager, mode: str, coroutine: Coroutine):
        for user_id in self.warns:
            if mode == WARN_TIMER_MODE_STACK:
                warn_end = self.get_warn_end_time_stack_mode(user_id)
                timer.add_timer(TIMER_WARN_UUID.format(warn_end), warn_end, coroutine)
            elif mode == WARN_TIMER_MODE_RESET:
                warn_end = self.get_warn_end_time_reset_mode(user_id)
                timer.add_timer(TIMER_WARN_UUID.format(warn_end), warn_end, coroutine)
            elif mode == WARN_TIMER_MODE_ADD:
                warn_end = self.get_warn_end_time_add_mode(user_id)
                timer.add_timer(TIMER_WARN_UUID.format(warn_end), warn_end, coroutine)
            else:
                logger.error("Timer mode is in an unhandled state, I ain't adding warn timers!")

    def add_all_mute_timers(self, timer: TimerManager, coroutine: Coroutine):
        for user_id in self.mutes:
            timer.add_timer(TIMER_MUTE_UUID.format(user_id), self.mutes[user_id], coroutine)


class ModerationModule(BaseModule):
    def __init__(self, *args):
        BaseModule.__init__(self, *args)
        self.cache: ModerationGlobalData = self.storage.caches.register_cache("moderation_data", ModerationGlobalData)
        self.storage.guilds.register_data_name("moderation_settings", ModerationGuildSettings)
        self.storage.guilds.register_data_name("moderation_data", ModerationGuildData)
        self.add_cog(NewPunishmentCog(self.bot, self.storage, self.timer, self.cache))
        self.add_cog(GuildLoggingCog(self.storage))

# class ModeratorModule(BaseModule):
#     def __init__(self, *args):
#         BaseModule.__init__(self, *args)
#         self.punish_manager: PunishmentManager = PunishmentManager(self.storage)
#         self.add_cog(PunishmentCog(self.storage, self.punish_manager, self.bot))
#         self.add_cog(WordBanCog(self.storage, self.punish_manager, self.bot))
#         self.add_cog(GuildLoggingCog(self.storage))


class NewPunishmentCog(commands.Cog, name="Moderation"):
    def __init__(self, bot: commands.Bot, storage: StorageManager, timer: TimerManager, cache: ModerationGlobalData):
        self.bot = bot
        self.storage = storage
        self.timer = timer
        self.cache = cache
        self.first_on_ready = True

    @commands.Cog.listener()
    async def on_ready(self):
        if self.first_on_ready:
            logger.debug("Punishment Cog ready, reading timers from storage.")
            self.first_on_ready = False
            for guild_id in self.cache.tracked_guilds:
                guild: discord.Guild = self.bot.get_guild(guild_id)
                if guild:
                    config: ModerationGuildSettings = self.storage.guilds.get(guild_id, "moderation_settings")
                    data: ModerationGuildData = self.storage.guilds.get(guild_id, "moderation_data")
                    users_to_unwarn, users_to_unmute = data.clean(config.warn_timer_mode)
                    logger.debug(f"Unwarn: {users_to_unwarn}    Unmute: {users_to_unmute}")
                    if warn_role := guild.get_role(config.warn_role):
                        for user_id in users_to_unwarn:
                            if member := guild.get_member(user_id):
                                await member.remove_roles(warn_role, reason="Time expired.")
                    if mute_role := guild.get_role(config.mute_role):
                        for user_id in users_to_unmute:
                            if member := guild.get_member(user_id):
                                await member.remove_roles(mute_role, reason="Time expired.")

    @commands.command(name="warn", brief="Warns the given user.")
    async def warn(self, context: commands.Context, member: discord.Member):
        config: ModerationGuildSettings = self.storage.guilds.get(context.guild.id, "moderation_settings")
        if config.warn_enabled:
            if config.warn_role and (warn_role := context.guild.get_role(config.warn_role)):
                data: ModerationGuildData = self.storage.guilds.get(context.guild.id, "moderation_data")
                await data.add_warn(context, self.cache, self.timer, config, context.guild, member, warn_role)
                # await context.send("Warn given.")
            else:
                await context.send("Warn role is either invalid or not specified, please configure it.")
        else:
            await context.send("Warns are not enabled.")

    @commands.command(name="mute", brief="Mutes the given user.")
    async def mute(self, context: commands.Context, member: discord.Member):
        config: ModerationGuildSettings = self.storage.guilds.get(context.guild.id, "moderation_settings")
        if config.mute_enabled:
            if config.mute_role and (mute_role := context.guild.get_role(config.mute_role)):
                if context.author.guild_permissions.administrator or \
                        has_any_role(context.guild, config.muter_roles, context.author):
                    data: ModerationGuildData = self.storage.guilds.get(context.guild.id, "moderation_data")
                    await data.add_mute(context, self.cache, self.timer, config, context.guild, member, mute_role)
                    # await context.send("Mute given.")
                else:
                    await context.send("You do not have permission to do this.")
            else:
                await context.send("Mute role is either invalid or not specified, please configure it.")
        else:
            await context.send("Mutes are not enabled.")

    @commands.group(name="mod", brief="Shows and controls the moderation features.",
                    invoke_without_command=True)
    async def mod(self, context: commands.Context, *subcommand):
        if not subcommand:
            await context.send_help(context.command)
        else:
            await context.send(universal_text.INVALID_SUBCOMMAND)

    @mod.command(name="info", brief="Shows information about the moderation features.")
    async def mod_info(self, context: commands.Context):
        config: ModerationGuildSettings = self.storage.guilds.get(context.guild.id, "moderation_settings")
        embed = discord.Embed(title="Moderation Settings", color=0x777777)
        if config.warn_role:
            warn_role = temp.mention if (temp := context.guild.get_role(config.warn_role)) else f"`{config.warn_role}`"
        else:
            warn_role = "`None`"
        warner_roles = " ".join(temp) if (
            temp := int_list_to_mention_list(context.guild, config.warner_roles)) else "`None`"

        warn_text = f"Enabled:`{config.warn_enabled}`\nWarn Role: {warn_role}\nWarner Roles: {warner_roles}\n" \
                    f"Warn Duration: `{config.warn_duration}`\nWarn Max: `{config.warn_max}`\n" \
                    f"Warn Timer Mode: `{config.warn_timer_mode}`\nWarn Max Mode: `{config.warn_max_mode}`"
        embed.add_field(name="Warns", value=warn_text, inline=True)
        if config.mute_role:
            mute_role = temp.mention if (temp := context.guild.get_role(config.mute_role)) else f"`{config.warn_role}`"
        else:
            mute_role = "`None`"
        muter_roles = " ".join(temp) if (
            temp := int_list_to_mention_list(context.guild, config.muter_roles)) else "`None`"

        mute_text = f"Enabled: `{config.mute_enabled}`\nMute Role: {mute_role}\nMuter Roles: {muter_roles}\n" \
                    f"Mute Duration: `{config.mute_duration}`"
        embed.add_field(name="Mutes", value=mute_text, inline=True)
        await context.send(embed=embed)

    @mod.group(name="warn", brief="Shows and controls warns.", invoke_without_command=True)
    async def mod_warn(self, context: commands.Context, *subcommand):
        if not subcommand:
            await context.send_help(context.command)
        else:
            await context.send(universal_text.INVALID_SUBCOMMAND)

    @commands.has_permissions(administrator=True)
    @mod_warn.group(name="timer", brief="Changes how the timers for warns work.", invoke_without_command=True)
    async def mod_warn_timer(self, context: commands.Context, *subcommand):
        if subcommand:
            await context.send(universal_text.INVALID_SUBCOMMAND)
        else:
            await context.send_help(context.command)

    @commands.has_permissions(administrator=True)
    @mod_warn_timer.command(name="reset", brief="A new warn resets all warn timers back to the normal duration.")
    async def mod_warn_timer_reset(self, context: commands.Context):
        config: ModerationGuildSettings = self.storage.guilds.get(context.guild.id, "moderation_settings")
        config.warn_timer_mode = WARN_TIMER_MODE_RESET
        await context.send("Warn timer mode set to: `Reset`\nWhen a user is warned when they already have a warn, the "
                           "timer will reset to the original duration. Example, if warns last 30 minutes, and 20 "
                           "minutes is left on their first warn, warning them again will make the timer last 30 "
                           "minutes. When the timer runs out, all warns will expire.")

    @commands.has_permissions(administrator=True)
    @mod_warn_timer.command(name="add", brief="A new warn adds the duration to the existing timer.")
    async def mod_warn_timer_add(self, context: commands.Context):
        config: ModerationGuildSettings = self.storage.guilds.get(context.guild.id, "moderation_settings")
        config.warn_timer_mode = WARN_TIMER_MODE_ADD
        await context.send("Warn timer mode set to: `Additive`\nWhen a user is warned when they already have a warn, "
                           "the timer will increase by the warn duration. Example, if warns last 30 minutes, and 20 "
                           "minutes is left on their first warn, warning them again will make the timer last 50 "
                           "minutes. When the timer runs out, all warns will expire.")

    @commands.has_permissions(administrator=True)
    @mod_warn_timer.command(name="stack", brief="A new warn will stack alongside previous warns.")
    async def mod_warn_timer_stack(self, context: commands.Context):
        config: ModerationGuildSettings = self.storage.guilds.get(context.guild.id, "moderation_settings")
        config.warn_timer_mode = WARN_TIMER_MODE_STACK
        await context.send("Warn timer mode set to: `Stack`\nWhen a user is warned when they already have a warn, the "
                           "timer of the original warn is not modified and another timer is made. Example, if warns "
                           "last 30 minutes, and 20 minutes is left on their first warn, warning them again will make "
                           "a second timer that will last for 30 minutes. After 20 minutes, the first warn will "
                           "expire, and 10 minutes after that the second warn will also expire.")

    @commands.has_permissions(administrator=True)
    @mod_warn.group(name="maxmode", brief="Changes what happens when max warns is hit.", invoke_without_command=True)
    async def mod_warn_maxmode(self, context: commands.Context, *subcommand):
        if subcommand:
            await context.send(universal_text.INVALID_SUBCOMMAND)
        else:
            await context.send_help(context.command)

    @commands.has_permissions(administrator=True)
    @mod_warn_maxmode.command(name="keep", brief="Mutes and keeps the current warns.")
    async def mod_warn_maxmode_keep(self, context: commands.Context):
        config: ModerationGuildSettings = self.storage.guilds.get(context.guild.id, "moderation_settings")
        config.warn_max_mode = WARN_MAX_MODE_KEEP
        await context.send("Warn max mode set to: `Keep`\nWhen a user hits the maximum warns, they will be muted and "
                           "warns are kept.")

    @commands.has_permissions(administrator=True)
    @mod_warn_maxmode.command(name="reset", brief="Mutes and removes all warns.")
    async def mod_warn_maxmode_reset(self, context: commands.Context):
        config: ModerationGuildSettings = self.storage.guilds.get(context.guild.id, "moderation_settings")
        config.warn_max_mode = WARN_MAX_MODE_RESET
        await context.send("Warn max mode set to: `Reset`\nWhen a user hits the maximum warns, they will be muted and "
                           "warns removed.")

    @commands.has_permissions(administrator=True)
    @mod_warn.command(name="max", brief="Set the max warns before a mute, if enabled.", invoke_without_command=True)
    async def mod_warn_max(self, context: commands.Context, number: int):
        if number > 0:
            config: ModerationGuildSettings = self.storage.guilds.get(context.guild.id, "moderation_settings")
            config.warn_max = number
            await context.send(f"Maximum warns before mute, assuming mutes are enabled, changed to {config.warn_max}")
        elif number == 0:
            await context.send("You can't set the max warns to 0. Maybe just use the mute command?")
        else:
            await context.send("...What are you trying to do? How does a negative amount of warns even work? Goodboy "
                               "points aren't a feature in this.")

    @commands.has_permissions(administrator=True)
    @mod_warn.command(name="duration", brief="Set the duration of a warn. D:H:M format.", aliases=["dur"])
    async def mod_warn_duration(self, context: commands.Context, time: str):
        if (warn_delta := time_string_to_timedelta(time)) and \
                (warn_delta_string := timedelta_to_time_string(warn_delta)):
            config: ModerationGuildSettings = self.storage.guilds.get(context.guild.id, "moderation_settings")
            # noinspection PyUnboundLocalVariable
            config.warn_duration = warn_delta_string
            await context.send(f"Warn duration set to `{warn_delta_string}`\nBe warned (hah), this will not change the "
                               f"duration of previous warns.")
        else:
            await context.send("Invalid time format, should be `days:hours:minutes`, but with numbers.")

    @commands.has_permissions(administrator=True)
    @mod_warn.command(name="enable", brief="Enables warns.")
    async def mod_warn_enable(self, context: commands.Context):
        config: ModerationGuildSettings = self.storage.guilds.get(context.guild.id, "moderation_settings")
        if config.warn_enabled:
            await context.send(universal_text.FEATURE_ALREADY_ENABLED_FORMAT.format("Mod Warn"))
        else:
            config.warn_enabled = True
            await context.send(universal_text.FEATURE_ENABLED_FORMAT.format("Mod Warn"))

    @commands.has_permissions(administrator=True)
    @mod_warn.command(name="disable", brief="Disables warns.")
    async def mod_warn_disable(self, context: commands.Context):
        config: ModerationGuildSettings = self.storage.guilds.get(context.guild.id, "moderation_settings")
        if config.warn_enabled:
            config.warn_enabled = False
            await context.send(universal_text.FEATURE_DISABLED_FORMAT.format("Mod Warn"))
        else:
            await context.send(universal_text.FEATURE_ALREADY_DISABLED_FORMAT.format("Mod Warn"))

    @commands.has_permissions(administrator=True)
    @mod_warn.command(name="set", brief="Set the role to warn people with")
    async def mod_warn_set(self, context: commands.Context, role: discord.Role):
        config: ModerationGuildSettings = self.storage.guilds.get(context.guild.id, "moderation_settings")
        config.warn_role = role.id
        await context.send(f"Warn role now set to `{role.name}`")

    @commands.has_permissions(administrator=True)
    @mod_warn.command(name="add", brief="Add a role that can warn people.")
    async def mod_warn_add(self, context: commands.Context, role: discord.Role):
        config: ModerationGuildSettings = self.storage.guilds.get(context.guild.id, "moderation_settings")
        if role.id in config.warner_roles:
            await context.send(f"This role has already been added!")
        else:
            config.warner_roles.append(role.id)
            await context.send(f"Users with the `{role.name}` role can now warn people, and cannot be warned.")

    @commands.has_permissions(administrator=True)
    @mod_warn.command(name="rm", brief="Remove a role that can warn people")
    async def mod_warn_rm(self, context: commands.Context, role: Union[discord.Role, int]):
        config: ModerationGuildSettings = self.storage.guilds.get(context.guild.id, "moderation_settings")
        role_id = role.id if isinstance(role, discord.Role) else role
        if role_id in config.warner_roles:
            config.warner_roles.remove(role_id)
            await context.send("Users with that role can no longer warn people, and once again can be warned.")
        else:
            await context.send("That role/ID was not added, and cannot be removed.")

    @mod.group(name="mute", brief="Shows and controls mutes.", invoke_without_command=True)
    async def mod_mute(self, context: commands.Context, *subcommand):
        if not subcommand:
            await context.send_help(context.command)
        else:
            await context.send(universal_text.INVALID_SUBCOMMAND)

    @commands.has_permissions(administrator=True)
    @mod_mute.command(name="duration", brief="Set the duration of a mute. D:H:M format.", aliases=["dur"])
    async def mod_mute_duration(self, context: commands.Context, time: str):
        if (mute_delta := time_string_to_timedelta(time)) and \
                (mute_delta_string := timedelta_to_time_string(mute_delta)):
            config: ModerationGuildSettings = self.storage.guilds.get(context.guild.id, "moderation_settings")
            # noinspection PyUnboundLocalVariable
            config.mute_duration = mute_delta_string
            await context.send(f"Mute duration set to `{mute_delta_string}`")
        else:
            await context.send("Invalid time format, should be `days:hours:minutes`, but with numbers.")

    @commands.has_permissions(administrator=True)
    @mod_mute.command(name="enable", brief="Enables warns.")
    async def mod_mute_enable(self, context: commands.Context):
        config: ModerationGuildSettings = self.storage.guilds.get(context.guild.id, "moderation_settings")
        if config.mute_enabled:
            await context.send(universal_text.FEATURE_ALREADY_ENABLED_FORMAT.format("Mod Mute"))
        else:
            config.mute_enabled = True
            await context.send(universal_text.FEATURE_ENABLED_FORMAT.format("Mod Mute"))

    @commands.has_permissions(administrator=True)
    @mod_mute.command(name="disable", brief="Disables warns.")
    async def mod_mute_disable(self, context: commands.Context):
        config: ModerationGuildSettings = self.storage.guilds.get(context.guild.id, "moderation_settings")
        if config.mute_enabled:
            config.mute_enabled = False
            await context.send(universal_text.FEATURE_DISABLED_FORMAT.format("Mod Mute"))
        else:
            await context.send(universal_text.FEATURE_ALREADY_DISABLED_FORMAT.format("Mod Mute"))

    @commands.has_permissions(administrator=True)
    @mod_mute.command(name="set", brief="Set the role to mute people with")
    async def mod_mute_set(self, context: commands.Context, role: discord.Role):
        config: ModerationGuildSettings = self.storage.guilds.get(context.guild.id, "moderation_settings")
        config.mute_role = role.id
        await context.send(f"Mute role now set to `{role.name}`")

    @commands.has_permissions(administrator=True)
    @mod_mute.command(name="add", brief="Add a role that can mute people.")
    async def mod_mute_add(self, context: commands.Context, role: discord.Role):
        config: ModerationGuildSettings = self.storage.guilds.get(context.guild.id, "moderation_settings")
        if role.id in config.muter_roles:
            await context.send(f"This role has already been added!")
        else:
            config.muter_roles.append(role.id)
            await context.send(f"Users with the `{role.name}` role can now mute people, and cannot be muted.")

    @commands.has_permissions(administrator=True)
    @mod_mute.command(name="rm", brief="Remove a role that can mute people")
    async def mod_mute_rm(self, context: commands.Context, role: Union[discord.Role, int]):
        config: ModerationGuildSettings = self.storage.guilds.get(context.guild.id, "moderation_settings")
        role_id = role.id if isinstance(role, discord.Role) else role
        if role_id in config.muter_roles:
            config.muter_roles.remove(role_id)
            await context.send("Users with that role can no longer mute people, and once again can be muted.")
        else:
            await context.send("That role/ID was not added, and cannot be removed.")

    @commands.has_permissions(administrator=True)
    @mod.group(name="clear", brief="Clears warns or mutes of the given person/group.",
               invoke_without_command=True)
    async def mod_clear(self, context: commands.Context, *subcommand):
        if not subcommand:
            await context.send_help(context.command)
        else:
            await context.send(universal_text.INVALID_SUBCOMMAND)

    @warn.error
    @mod.error
    @mod_info.error
    @mod_clear.error
    @mod_warn.error
    @mod_warn_enable.error
    @mod_warn_disable.error
    @mod_warn_set.error
    @mod_warn_duration.error
    @mod_warn_add.error
    @mod_warn_rm.error
    @mod_warn_timer.error
    @mod_warn_timer_stack.error
    @mod_warn_timer_add.error
    @mod_warn_timer_reset.error
    @mod_warn_maxmode.error
    @mod_warn_maxmode_keep.error
    @mod_warn_maxmode_reset.error
    @mod_warn_max.error
    @mod_mute.error
    @mod_mute_enable.error
    @mod_mute_disable.error
    @mod_mute_set.error
    @mod_mute_add.error
    @mod_mute_rm.error
    async def mod_error_handler(self, context: commands.Context, exception: Exception):
        await error_handler(context, exception)


def int_list_to_mention_list(guild: discord.Guild, roles: List[int]):
    ret = []
    for role in roles:
        ret.append(guild_role.mention if (guild_role := guild.get_role(role)) else role)
    return ret


def time_string_to_timedelta(time_string: str) -> Optional[timedelta]:
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
        return timedelta(days=days, hours=hours, minutes=minutes)


def time_string_to_datetime(time_string: str) -> Optional[datetime]:
    if delta := time_string_to_timedelta(time_string):
        return datetime.utcnow() + delta
    else:
        return None


def timedelta_to_time_string(delta: timedelta):
    ret = ""
    if delta.days:
        ret += f"{delta.days}:"
    if hours := delta.seconds // 3600:
        ret += f"{hours}:"
    elif delta.days:
        ret += ":"
    if minutes := delta.seconds % 3600 // 60:
        ret += f"{minutes}"
    return ret


def has_any_role(guild: discord.Guild, given_roles: Iterable, member: discord.Member) -> bool:
    for role in given_roles:
        for user_role in member.roles:
            if guild.get_role(role) == user_role:
                return True
    return False
