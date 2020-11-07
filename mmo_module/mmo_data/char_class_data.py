from typing import Dict, List, Type, Tuple
from mmo_module.mmo_data import spell_data


class BaseCharClass:
    def __init__(self):
        self.name: str = "Base Class"
        self.min_level: int = 0
        self.is_monster: bool = False

        self.default_attack: spell_data.BaseSpell = spell_data.BASIC_ATTACK
        self.spells: List[spell_data.BaseSpell] = [spell_data.BASIC_ATTACK, spell_data.DOUBLE_ATTACK]


class StarterClass(BaseCharClass):
    def __init__(self):
        BaseCharClass.__init__(self)
        self.name = "starter"
        self.min_level = 0


CHARACTER_CLASSES: Dict[str, Type[BaseCharClass]] = dict()
for class_name_root in BaseCharClass.__subclasses__():
    CHARACTER_CLASSES[class_name_root().name] = class_name_root


def get_character_class(class_name: str) -> BaseCharClass:
    return CHARACTER_CLASSES.get(class_name.lower(), StarterClass)()


def get_class_levels() -> Tuple[List[int], Dict[int, List[str]]]:
    level_thresholds: List[int] = list()
    class_levels: Dict[int, List[str]] = dict()

    for class_name in CHARACTER_CLASSES:
        char_class = CHARACTER_CLASSES[class_name]()
        if char_class.min_level not in level_thresholds:
            level_thresholds.append(char_class.min_level)
        if char_class.min_level not in class_levels:
            class_levels[char_class.min_level] = list()
        class_levels[char_class.min_level].append(char_class.name.capitalize())

    level_thresholds.sort()
    return level_thresholds, class_levels
