from mmo_module.mmo_data import GuildMMOConfig, UserMMOConfig, BasicMMODataStorage, CharacterSaveData
from alento_bot import BaseModule, StorageManager
from mmo_module import mmo_admin, mmo_user, text
from mmo_module.mmo_controller import MMOServer, MMOBattleManager
from discord.ext import commands
from datetime import datetime
from typing import Dict


class MMOModule(BaseModule):
    def __init__(self, bot, storage):
        BaseModule.__init__(self, bot, storage)
        # noinspection PyArgumentList
        self.storage.caches.register_cache("basic_mmo_data", BasicMMODataStorage(self.storage.config))
        self.storage.users.register_data_name("mmo_char_save", CharacterSaveData)
        self.storage.guilds.register_data_name("mmo_config", GuildMMOConfig)
        self.storage.users.register_data_name("mmo_config", UserMMOConfig)

        self.mmo_server: MMOServer = MMOServer(self.storage)

        self.add_cog(MMOAdmin(self.storage, self.mmo_server))
        self.add_cog(MMOUser(self.bot, self.storage, self.mmo_server))


class MMOUser(commands.Cog, name="MMO User"):
    def __init__(self, bot: commands.Bot, storage: StorageManager, mmo_server: MMOServer):
        self.bot: commands.Bot = bot
        self.storage: StorageManager = storage
        self.mmo_server: MMOServer = mmo_server
        self.mmo_battle: MMOBattleManager = MMOBattleManager(self.mmo_server)
        self._change_class_cooldowns: Dict[int, datetime] = dict()

    @commands.group(name="mmo", brief=text.MMO_BRIEF, invoke_without_command=True)
    async def mmo_user(self, context: commands.Context):
        if context.message.content.strip().lower() == f"{context.prefix}{context.command.name}":
            await context.send_help(context.command)
        else:
            await context.send(text.INVALID_COMMAND)

    @mmo_user.command(name="enable", brief=text.MMO_ENABLE_BRIEF)
    async def mmo_enable(self, context: commands.Context):
        await mmo_user.enable(self.mmo_server, context)

    @mmo_user.command(name="disable", brief=text.MMO_DISABLE_BRIEF)
    async def mmo_disable(self, context: commands.Context):
        await mmo_user.disable(self.mmo_server, context)

    @mmo_user.command(name="status", brief=text.MMO_STATUS_BRIEF)
    async def mmo_status(self, context: commands.Context):
        await mmo_user.status(self.mmo_server, context)

    @mmo_user.command(name="battle", brief=text.MMO_BATTLE_BRIEF)
    async def mmo_battle(self, context: commands.Context):
        if self.mmo_server.user.enabled(context.author.id):
            await self.mmo_battle.create_battle(context)
        else:
            await context.send(mmo_user.text.MMO_CURRENTLY_DISABLED)

    @mmo_user.command("attack", brief=text.MMO_ATTACK_BRIEF)
    async def mmo_attack(self, context: commands.Context, attack_name="Default Attack"):
        await self.mmo_battle.attack(context, attack_name)

    @mmo_user.group("char", brief=text.MMO_CHAR_BRIEF, invoke_without_command=True)
    async def mmo_char(self, context: commands.Context):
        if context.message.content.strip().lower() == f"{context.prefix}mmo char":
            await context.send_help(context.command)
        else:
            await context.send(text.INVALID_COMMAND)

    @mmo_char.group("class", brief=text.MMO_CHAR_CLASS_BRIEF, invoke_without_command=True)
    async def mmo_char_class(self, context: commands.Context, class_name: str = None):
        if context.message.content.strip().lower() == f"{context.prefix}mmo char class":
            await context.send_help(context.command)
        else:
            await mmo_user.set_class(self.mmo_server, self._change_class_cooldowns, context, class_name)

    @mmo_char_class.command("list", brief=text.MMO_CHAR_CLASS_LIST_BRIEF)
    async def mmo_char_class_list(self, context: commands.Context):
        await mmo_user.send_class_display(self.mmo_server, context)

    @mmo_char.command("name", brief=text.MMO_CHAR_NAME_BRIEF)
    async def mmo_char_name(self, context: commands.Context, new_name: str):
        await mmo_user.set_character_name(self.mmo_server, context, new_name)

    @mmo_char.command("attack", brief=text.MMO_CHAR_ATTACK_BRIEF)
    async def mmo_char_attack(self, context: commands.Context, new_attack: str):
        await mmo_user.set_default_attack(self.mmo_server, context, new_attack)

    @mmo_user.command("spells", brief=text.MMO_SPELLS_BRIEF)
    async def mmo_spells(self, context: commands.Context):
        await mmo_user.send_ability_display(self.mmo_server, context)


class MMOAdmin(commands.Cog, name="MMO Admin"):
    def __init__(self, storage: StorageManager, mmo_server: MMOServer):
        self.storage = storage
        self.mmo_server: MMOServer = mmo_server

    @commands.group(name="mmoa", brief=text.MMOA_BRIEF, invoke_without_command=True)
    async def mmoa(self, context: commands.Context):
        if context.message.content.strip() == f"{context.prefix}{context.command.name}":
            await context.send_help(context.command)
        else:
            await context.send(text.INVALID_COMMAND)

    @mmoa.command(name="enable", brief=text.MMOA_ENABLE_BRIEF)
    async def mmoa_enable(self, context: commands.Context):
        await mmo_admin.enable(self.mmo_server, context)

    @mmoa.command(name="disable", brief=text.MMOA_DISABLE_BRIEF)
    async def mmoa_disable(self, context: commands.Context):
        await mmo_admin.disable(self.mmo_server, context)
