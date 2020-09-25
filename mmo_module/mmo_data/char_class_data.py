from typing import Dict, List, Type


class BaseCharClass:
    def __init__(self):
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
        self.level_thresholds: List[int] = [10, ]
        self.classes: Dict[int, Dict[str, Type[BaseCharClass]]] = dict()


class StarterClass(BaseCharClass):
    def __init__(self):
        BaseCharClass.__init__(self)


CHARACTER_CLASSES: Dict[str, type] = {"starter": StarterClass}


def get_character_class(class_name: str) -> BaseCharClass:
    return CHARACTER_CLASSES.get(class_name.lower(), StarterClass)()

