from alento_bot import BaseGuildCache
import typing


class RoleSelfAssignData(BaseGuildCache, name="self_roles_data"):
    def __init__(self, config, guild_id):
        super().__init__(config, guild_id)
        self.roles: typing.Dict[str, int] = dict()
