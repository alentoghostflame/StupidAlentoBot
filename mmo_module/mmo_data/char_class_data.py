from typing import Dict, List, Type, Tuple


class BaseCharClass:
    def __init__(self):
        self.name: str = "base"
        self.min_level: int = 0
        self.is_monster: bool = False

        self.base_health: int = 20
        self.health_per_level: int = 4
        self.health_per_min: float = 1
        self.base_mana: int = 5
        self.mana_per_level: int = 1
        self.mana_per_min: float = 0.5

        self.attack_speed: float = 1
        self.physical_damage: float = 4
        self.physical_damage_per_level: float = 1
        self.magical_damage: float = 4
        self.magical_damage_per_level: float = 1


class CharacterClassManager:
    def __init__(self):
        # self.level_thresholds: List[int] = [10, ]
        self.classes: Dict[int, Dict[str, Type[BaseCharClass]]] = dict()


class StarterClass(BaseCharClass):
    def __init__(self):
        BaseCharClass.__init__(self)
        self.name = "starter"
        self.min_level = 0


class MageClass(BaseCharClass):
    def __init__(self):
        BaseCharClass.__init__(self)
        self.name = "mage"
        self.min_level = 10

        self.health_per_min = 2
        self.base_mana = 10
        self.mana_per_level = 5
        self.mana_per_min = 5
        self.magical_damage = 6
        self.magical_damage_per_level = 2


class WarriorClass(BaseCharClass):
    def __init__(self):
        BaseCharClass.__init__(self)
        self.name = "warrior"
        self.min_level = 10

        self.health_per_level = 5
        self.health_per_min = 5
        self.mana_per_min = 2
        self.physical_damage = 6
        self.physical_damage_per_level = 2


class RogueClass(BaseCharClass):
    def __init__(self):
        BaseCharClass.__init__(self)
        self.name = "rogue"
        self.min_level = 10

        self.health_per_min = 3
        self.mana_per_min = 3
        self.mana_per_level = 2

        self.attack_speed = 0.75


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
