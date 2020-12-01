from discord.ext.commands.help import HelpCommand
from discord.ext import commands
from random import randint
from typing import Iterable
import itertools
import discord


# class AlentoHelpPaginator:
#     def __init__(self, max_size: int = 2000):
#         self.max_size: int = max_size


class AlentoHelpCommand(HelpCommand):
    def __init__(self):
        self.no_category = "No Category"
        HelpCommand.__init__(self)

    # noinspection PyMethodMayBeStatic
    def add_indented_commands(self, embed: discord.Embed, cmds: Iterable[commands.Command], heading: str):
        if cmds:
            command_str = ""
            width = 0
            for cmd in cmds:
                string_addon = f"`{cmd.qualified_name}{'|' + '|'.join(cmd.aliases) if cmd.aliases else ''}`: " \
                               f"{cmd.short_doc if cmd.short_doc else 'No description'}\n"
                command_str += string_addon
                if len(string_addon) > width:
                    width = len(string_addon)
            if width > 40:
                embed.add_field(name=heading, value=command_str, inline=False)
            else:
                embed.add_field(name=heading, value=command_str, inline=True)

    async def send_bot_help(self, mapping, inline_length: int = 0):
        context: commands.Context = self.context
        bot: commands.Bot = context.bot
        destination = self.get_destination()

        help_embed = discord.Embed(title="Bot Help", color=randint(0, 0xffffff))

        if bot.description:
            help_embed.add_field(name="Description", value=bot.description)

        # no_category = '\u200b{0.no_category}:'.format(self)
        no_category = f"​{self.no_category}"

        def get_category(command, *, no_cat=no_category):
            cog = command.cog
            return cog.qualified_name + ':' if cog is not None else no_cat

        filtered = await self.filter_commands(bot.commands, sort=True, key=get_category)
        # max_size = self.get_max_size(filtered)
        to_iterate = itertools.groupby(filtered, key=get_category)

        for category, bot_cmds in to_iterate:
            command_list = sorted(bot_cmds, key=lambda c: c.name)
            self.add_indented_commands(help_embed, command_list, category)

        await destination.send(embed=help_embed)

    async def send_command_help(self, command: commands.Command):
        bot: commands.Bot = self.context.bot
        destination = self.get_destination()
        if command.parents:
            title = self.context.prefix
            for parent in command.parents:
                title += f"{parent.name} "
            title += command.name
        else:
            title = command.name.capitalize()
        embed = discord.Embed(title=title, color=randint(0, 0xffffff))
        if command.description:
            command_desc = command.description
        elif command.brief:
            command_desc = command.brief
        else:
            command_desc = "None"

        embed.add_field(name="Description", value=command_desc, inline=False)
        if command.aliases:
            embed.add_field(name="Aliases", value=f"`{'|'.join(command.aliases)}`")
        command_sig = self.get_command_signature(command)
        embed.add_field(name="Usage", value=f"`{command_sig}`", inline=False)

        await destination.send(embed=embed)

    async def send_group_help(self, group: commands.Group):
        destination = self.get_destination()
        if group.parents:
            title = self.context.prefix
            for parent in group.parents:
                title += f"{parent.name} "
            title += group.name
        else:
            title = group.name.capitalize()
        help_embed = discord.Embed(title=title, color=randint(0, 0xffffff))
        if (desc_text := group.description) or (desc_text := group.brief):
            help_embed.add_field(name="Description", value=desc_text, inline=False)
        if group.aliases:
            help_embed.add_field(name="Aliases", value=f"`{'|'.join(group.aliases)}`")
        filtered = await self.filter_commands(group.commands, sort=True)
        self.add_indented_commands(help_embed, filtered, "Subcommands")
        help_embed.add_field(name="Usage", value=f"`{self.get_command_signature(group)}`", inline=False)

        await destination.send(embed=help_embed)
