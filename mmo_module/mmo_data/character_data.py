from alento_bot import user_data_transformer
from mmo_module.mmo_data.char_class_data import BaseCharClass, StarterClass, get_character_class, get_class_levels
from mmo_module.mmo_data.base_char_stats import BaseNumberStats, DefaultSaveData
from mmo_module.mmo_data.spell_data import BaseSpell
from mmo_module.mmo_data import spell_data
from mmo_module.mmo_core import get_display_bar
# from mmo_module.mmo_data.equipment_data import BaseEquipment
from mmo_module.mmo_data import text
from typing import Optional, Dict
from discord.ext import commands, tasks
from datetime import datetime
import logging


NAME_LENGTH_LIMIT = 32
DEFAULT_NAME = "Default Name"


logger = logging.getLogger("main_bot")


class ModifiedStats:
    def __init__(self, save_data: DefaultSaveData, base_stats: BaseNumberStats, equipment=None):
        self._save_data: DefaultSaveData = save_data
        self._base_stats: BaseNumberStats = base_stats
        self._equipment: dict = None
        self._buffs: list = list()
        # This goes through the buffs, the buffs do not read this.
        # TODO: Go through buffs and modify stats as needed.

        self._health_per_min: float = 0
        self._max_health: float = 0
        self._max_health_mod: float = 0.0
        self._max_health_amp: float = 1.0
        self._mana_per_min: float = 0
        self._max_mana: float = 0
        self._max_mana_mod: float = 0.0
        self._max_mana_amp: float = 1.0
        self._speed: float = 0
        self._speed_mod: float = 0.0
        self._speed_amp: float = 1.0

        self._physical_attack: float = 0
        self._physical_attack_mod: float = 0.0
        self._physical_attack_amp: float = 1.0
        self._physical_resist: float = 0
        self._physical_resist_mod: float = 0.0
        self._physical_resist_amp: float = 1.0

        self._magical_attack: float = 0
        self._magical_attack_mod: float = 0.0
        self._magical_attack_amp: float = 1.0
        self._magical_resist: float = 0
        self._magical_resist_mod: float = 0.0
        self._magical_resist_amp: float = 1.0

    @property
    def health(self) -> float:
        return self._save_data.health

    @health.setter
    def health(self, new_amount: float):
        self._save_data.health = new_amount
        if self._save_data.health > self.max_health:
            self._save_data.health = self.max_health
        elif self._save_data.health < 0:
            self._save_data.health = 0

    @property
    def health_per_min(self) -> float:
        return self._health_per_min

    @property
    def max_health(self) -> float:
        return self._max_health

    @property
    def mana_per_min(self) -> float:
        return self._mana_per_min

    @property
    def mana(self) -> float:
        return self._save_data.mana

    @mana.setter
    def mana(self, new_amount: float):
        self._save_data.mana = new_amount
        if self._save_data.mana > self.max_mana:
            self._save_data.mana = self.max_mana
        elif self._save_data.mana < 0:
            self._save_data.mana = 0

    @property
    def max_mana(self) -> float:
        return self._max_mana

    @property
    def speed(self) -> float:
        return self._speed

    @property
    def physical_attack(self) -> float:
        return self._physical_attack

    @property
    def physical_resist(self) -> float:
        return self._physical_resist

    @property
    def magical_attack(self) -> float:
        return self._magical_attack

    @property
    def magical_resist(self) -> float:
        return self._magical_resist

    def calculate(self):
        # self._base_stats.calculate_stats()
        self.calc_max_health()
        self.calc_health_per_min()
        self.calc_max_mana()
        self.calc_mana_per_min()
        self.calc_speed()
        self.calc_physical_attack()
        self.calc_physical_resist()
        self.calc_magical_attack()
        self.calc_magical_resist()
        # TODO: Iterate through buffs and modify stats as needed.

    def calc_health_per_min(self):
        self._health_per_min = self._base_stats.health_per_min

    def calc_max_health(self):
        self._max_health = self._base_stats.max_health * self._max_health_amp + self._max_health_mod

    def calc_mana_per_min(self):
        self._mana_per_min = self._base_stats.mana_per_min

    def calc_max_mana(self):
        self._max_mana = self._base_stats.max_mana * self._max_mana_amp + self._max_mana_mod

    def calc_speed(self):
        self._speed = self._base_stats.speed

    def calc_physical_attack(self):
        self._physical_attack = self._base_stats.physical_attack * self._physical_attack_amp + self._physical_attack_mod

    def calc_physical_resist(self):
        self._physical_resist = self._base_stats.physical_resist * self._physical_resist_amp

    def calc_magical_attack(self):
        self._magical_attack = self._base_stats.magical_attack * self._magical_attack_amp + self._magical_attack_mod

    def calc_magical_resist(self):
        self._magical_resist = self._base_stats.magical_resist * self._magical_resist_amp

    def deal_damage(self, base_damage: float, spell: BaseSpell) -> float:
        # TODO: Add actual damage resists once multiple damage types are solidified.
        damage = base_damage * spell.phys_amp + spell.phys_dmg
        self.health -= damage
        return damage


class CombatHandler:
    def __init__(self):
        self.active: bool = False
        self.alive: bool = True
        self.target: Optional[int] = None
        self.task: Optional[tasks.Loop] = None
        self.on_team1: Optional[bool] = None
        self.attack: spell_data.BaseSpell = spell_data.BASIC_ATTACK


class BaseCharacter:
    def __init__(self, save_data: DefaultSaveData = None):
        if save_data:
            self._save_data: DefaultSaveData = save_data
        else:
            self._save_data: DefaultSaveData = DefaultSaveData()

        if self._save_data.char_class:
            self.char_class: BaseCharClass = get_character_class(self._save_data.char_class)
        else:
            self.char_class: BaseCharClass = StarterClass()

        self._base_stats: BaseNumberStats = BaseNumberStats(self._save_data)
        self._default_spell: Optional[BaseSpell] = None
        self._equipment: dict = None
        self._inventory: dict = None
        self.combat: CombatHandler = CombatHandler()

        self.stats = ModifiedStats(self._save_data, self._base_stats, self._equipment)

    @property
    def health(self):
        return self.stats.health

    @property
    def mana(self):
        return self.stats.mana

    def deal_damage(self, base_damage: float, spell: BaseSpell):
        # TODO: Replace once spells get worked out.
        self.stats.deal_damage(base_damage, spell)

    def get_damage(self) -> float:
        # TODO: Replace once spells get worked out.
        return self.stats.physical_attack * self.combat.attack.phys_amp

# class BaseCharacter:
#     def __init__(self, save_data: DefaultSaveData = None, load: bool = True):
#         if save_data:
#             self._save_data: DefaultSaveData = save_data
#         else:
#             self._save_data: DefaultSaveData = DefaultSaveData()
#         if self._save_data.char_class:
#             self.char_class: BaseCharClass = get_character_class(self._save_data.char_class)
#         else:
#             self.char_class: BaseCharClass = StarterClass()
#         self.stats: BaseCharStats = BaseCharStats(self._save_data)
#
#         self._equipment: dict = dict()
#         self._default_spell: Optional[spell_data.BaseSpell] = None
#         self.combat: CombatHandler = CombatHandler()
#
#         # self.stats.calculate_stats()
#
#     def deal_damage(self, amount: float) -> float:
#         return self.stats.deal_damage(amount)
#
#     def get_damage(self) -> float:
#         return self.stats.get_damage() * self.combat.attack.phys_amp

    @property
    def default_spell(self):
        if not self._default_spell:
            found_spell = False
            for spell in self.char_class.spells:
                if spell.name.lower() == self._save_data.default_spell:
                    found_spell = True
                    self._default_spell = spell
            if not found_spell:
                self._default_spell = spell_data.BASIC_ATTACK
        return self._default_spell

    @default_spell.setter
    def default_spell(self, spell: spell_data.BaseSpell):
        if spell in self.char_class.spells:
            self._default_spell = spell
            self._save_data.default_spell = spell.name

    # def tick(self):
    #     self.stats.tick(finish_tick=True)
    def init_tick(self):
        if self.health is None:
            self.stats.health = self.stats.max_health
        if self.mana is None:
            self.stats.mana = self.stats.max_mana

    def tick(self, finish_tick: bool = True):
        self.stats.calculate()
        self.init_tick()
        if self._save_data.last_tick:
            time_now = datetime.utcnow()
            time_diff_sec = round((time_now - self._save_data.last_tick).total_seconds())
            self._base_stats.xp.tick()
            self.stats.calculate()

            # if self.hp.current is not self.hp.max:
            if self.stats.health is not self.stats.max_health:
                self.stats.health += self.stats.health_per_min * time_diff_sec / 60
            if self.stats.mana is not self.stats.max_mana:
                self.stats.mana += self.stats.health_per_min * time_diff_sec / 60
            #     self.hp.current += self.hp.per_min * time_diff_sec / 60
            # if self.mp.current is not self.mp.max:
            #     self.mp.current += self.mp.per_min * time_diff_sec / 60
            if finish_tick:
                self._save_data.last_tick = time_now
        else:
            self._save_data.last_tick = datetime.utcnow()

    async def context_tick(self, context: commands.Context, do_tick: bool = True):
        if do_tick:
            self.tick()

        if self._base_stats.xp.leveled_up:
            await context.send(text.LEVEL_UP_MESSAGE.format(self._save_data.name, self._base_stats.xp.level))
            self._base_stats.xp.leveled_up = False

            level_thresholds, class_levels = get_class_levels()
            for level_threshold in level_thresholds:
                if self.char_class.min_level < level_threshold <= self._base_stats.xp.level:
                    logger.debug(f"{self.char_class.min_level} {level_threshold} {self._base_stats.xp.level} "
                                 f"{type(self.char_class)} {self.char_class.name}")
                    await context.send(text.CLASSES_AVAILABLE_MESSAGE)
                    break

    @property
    def level(self) -> int:
        return self._save_data.level

    @property
    def xp_worth(self) -> int:
        return self._base_stats.xp.worth

    @property
    def xp(self) -> int:
        return self._base_stats.xp.current

    @xp.setter
    def xp(self, amount: int):
        self._base_stats.xp.current += amount

    @property
    def char_class(self) -> BaseCharClass:
        return self._char_class

    @char_class.setter
    def char_class(self, char_class: BaseCharClass):
        self._save_data.char_class = char_class.name
        self._char_class = char_class

    @property
    def name(self) -> str:
        if self._save_data.name:
            return self._save_data.name
        else:
            return DEFAULT_NAME

    @name.setter
    def name(self, new_name: str):
        self._save_data.name = new_name[:NAME_LENGTH_LIMIT]

    def get_health_display(self, adjustment: int = 0, regen: bool = False):
        if regen:
            return get_display_bar("Health", self.health, self.stats.max_health, adjustment,
                                   f", at {round(self.stats.health_per_min, 1)}/m")
        else:
            return get_display_bar("Health", self.health, self.stats.max_health, adjustment)

    def get_mana_display(self, adjustment: int = 0, regen: bool = False) -> str:
        if regen:
            return get_display_bar("Mana", self.mana, self.stats.max_mana, adjustment,
                                   f", at {round(self.stats.mana_per_min, 1)}/m")
        else:
            return get_display_bar("Mana", self.mana, self.stats.max_mana, adjustment)

    def get_xp_display(self, adjustment: int = 0):
        return get_display_bar("XP", self._base_stats.xp.current, self._base_stats.xp.xp_to_next_level, adjustment,
                               f", LV {self._save_data.level}")

