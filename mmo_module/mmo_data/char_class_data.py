from typing import Dict


class BaseCharClass:
    def __init__(self):
        self.add_max_health: int = 0
        self.add_max_mana: int = 0
        self.add_health_per_min: int = 0
        self.add_mana_per_min: int = 0


class StarterClass(BaseCharClass):
    def __init__(self):
        BaseCharClass.__init__(self)


CHARACTER_CLASSES: Dict[str, type] = {"Starter": StarterClass}
