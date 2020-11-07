from mmo_module.mmo_data import text
from mmo_module.mmo_core import DamageTypes


class BaseSpell:
    def __init__(self, damage_types: DamageTypes, name: str, brief: str, mana_cost: float,
                 phys_dmg: float = 0, phys_amp: float = 1.0,
                 magi_dmg: float = 0, magi_amp: float = 1.0):
        self.type: DamageTypes = damage_types
        self.name: str = name
        self.brief: str = brief
        self.mana_cost: float = mana_cost
        self.phys_dmg: float = phys_dmg
        self.phys_amp: float = phys_amp
        self.magi_dmg: float = magi_dmg
        self.magi_amp: float = magi_amp


BASIC_ATTACK = BaseSpell(DamageTypes(physical=True), "Basic", text.SPELL_BASIC_ATTACK, 0)
DOUBLE_ATTACK = BaseSpell(DamageTypes(physical=True), "Double", text.SPELL_DOUBLE_ATTACK, 10, phys_amp=1.5)
