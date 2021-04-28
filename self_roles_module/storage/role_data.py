from alento_bot import guild_data_transformer
from typing import Dict, List


@guild_data_transformer(name="self_roles_data")
class RoleSelfAssignData:
    def __init__(self):
        self.roles: Dict[str, int] = dict()
        self.auto_enabled: bool = False
        self.auto_role: int = 0
        self.groups: Dict[str, List[str]] = dict()
