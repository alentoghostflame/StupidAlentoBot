from faq_module.commands import faq_cmds, faq_on_message
from faq_module.commands import text
from faq_module.storage import FAQManager, FAQConfig
from alento_bot import BaseModule, StorageManager, universal_text
from discord.ext import commands
from typing import Optional, Union
import logging
import discord


logger = logging.getLogger("main_bot")


class NotAllowedOrAdmin(Exception):
    pass


class FAQModule(BaseModule):
    def __init__(self, bot, storage):
        BaseModule.__init__(self, bot, storage)
        self.storage.guilds.register_data_name("faq_config", FAQConfig)
        self.faq_manager: FAQManager = FAQManager(self.storage)
        self.add_cog(FAQCog(self.storage, self.faq_manager, self.bot))


class FAQCog(commands.Cog, name="FAQ"):
    def __init__(self, storage: StorageManager, faq_manager: FAQManager, bot: commands.Bot):
        self.storage: StorageManager = storage
        self.faq_manager: FAQManager = faq_manager
        self.bot = bot

    async def is_allowed_or_admin(self, context: commands.Context) -> bool:
        faq_config: FAQConfig = self.storage.guilds.get(context.guild.id, "faq_config")
        if context.author.guild_permissions.administrator or faq_cmds.has_any_role(context.guild, faq_config.edit_roles,
                                                                                   context.author):
            return True
        else:
            raise NotAllowedOrAdmin

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild:
            faq_config: FAQConfig = self.storage.guilds.get(message.guild.id, "faq_config")
            if faq_config.enabled and not message.author.bot:
                context: commands.Context = await self.bot.get_context(message)
                if not context.valid:
                    await faq_on_message(self.faq_manager, message)

    @commands.guild_only()
    @commands.group(name="faq", description=text.FAQ_GROUP_DESCRIPTION, brief=text.FAQ_GROUP_BRIEF,
                    invoke_without_command=True)
    async def faq_group(self, context: commands.Context, *subcommand):
        if subcommand:
            await context.send(universal_text.INVALID_SUBCOMMAND)
        else:
            await context.send_help(context.command)

    @commands.guild_only()
    @faq_group.command(name="info", brief=text.FAQ_INFO_BRIEF)
    async def faq_info(self, context: commands.Context):
        faq_config: FAQConfig = self.storage.guilds.get(context.guild.id, "faq_config")
        await faq_cmds.send_list_embed(self.faq_manager, faq_config, context)

    @commands.guild_only()
    @faq_group.command(name="add", brief=text.FAQ_ADD_BRIEF)
    async def faq_add(self, context: commands.Context, keyword: str, phrase: str, image_url: Optional[str], *args):
        await self.is_allowed_or_admin(context)
        if args:
            await context.send(text.FAQ_TOO_MANY_ARGS)
        else:
            await faq_cmds.add_keyword(self.faq_manager, context, keyword, phrase, image_url)

    @commands.guild_only()
    @faq_group.command(name="remove", aliases=["rm", ], brief=text.FAQ_REMOVE_BRIEF)
    async def faq_remove(self, context: commands.Context, keyword: str):
        await self.is_allowed_or_admin(context)
        await faq_cmds.remove_keyword(self.faq_manager, context, keyword)

    @commands.guild_only()
    @faq_group.command(name="enable", brief=text.FAQ_ENABLE_BRIEF)
    async def faq_enable(self, context: commands.Context):
        await self.is_allowed_or_admin(context)
        faq_config: FAQConfig = self.storage.guilds.get(context.guild.id, "faq_config")
        await faq_cmds.faq_enable(faq_config, context)

    @commands.guild_only()
    @faq_group.command(name="disable", brief=text.FAQ_DISABLE_BRIEF)
    async def faq_disable(self, context: commands.Context):
        await self.is_allowed_or_admin(context)
        faq_config: FAQConfig = self.storage.guilds.get(context.guild.id, "faq_config")
        await faq_cmds.faq_disable(faq_config, context)

    @commands.guild_only()
    @faq_group.group(name="role", brief=text.FAQ_ROLE_GROUP_BRIEF, invoke_without_command=True)
    async def faq_role_group(self, context: commands.Context):
        if context.message.content.strip() == f"{context.prefix}faq {context.command.name}":
            await faq_cmds.send_faq_role_help_embed(context)
        else:
            await context.send(text.FAQ_ROLE_INVALID_SUBCOMMAND)

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @faq_role_group.command(name="add", brief=text.FAQ_ROLE_ADD_BRIEF)
    async def faq_role_add(self, context: commands.Context, role_mention: discord.Role):
        faq_config: FAQConfig = self.storage.guilds.get(context.guild.id, "faq_config")
        await faq_cmds.add_role(faq_config, context, role_mention)

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @faq_role_group.command(name="remove", aliases=["rm", ], brief=text.FAQ_ROLE_REMOVE_BRIEF)
    async def faq_role_remove(self, context: commands.Context, role_mention: Union[discord.Role, str]):
        faq_config: FAQConfig = self.storage.guilds.get(context.guild.id, "faq_config")
        await faq_cmds.remove_role(faq_config, context, role_mention)

    @faq_group.error
    @faq_info.error
    @faq_add.error
    @faq_remove.error
    @faq_enable.error
    @faq_disable.error
    @faq_role_group.error
    @faq_role_add.error
    @faq_role_remove.error
    async def faq_error_handler(self, context: commands.Context, error: Exception):
        if isinstance(error, commands.MissingRequiredArgument):
            await context.send(text.MISSING_REQUIRED_ARGUMENT.format(error))
        elif isinstance(error, commands.BadArgument):
            await context.send(str(error))
        elif isinstance(error, commands.NoPrivateMessage):
            await context.send(text.NO_PRIVATE_MESSAGE)
        elif isinstance(error, commands.MissingPermissions):
            await context.send(text.USER_MISSING_ADMIN_PERMISSION)
        else:
            await context.send(f"A CRITICAL ERROR OCCURED:\n\n {type(error)}\n\n {error}\n\n"
                               f"REPORT THIS TO SOMBRA/ALENTO GHOSTFLAME!")
            raise error




