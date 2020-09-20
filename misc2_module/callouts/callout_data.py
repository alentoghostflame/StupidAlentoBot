from alento_bot import guild_data_transformer


@guild_data_transformer(name="callout_guild_config")
class CalloutGuildConfig:
    def __init__(self):
        self.deletes: bool = False
        self.fistbumps: bool = True
