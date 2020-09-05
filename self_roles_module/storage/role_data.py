from alento_bot import guild_data_transformer
import typing


@guild_data_transformer(name="self_roles_data")
class RoleSelfAssignData:
    def __init__(self):
        self.roles: typing.Dict[str, int] = dict()
