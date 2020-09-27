from alento_bot import StorageManager, guild_data_transformer, cache_transformer
from discord.ext import commands
from datetime import datetime
import discord.errors
import discord
import logging
import typing


logger = logging.getLogger("main_bot")


class PunishmentManager:
    def __init__(self, storage: StorageManager):
        self.storage: StorageManager = storage

        # noinspection PyArgumentList
        self.punish_cache = PunishmentCache(self.storage.config)

        self.storage.caches.register_cache("punishment_cache", self.punish_cache)
        self.storage.guilds.register_data_name("punishment_storage", PunishmentStorage)
        self.storage.guilds.register_data_name("punishment_config", PunishmentConfig)
        self.storage.guilds.register_data_name("word_ban_config", WordBanConfig)

    def create_warn(self, guild_id: int, user_id: int, start: datetime, end: datetime):
        warn_dict = {"user_id": user_id, "start": str(start), "end": str(end)}
        guild_data: PunishmentStorage = self.storage.guilds.get(guild_id, "punishment_storage")
        guild_data.warned_users[user_id] = warn_dict
        self.punish_cache.tracked_guilds.add(guild_id)

    def create_mute(self, guild_id: int, user_id: int, start: datetime, end: datetime):
        mute_dict = {"user_id": user_id, "start": str(start), "end": str(end)}
        guild_data: PunishmentStorage = self.storage.guilds.get(guild_id, "punishment_storage")
        guild_data.muted_users[user_id] = mute_dict
        self.punish_cache.tracked_guilds.add(guild_id)

    async def remove_expired(self, bot: commands.Bot):
        for guild_id in self.punish_cache.tracked_guilds:
            guild: discord.Guild = bot.get_guild(guild_id)
            if guild:
                punish_storage: PunishmentStorage = self.storage.guilds.get(guild_id, "punishment_storage")
                punish_config: PunishmentConfig = self.storage.guilds.get(guild_id, "punishment_config")
                warn_role = guild.get_role(punish_config.warn_role_id)
                if warn_role:
                    await if_time_remove_role(punish_storage.warned_users, guild, warn_role)
                mute_role = guild.get_role(punish_config.mute_role_id)
                if mute_role:
                    await if_time_remove_role(punish_storage.muted_users, guild, mute_role)


async def if_time_remove_role(member_storage: typing.Dict[int, dict], guild: discord.Guild, role: discord.Role):
    looping_keys = list(member_storage.keys())
    for user_id in looping_keys:
        member: discord.Member = guild.get_member(user_id)
        if member:
            # 2020-05-24 17:29:01.946074
            end_time = datetime.strptime(member_storage[user_id]["end"], "%Y-%m-%d %H:%M:%S.%f")
            try:
                if end_time <= datetime.utcnow():
                    await member.remove_roles(role, reason="Time expired.")
                    member_storage.pop(user_id, None)
                    logger.debug(f"Removed user {member.display_name} from punishment storage.")
            except discord.errors.Forbidden:
                logger.debug("Couldn't remove role from user, forbidden?")


@guild_data_transformer(name="punishment_storage")
class PunishmentStorage:
    def __init__(self):
        self.warned_users: typing.Dict[int, dict] = dict()
        self.muted_users: typing.Dict[int, dict] = dict()


@guild_data_transformer(name="punishment_config")
class PunishmentConfig:
    def __init__(self):
        self.warn_role_id: int = 0
        self.warner_roles: typing.Set[int] = set()
        self.mute_role_id: int = 0
        self.muter_roles: typing.Set[int] = set()


@cache_transformer(name="punishment_cache")
class PunishmentCache:
    def __init__(self):
        self.tracked_guilds: typing.Set[int] = set()


@guild_data_transformer(name="word_ban_config")
class WordBanConfig:
    def __init__(self):
        self.toggled_on: bool = False
        self.banned_words: set = set()
