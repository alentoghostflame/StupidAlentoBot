from stupid_utils import DataSync, default_server_data
from discord.ext import commands
from datetime import datetime
import admin_module
import info_module
import typing
import yaml
import os
# import discord
# import random


# ENABLE_PHRASES: set = {"true", "on", "enable", "online"}
# DISABLE_PHRASES: set = {"false", "off", "disable", "offline"}
# BOT_ID: str = "<@666768689768562738>"
#
# # noinspection SpellCheckingInspection
# PANKAKKE_EXPLICIT_TRIGGERS: set = {"Pancake", "pancake", "pan", "Pan", "Panc", "panc", "pancakke"}
# PANKAKKE_SOFT_TRIGGERS: set = {"Pancake", "pancake"}
# PANKAKKE_PHRASES: set = {"Don't you mean \"{0}\"", "I think you meant \"{0}\"",
#                          "Hey {1}, I think you should say \"{0}\" next time.",
#                          "Come on, Pankakke isn't all that hard to type, {1}", "> {0} \n Fixed that for you, {1}"}
#
# SELF_CORRECTION_EXPLICIT_TRIGGERS: set = {"SAB", "sab", "stupidalentobot"}
# SELF_CORRECTION_PHRASES: set = {"Just @mention me next time.", "Instead of calling me that, try {1}",
#                                 "Calling me the correct name ({1}) would be nice."}


class StupidAlentoBot:
    def __init__(self):
        self.bot = commands.Bot(command_prefix=";")

        self.data_sync = DataSync(self, self.bot)
        self.bot_data: typing.Dict[str, dict] = {"testing": default_server_data()}

        # self.bot.add_cog(OnMessageCog())
        self.bot.add_cog(admin_module.AdminCog(self.data_sync, self.bot_data))
        self.bot.add_cog(info_module.InfoCog(self.data_sync, self.bot_data))

    def run(self, token: str):
        self.bot.run(token)

    def load_data(self):
        print("Attempting to load bot data.")
        if os.path.exists("save_data.yaml"):
            file = open("save_data.yaml", "r")
            self.bot_data.update(yaml.full_load(file))
        else:
            print("File doesn't exist yet, using default.")
        print("Load complete.")

    def save_data(self):
        print("Attempting to save bot data.")
        file = open("save_data.yaml", "w+")
        yaml.dump(self.bot_data, file, default_flow_style=None)
        print("Save complete.")

    def update_data(self):
        print("Updating bot data.")


# class OnMessageCog(commands.Cog, name="On Message"):
#     def __init__(self):
#         super().__init__()
#         self.enable_phrases: set = ENABLE_PHRASES
#         self.disable_phrases: set = DISABLE_PHRASES
#         self.bot_id: str = BOT_ID
#
#         self.pankakke_enabled: bool = False
#         self.pankakke_explicit_triggers: set = PANKAKKE_EXPLICIT_TRIGGERS
#         self.pankakke_soft_triggers: set = PANKAKKE_SOFT_TRIGGERS
#         self.pankakke_phrases: set = PANKAKKE_PHRASES
#
#         self.self_correction_enabled: bool = True
#         self.self_correction_explicit_triggers: set = SELF_CORRECTION_EXPLICIT_TRIGGERS
#         self.self_correction_phrases: set = SELF_CORRECTION_PHRASES
#
#         self.messages_read: int = 0
#         self.messages_sent: int = 0
#
#     @commands.Cog.listener()
#     async def on_ready(self):
#         print("Logged in.")
#
#     @commands.Cog.listener()
#     async def on_message(self, message):
#         self.messages_read += 1
#         await self.pankakke(message)
#         await self.self_correction(message)
#         await self.correct_nu(message)
#
#     @commands.command(name="status", brief="Show the status of the bot.")
#     async def list_status(self, context):
#         embed = discord.Embed(title="Bot Status", color=0xffff00)
#         embed.add_field(name="Pankakke", value=str(self.pankakke_enabled), inline=True)
#         embed.add_field(name="Self Correction", value=str(self.self_correction_enabled), inline=True)
#         embed.add_field(name="Messages Read", value=str(self.messages_read + 1), inline=True)
#         embed.add_field(name="Messages Sent", value=str(self.messages_sent + 1), inline=True)
#         await context.send(embed=embed)
#         self.messages_sent += 1
#
#     @commands.command(name="messages", brief="List amount of messages read and sent")
#     async def list_messages(self, context):
#         await context.send("{} Messages read, {} Messages sent.".format(self.messages_read, self.messages_sent))
#
#     @commands.command(name="pankakke", usage="true/false, on/off, enable/disable, online/offline",
#                       brief="Enable or disable Pankakke mode.", aliases=["Pankakke"])
#     async def toggle_pankakke(self, context, arg=None):
#         self.pankakke_enabled, message = toggle_feature(arg, "Pankakke", self.enable_phrases, self.disable_phrases, self.pankakke_enabled)
#         await context.send(message)
#         self.messages_sent += 1
#
#     async def pankakke(self, message):
#         send = False
#         fixed_message = message.content
#         if self.pankakke_enabled and not message.author.bot:
#             if contains_explicit_trigger(self.pankakke_explicit_triggers, fixed_message):
#                 fixed_message = replace_explicit_trigger(self.pankakke_explicit_triggers, fixed_message, "Pankakke")
#                 send = True
#             if any(x in fixed_message for x in self.pankakke_soft_triggers):
#                 for word in self.pankakke_soft_triggers:
#                     fixed_message = fixed_message.replace(word, "Pankakke")
#                 send = True
#         if send:
#             self.messages_sent += 1
#             await message.channel.send(random.sample(self.pankakke_phrases, 1)[0].format(fixed_message,
#                                                                                          str(message.author).rsplit("#")
#                                                                                          [0]))
#
#     @commands.command(name="self_correction", usage="true/false, on/off, enable/disable, online/offline",
#                       brief="Enable or disable Self Correction mode.", aliases=["Self_Correction", "Self_correction"])
#     async def toggle_self_correction(self, context, arg=None):
#         self.self_correction_enabled, message = toggle_feature(arg, "self_correction", self.enable_phrases, self.disable_phrases, self.self_correction_enabled)
#         await context.send(message)
#         self.messages_sent += 1
#
#     async def self_correction(self, message):
#         if self.self_correction_enabled and not message.author.bot:
#             if contains_explicit_trigger(self.self_correction_explicit_triggers, message.content):
#                 self.messages_sent += 1
#                 await message.channel.send(random.sample(self.self_correction_phrases, 1)[0].format(str(message.author).rsplit("#")[0], self.bot_id))
#
#     async def correct_nu(self, message):
#         if not message.author.bot:
#             if contains_explicit_trigger({"nu"}, message.content):
#                 await message.channel.send("Do you mean \"no u\" or \"no\"?")
#
#
# def toggle_feature(arg: str, feature_name: str, enable_phrases: set, disable_phrases: set, enabled_var: bool):
#     if arg:
#         if any(x in arg.lower() for x in enable_phrases):
#             if enabled_var:
#                 return True, "{} is already enabled.".format(feature_name)
#             else:
#                 return True, "{} enabled.".format(feature_name)
#         elif any(x in arg.lower() for x in disable_phrases):
#             if enabled_var:
#                 return False, "{} disabled.".format(feature_name)
#             else:
#                 return False, "{} is already disabled.".format(feature_name)
#         else:
#             return enabled_var, "Argument `{}` is invalid for feature `{}`.".format(arg, feature_name)
#     else:
#         return enabled_var, "You need to actually say something after `;{}`, like enable or disable.".format(feature_name.lower())
#
#
# def contains_explicit_trigger(triggers: set, text: str) -> bool:
#     placeholder = text.split(" ")
#     for word in placeholder:
#         if word in triggers:
#             return True
#     return False
#
#
# def replace_explicit_trigger(triggers: set, text: str, replacement: str) -> str:
#     placeholder = text.split(" ")
#     for i in range(len(placeholder)):
#         if placeholder[i] in triggers:
#             placeholder[i] = replacement
#     return " ".join(placeholder)


stupid_bot = StupidAlentoBot()
stupid_bot.load_data()
stupid_bot.update_data()
stupid_bot.run("NjY2NzY4Njg5NzY4NTYyNzM4.Xh4-5A.N4MmdSZt8P7B16fgXt25JDcjBLA")
stupid_bot.save_data()
