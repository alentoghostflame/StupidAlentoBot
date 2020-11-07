from typing import Optional


class DamageTypes:
    def __init__(self, physical=False, magical=False):
        self.physical: bool = physical
        self.magical: bool = magical
