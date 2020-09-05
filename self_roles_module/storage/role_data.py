from alento_bot import guild_data_transformer
import typing


@guild_data_transformer(name="self_roles_data")
class RoleSelfAssignData:
    def __init__(self, config, guild_id):
        super().__init__(config, guild_id)
        self.roles: typing.Dict[str, int] = dict()
