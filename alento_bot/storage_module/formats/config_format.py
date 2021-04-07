from alento_bot.storage_module.formats.save_format import config_file


@config_file("config.yaml")
class ConfigData:
    def __init__(self):
        self._c_discord_command_prefix = "Character/symbol required to prefix all your commands with."
        self.discord_command_prefix = ";"
        self._c_discord_bot_token = "Your discord bot token, get it from the Discord app developer page."
        self.discord_bot_token = ""
        self._c_data_folder_path = "Path to store all cache/guild/user storage files. Will create the folder if needed."
        self.data_folder_path = "data"
        self._c_bot_invite_link = "Link sent when the invite command is used. Only used for the invite command."
        self.bot_invite_link = ""
