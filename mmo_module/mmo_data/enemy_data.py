from mmo_module.mmo_data.character_data import BaseCharacter


class BaseEnemy(BaseCharacter):
    def __init__(self):
        BaseCharacter.__init__(self)
