from alento_bot import StorageManager, BaseModule, user_data_transformer, universal_text, cache_transformer
from discord.ext.commands.errors import MissingRequiredArgument, BadArgument
from discord.ext import commands, tasks
from typing import Dict, Optional, Union, Set
from datetime import datetime, timedelta
import discord
import logging
import random
import re

# TradeStreak Name
TS_NAME = "Mudae Tradestreaks"
# Wait For Ranked CHARacter LIST
WF_R_CHAR_LIST = "WFRCHARLIST"
# Wait For KEY'd CHARacter LIST
WF_KEY_LIST = "WFKEYLIST"

# Wait For MUDAE TRADE
WF_MUDAE_TRADE_START = "WFMUDAETRADESTART"
WF_MUDAE_TRADE_MID = "WFMUDAETRADEMID"

MARRY_REGEX = re.compile("\\A💖\\s\\*\\*([^*]+)\\*\\*\\sand\\s\\*\\*([^*]+)[^💖]+💖")
TRADE_START_REGEX = re.compile("^\\$me\\s+<\\W+(\\d+)>[\\s\\w]*")
MENTION_REGEX = re.compile("<[\\D]+(\\d+)>")
TRADE_MIDDLE_REGEX = re.compile("<[\\D](\\d+)>,(.+)")
TRADE_END_REGEX = re.compile("🤝 The exchange is over: (.+)")


logger = logging.getLogger("main_bot")


@user_data_transformer(name="mudae_data")
class MudaeUserData:
    def __init__(self):
        self.ts_enabled: Dict[int, bool] = dict()
        self.ts_amount: Dict[int, int] = dict()
        self.ts_quests: Dict[int, Dict[str, bool]] = dict()
        self.ts_streak: int = 0
        self.ts_highest_streak: int = 0
        # self.claimed_characters: List[str] = list()
        # self.keyed_characters: List[str] = list()
        self.claimed_chars: Dict[int, Set[str]] = dict()
        self.keyed_chars: Dict[int, Set[str]] = dict()


@cache_transformer(name="mudae_data")
class MudaeCacheData:
    def __init__(self):
        self.has_features_enabled: Set[int] = set()
        # self.tradestreak_time: Optional[datetime] = None


class MudaeTrade:
    def __init__(self, first: int, second: int, first_mar: Optional[str], second_mar: Optional[str]):
        self.first: int = first
        self.second: int = second
        self.first_mar: Optional[str] = first_mar
        self.second_mar: Optional[str] = second_mar


class MudaeModModule(BaseModule):
    def __init__(self, bot, storage):
        BaseModule.__init__(self, bot, storage)
        self.storage.users.register_data_name("mudae_data", MudaeUserData)
        # noinspection PyArgumentList
        self.storage.caches.register_cache("mudae_data", MudaeCacheData(storage.config))
        self.add_cog(MudaeModCog(bot, storage))


class MudaeModCog(commands.Cog, name="MudaeMod"):
    def __init__(self, bot: commands.Bot, storage: StorageManager):
        self.bot: commands.Bot = bot
        self.storage: StorageManager = storage
        self.waiting_for_next_message: Dict[int, str] = dict()
        self.waiting_for_bot_message: Dict[Union[int, tuple], MudaeTrade] = dict()
        self.cache: MudaeCacheData = self.storage.caches.get_cache("mudae_data")
        self.ts_cycle: Optional[datetime] = None

    @commands.Cog.listener()
    async def on_ready(self):
        self.tradestreak_loop.start()

    def cog_unload(self):
        self.tradestreak_loop.stop()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild:
            if message.author.bot:
                await self.detect_marry(message)
                await self.detect_me_middle(message)
                await self.detect_me_end(message)

            else:
                if (trade_start := re.match(TRADE_START_REGEX, message.content)) and \
                        trade_start.groups()[0].isdigit():
                    self.waiting_for_bot_message[message.author.id] = \
                        MudaeTrade(message.author.id, int(trade_start.groups()[0]), None, None)
                    await message.channel.send("Trade detected, starting to track.")

                elif not message.content.startswith("$") and (keyword := self.waiting_for_next_message.get(
                        message.author.id, None)):
                    self.waiting_for_next_message.pop(message.author.id)
                    user_data: MudaeUserData = self.storage.users.get(message.author.id, "mudae_data")
                    # PyCharm doesn't fully understand the walrus operator
                    # noinspection PyUnboundLocalVariable
                    if keyword == WF_R_CHAR_LIST:
                        if await process_message_and_run(message, self.process_ranked_characters):
                            await message.channel.send(f"{len(user_data.claimed_chars[message.guild.id])} claimed characters "
                                                       f"processed.")
                    elif keyword == WF_KEY_LIST:
                        if await process_message_and_run(message, self.process_keyed_characters):
                            await message.channel.send(f"{len(user_data.keyed_chars[message.guild.id])} keyed characters processed.")
                    else:
                        await message.channel.send("Error occurred, send this to Alento Ghostflame:\n"
                                                   f"`MUDAEMOD ON_MESSAGE NOTBOT BAD_WF {keyword}`")

    @commands.group(name="mudaemod", brief="Controls mods for Mudae for you or this server.", aliases=["mudae", "mm"],
                    invoke_without_command=True)
    async def mudaemod(self, context: commands.Context, *subcommand):
        if subcommand:
            await context.send(universal_text.INVALID_COMMAND)
        else:
            await context.send_help(context.command)

    @mudaemod.command(name="info", brief="Gives Mudae Mod information to you.")
    async def mudaemod_info(self, context: commands.Context):
        user_data: MudaeUserData = self.storage.users.get(context.author.id, "mudae_data")
        embed = discord.Embed(title="MudaeMod Info", color=0xff0000)

        toggles = f"Tradestreaks: `{user_data.ts_enabled.get(context.guild.id, False)}`\n"
        embed.add_field(name="Toggles", value=toggles, inline=True)

        stat_text = f"Trade Streak: `{user_data.ts_streak}`\n"
        stat_text += f"Trades Per Day: `{user_data.ts_amount.get(context.guild.id, 0)}`\n"
        stat_text += f"Highest TS: `{user_data.ts_highest_streak}`\n"
        embed.add_field(name="Stats", value=stat_text, inline=True)

        sync_text = f"Claimed: `{len(user_data.claimed_chars[context.guild.id])}`\n" if \
            user_data.claimed_chars.get(context.guild.id, False) else \
            f"Claimed: `None`, sync with `{context.prefix}mudaemod sync chars`\n"
        sync_text += f"Keyed: `{len(user_data.keyed_chars[context.guild.id])}`\n" if \
            user_data.keyed_chars.get(context.guild.id, False) else \
            f"Keyed: `None`, sync with `{context.prefix}mudaemod sync keys`\n"
        embed.add_field(name="Sync", value=sync_text, inline=False)

        await context.send(embed=embed)

    @mudaemod.group(name="sync", brief="Syncs information between Mudae and this bot.", invoke_without_command=True)
    async def mudaemod_sync(self, context: commands.Context, *subcommand):
        if subcommand:
            await context.send(universal_text.INVALID_COMMAND)
        else:
            await context.send_help(context.command)

    @mudaemod_sync.command(name="chars", brief="Syncs characters between Mudae and this bot.")
    async def mudaemod_sync_chars(self, context: commands.Context):
        await self.ask_for_ranked_characters(context)

    @mudaemod_sync.command(name="keys", brief="Syncs key'd characters between Mudae and this bot.")
    async def mudaemod_sync_keys(self, context: commands.Context):
        await self.ask_for_keyed_characters(context)

    @commands.guild_only()
    @mudaemod_sync.command(name="clear", description="Clears all synced Mudae data from this bot and will disable/"
                                                     "reset the mods that rely on it.",
                           brief="Clears all Mudae sync data, disables certain mods.")
    async def mudaemod_sync_clear(self, context: commands.Context):
        user_data: MudaeUserData = self.storage.users.get(context.author.id, "mudae_data")
        user_data.ts_enabled[context.guild.id] = False
        user_data.claimed_chars[context.guild.id] = set()
        user_data.keyed_chars[context.guild.id] = set()
        user_data.ts_streak = 0
        await context.send("Cleared mudae sync data and disabled/reset related mods.")

    @mudaemod.group(name="tradestreak", brief="Controls the tradestreak Mudae mod.", aliases=["ts"],
                    invoke_without_command=True)
    async def mudaemod_ts(self, context: commands.Context, *subcommand):
        if subcommand:
            await context.send(universal_text.INVALID_COMMAND)
        else:
            await context.send_help(context.command)

    @mudaemod_ts.command(name="enable", brief="Enables tradestreaks for your account on this server.")
    async def mudaemod_ts_enable(self, context: commands.Context):
        user_data: MudaeUserData = self.storage.users.get(context.author.id, "mudae_data")
        if user_data.ts_enabled.get(context.guild.id, False):
            await context.send(universal_text.FEATURE_ALREADY_ENABLED_FORMAT.format(TS_NAME))
        elif not user_data.claimed_chars.get(context.guild.id, set()):
            await context.send("You don't have any claimed characters synced, check `mudaemod info` for more information")
        else:
            user_data.ts_enabled[context.guild.id] = True
            self.cache.has_features_enabled.add(context.author.id)
            await context.send(universal_text.FEATURE_ENABLED_FORMAT.format(TS_NAME))

    @mudaemod_ts.command(name="disable", brief="Disables and resets tradestreaks for your account on this server.")
    async def mudaemod_ts_disable(self, context: commands.Context):
        user_data: MudaeUserData = self.storage.users.get(context.author.id, "mudae_data")
        if user_data.ts_enabled.get(context.guild.id, False):
            user_data.ts_enabled[context.guild.id] = False
            user_data.ts_streak = 0
            await context.send(universal_text.FEATURE_DISABLED_FORMAT.format(TS_NAME))
        else:
            await context.send(universal_text.FEATURE_ALREADY_DISABLED_FORMAT.format(TS_NAME))

    @mudaemod_ts.command(name="set", brief="Sets the amount of tradestreaks for your account on this server.")
    async def mudaemod_ts_set(self, context: commands.Context, amount_per_day: int):
        user_data: MudaeUserData = self.storage.users.get(context.author.id, "mudae_data")
        if amount_per_day < 1:
            await context.send("If you're going to set it that low, just disable this feature =(")
        elif user_data.ts_amount == amount_per_day:
            await context.send(f"You already have {amount_per_day} per day!")
        elif len(user_data.claimed_chars[context.guild.id]) - len(user_data.keyed_chars[context.guild.id]) < \
                amount_per_day:
            await context.send(f"You can't have more quests than you currently have tradable characters!")
        else:
            user_data.ts_amount[context.guild.id] = amount_per_day
            await context.send(f"Set to {user_data.ts_amount[context.guild.id]} per day, starting next cycle.")

    @commands.guild_only()
    @mudaemod_ts.command(name="trades", brief="Lists the Tradestreak trades for this server.")
    async def mudaemod_ts_quests(self, context: commands.Context):
        user_data: MudaeUserData = self.storage.users.get(context.author.id, "mudae_data")
        embed = discord.Embed(title="Tradestreak Quests", color=0xff0000)

        if context.guild.id in user_data.ts_quests:
            current_quests = ""
            for char_name in user_data.ts_quests[context.guild.id]:
                current_quests += f"`{char_name}`: ✅\n" if user_data.ts_quests[context.guild.id][char_name] else f"`{char_name}`: ❌\n"
        else:
            current_quests = "You have no trades for this server."
        embed.add_field(name="Server Trades", value=current_quests, inline=False)
        total_quests = 0
        for guild_id in user_data.ts_quests:
            for char_name in user_data.ts_quests[guild_id]:
                if user_data.ts_quests[guild_id][char_name] is False:
                    total_quests += 1
        embed.add_field(name="Cross-server", value=f"Total trades remaining: {total_quests}", inline=False)

        await context.send(embed=embed)

    async def ask_for_ranked_characters(self, context: commands.Context):
        await context.send("To synchronize your married Mudae characters with this bot, do `$mmrs` and once Mudae is "
                           "done messaging you, copy and paste all of the text here. If it wants to turn it into "
                           "`message.txt`, that's fine. If Mudae says \"No result!\", say \"None\" on your next "
                           "message.")
        self.waiting_for_next_message[context.author.id] = WF_R_CHAR_LIST

    async def ask_for_keyed_characters(self, context: commands.Context):
        await context.send("To synchronized your keyed Mudae characters with this bot, do `$mmys` and once Mudae is "
                           "done messaging you, copy and paste all of the text here. If it wants to turn it into "
                           "`message.txt`, that's fine. If Mudae says \"No result!\", say \"None\" on your next "
                           "message.")
        self.waiting_for_next_message[context.author.id] = WF_KEY_LIST

    async def process_ranked_characters(self, message: discord.Message, text: str) -> bool:
        split_text = text.split("\n")
        logger.debug(f"Processing ranked characters for {message.author.name}:{message.author.id}")
        if text.lower() == "none":
            user_data: MudaeUserData = self.storage.users.get(message.author.id, "mudae_data")
            user_data.claimed_chars[message.guild.id] = set()
            return True
        elif not split_text:
            await message.channel.send("Invalid text given.")
            return False
        elif not split_text[0].strip().endswith(f"{message.author.name}'s harem"):
            await message.channel.send("Invalid header, did you properly copy or did Mudae change?")
            logger.debug(f"Invalid header for {message.author.name}:{message.author.id},\n{split_text[0].strip()}")
            return False
        else:
            character_set: Set[str] = set()
            for line in split_text[1:]:
                if (char_split := line.split("-")) and len(char_split) == 2:
                    character_set.add(char_split[1].strip())
            user_data: MudaeUserData = self.storage.users.get(message.author.id, "mudae_data")
            user_data.claimed_chars[message.guild.id] = character_set
            return True

    async def process_keyed_characters(self, message: discord.Message, text: str) -> bool:
        split_text = text.split("\n")
        logger.debug(f"Processing ranked characters for {message.author.name}:{message.author.id}")
        if text.lower() == "none":
            user_data: MudaeUserData = self.storage.users.get(message.author.id, "mudae_data")
            user_data.keyed_chars[message.guild.id] = set()
            return True
        elif not split_text:
            await message.channel.send("Invalid text given.")
            return False
        elif not split_text[0].strip().endswith(f"{message.author.name}'s harem"):
            await message.channel.send("Invalid header, did you properly copy or did Mudae change?")
            logger.debug(f"Invalid header for {message.author.name}:{message.author.id},\n{split_text[0].strip()}")
            return False
        else:
            character_list: Set[str] = set()
            for line in split_text[1:]:
                if (char_split := line.split("·")) and len(char_split) == 2:
                    character_list.add(char_split[0].strip())
            user_data: MudaeUserData = self.storage.users.get(message.author.id, "mudae_data")
            user_data.keyed_chars[message.guild.id] = character_list
            return True

    @tasks.loop(minutes=1)
    async def tradestreak_loop(self):
        now = datetime.utcnow()
        if not self.ts_cycle:
            logger.debug("Tradestreak cycle not set, going to set it!")
            self.ts_cycle = now.replace(hour=16, minute=0, second=0, microsecond=0) + timedelta(days=1)
            # self.ts_cycle = now + timedelta(minutes=1)
        if self.ts_cycle < now:
            logger.debug("Running TS Cycle!")
            self.ts_cycle = None
            for user_id in self.cache.has_features_enabled:
                mudae_data: MudaeUserData = self.storage.users.get(user_id, "mudae_data")
                if check_for_failed_quest(mudae_data.ts_quests):
                    user: discord.User = self.bot.get_user(user_id)
                    dm_channel = user.dm_channel
                    if not dm_channel:
                        await user.create_dm()
                        dm_channel = user.dm_channel
                    await dm_channel.send("You failed to trade a character, resetting your streak to 0!")
                    mudae_data.ts_streak = 0
                for guild_id in mudae_data.ts_enabled:
                    guild: discord.Guild = self.bot.get_guild(guild_id)
                    if guild and mudae_data.ts_enabled[guild_id]:
                        char_list = list(mudae_data.claimed_chars[guild_id] - mudae_data.keyed_chars[guild_id])
                        if char_list:
                            count = mudae_data.ts_amount[guild_id] if mudae_data.ts_amount[guild_id] < len(char_list) else \
                                len(char_list)
                            mudae_data.ts_quests[guild_id] = dict()
                            char_string = f"Todays trade quests for `{guild.name}`:\n"
                            for char_name in random.sample(char_list, count):
                                mudae_data.ts_quests[guild_id][char_name] = False
                                char_string += f"`{char_name}`\n"
                            user: discord.User = self.bot.get_user(user_id)
                            dm_channel = user.dm_channel
                            if not dm_channel:
                                await user.create_dm()
                                dm_channel = user.dm_channel
                            await dm_channel.send(char_string)

    @mudaemod_ts_set.error
    async def on_error(self, context: commands.Context, exception: Exception):
        if isinstance(exception, MissingRequiredArgument):
            await context.send_help(context.command)
        elif isinstance(exception, BadArgument):
            await context.send(universal_text.ERROR_BAD_ARGUMENT_NUMBERS)
        else:
            await context.send("an error has occured, check console.")
            raise exception

    async def detect_marry(self, message: discord.Message):
        if (marry_detect := re.fullmatch(MARRY_REGEX, message.content)) and \
                len(marry_detect.groups()) == 2 and \
                (member := message.guild.get_member_named(marry_detect.groups()[0])):
            user_data: MudaeUserData = self.storage.users.get(member.id, "mudae_data")
            if message.guild.id not in user_data.claimed_chars:
                user_data.claimed_chars[message.guild.id] = set()
            user_data.claimed_chars[message.guild.id].add(marry_detect.groups()[1])
            logger.debug("Adding character to sync list.")
            await message.channel.send("Character added to sync list!")

    async def detect_me_middle(self, message: discord.Message):
        if message.content.strip().endswith(". Do you confirm the exchange? (y/n/yes/no)"):
            cut_msg = message.content.strip()[:-len(". Do you confirm the exchange? (y/n/yes/no)")]
            trade_regex = re.match(TRADE_MIDDLE_REGEX, cut_msg)
            member_id = trade_regex.groups()[0]
            trade_string = trade_regex.groups()[1]
            logger.debug("Found middle of trade.")
            if len(trade_regex.groups()) == 2 and (member := message.guild.get_member(int(member_id))):
                logger.debug("Groups = 2, member found.")
                split_trade = trade_string.replace("<:kakera:469835869059153940>", " ").replace("*", ""). \
                    strip().split(" vs ")
                logger.debug(trade_string)
                logger.debug(split_trade)
                # noinspection PyUnboundLocalVariable
                if len(split_trade) == 2 and member.id in self.waiting_for_bot_message:
                    trade_data = self.waiting_for_bot_message.pop(member.id)
                    trade_data.first_mar = split_trade[0]
                    trade_data.second_mar = split_trade[1]
                    self.waiting_for_bot_message[(split_trade[0], split_trade[1])] = trade_data
                    logger.debug("Trade middle found!")

    async def detect_me_end(self, message: discord.Message):
        if message.content.strip().startswith("🤝 The exchange is over: "):
            logger.debug("Found exchange is over.")
            cut_msg = message.content.strip()[len("🤝 The exchange is over: "):]
            split_trade = cut_msg.replace("<:kakera:469835869059153940>", " ").replace("*", "").strip(). \
                split(" vs ")
            if len(split_trade) == 2:
                if trade_data := self.waiting_for_bot_message.get((split_trade[0], split_trade[1]), False):
                    mudae_data1: MudaeUserData = self.storage.users.get(trade_data.first, "mudae_data")
                    if message.guild.id not in mudae_data1.claimed_chars:
                        mudae_data1.claimed_chars[message.guild.id] = set()
                    mudae_data2: MudaeUserData = self.storage.users.get(trade_data.second, "mudae_data")
                    if message.guild.id not in mudae_data2.claimed_chars:
                        mudae_data2.claimed_chars[message.guild.id] = set()
                    char_list1 = []
                    for char_name in trade_data.first_mar.split("+")[0].split(","):
                        if char_name.strip() in mudae_data2.ts_quests.get(message.guild.id, set()):
                            mudae_data2.ts_quests[message.guild.id][char_name.strip()] = False
                            mudae_data2.ts_streak += -1
                            await message.channel.send("A trade has been unfulfilled...")
                        if char_name.strip() in mudae_data1.ts_quests.get(message.guild.id, set()):
                            mudae_data1.ts_quests[message.guild.id][char_name.strip()] = True
                            mudae_data1.ts_streak += 1
                            if mudae_data1.ts_streak > mudae_data1.ts_highest_streak:
                                mudae_data1.ts_highest_streak = mudae_data1.ts_streak
                            await message.channel.send("A trade has been fulfilled!")

                        mudae_data1.claimed_chars[message.guild.id].discard(char_name.strip())
                        mudae_data2.claimed_chars[message.guild.id].add(char_name.strip())
                        char_list1.append(char_name.strip())

                    char_list2 = []
                    for char_name in trade_data.second_mar.split("+")[0].split(","):
                        if char_name.strip() in mudae_data2.ts_quests.get(message.guild.id, set()):
                            mudae_data2.ts_quests[message.guild.id][char_name.strip()] = True
                            mudae_data2.ts_streak += 1
                            if mudae_data2.ts_streak > mudae_data2.ts_highest_streak:
                                mudae_data2.ts_highest_streak = mudae_data2.ts_streak
                            await message.channel.send("A trade has been fulfilled!")
                        if char_name.strip() in mudae_data1.ts_quests.get(message.guild.id, set()):
                            mudae_data1.ts_quests[message.guild.id][char_name.strip()] = False
                            mudae_data1.ts_streak += -1
                            await message.channel.send("A trade has been unfulfilled...")
                        mudae_data2.claimed_chars[message.guild.id].discard(char_name.strip())
                        mudae_data1.claimed_chars[message.guild.id].add(char_name.strip())
                        char_list2.append(char_name.strip())


async def process_message_and_run(message: discord.Message, coroutine) -> bool:
    if not message.attachments:
        return await coroutine(message, message.content)
    elif len(message.attachments) > 1:
        await message.channel.send("Multiple attachements given? Not supported.")
        return False
    elif message.attachments[0].filename != "message.txt":
        await message.channel.send("Attachment is not named `message.txt`, please leave it as the default!")
        return False
    else:
        byte_content: bytes = await message.attachments[0].read()
        return await coroutine(message, byte_content.decode("utf8"))


def check_for_failed_quest(quests: Dict[int, Dict[str, bool]]) -> bool:
    for guild_id in quests:
        for char_name in quests[guild_id]:
            if quests[guild_id][char_name] is False:
                return True
    return False
