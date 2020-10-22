from mmo_module.mmo_data.char_class_data import BaseCharClass
from mmo_module.mmo_data.character_data import BaseCharacter
from typing import Optional, Tuple
import random


SLIME_NAMES: Tuple[str, ...] = ("Black Slime", "Blue Slime", "Green Slime", "Red Slime", "White Slime", "Clear Slime")


class BaseEnemy(BaseCharacter):
    def __init__(self, char_class: BaseCharClass, name: str, level: int):
        BaseCharacter.__init__(self)

        self.char_class = char_class
        self._save_data.name = name
        self._save_data.level = level


def get_enemy(level_range: Tuple[int, int]) -> BaseEnemy:
    enemy = BaseEnemy(SlimeClass(), random.sample(SLIME_NAMES, 1)[0], random.randrange(level_range[0], level_range[1]))
    enemy.tick()
    return enemy


class SlimeClass(BaseCharClass):
    def __init__(self):
        BaseCharClass.__init__(self)
        self.name = "Slime Class"
        self.is_monster = True
        # self.physical_damage = 0.5
        # self.physical_damage_per_level = 0
        self.base_health = 10
        self.health_per_min = 0
        self.base_mana = 0
        self.mana_per_level = 1
        self.mana_per_min = 0
        self.attack_speed = 1.5



