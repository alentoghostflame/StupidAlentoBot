from alento_bot import user_data_transformer
from mmo_module.mmo_data.char_class_data import BaseCharClass, StarterClass, get_character_class, get_class_levels
from mmo_module.mmo_data.base_char_stats import BaseCharStats, DefaultSaveData
from mmo_module.mmo_data import spell_data
# from mmo_module.mmo_data.equipment_data import BaseEquipment
from mmo_module.mmo_data import text
from typing import Optional, Dict
from discord.ext import commands, tasks
import logging


NAME_LENGTH_LIMIT = 32
DEFAULT_NAME = "Default Name"


logger = logging.getLogger("main_bot")


class CombatHandler:
    def __init__(self):
        self.active: bool = False
        self.alive: bool = True
        self.target: Optional[int] = None
        self.task: Optional[tasks.Loop] = None
        self.on_team1: Optional[bool] = None
        self.attack: spell_data.BaseSpell = spell_data.BASIC_ATTACK


class BaseCharacter:
    def __init__(self, save_data: DefaultSaveData = None, load: bool = True):
        if save_data:
            self._save_data: DefaultSaveData = save_data
        else:
            self._save_data: DefaultSaveData = DefaultSaveData()
        if self._save_data.char_class:
            self.char_class: BaseCharClass = get_character_class(self._save_data.char_class)
        else:
            self.char_class: BaseCharClass = StarterClass()
        self.stats: BaseCharStats = BaseCharStats(self._save_data)

        self._equipment: dict = dict()
        self._default_spell: Optional[spell_data.BaseSpell] = None
        self.combat: CombatHandler = CombatHandler()

        # self.stats.calculate_stats()

    def deal_damage(self, amount: float) -> float:
        return self.stats.deal_damage(amount)

    def get_damage(self) -> float:
        return self.stats.get_damage() * self.combat.attack.phys_amp

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

    def tick(self):
        self.stats.tick(finish_tick=True)

    async def context_tick(self, context: commands.Context, do_tick: bool = True):
        if do_tick:
            self.tick()

        if self.stats.xp.leveled_up:
            await context.send(text.LEVEL_UP_MESSAGE.format(self._save_data.name, self.stats.xp.level))
            self.stats.xp.leveled_up = False

            level_thresholds, class_levels = get_class_levels()
            for level_threshold in level_thresholds:
                if self.char_class.min_level < level_threshold <= self.stats.xp.level:
                    logger.debug(f"{self.char_class.min_level} {level_threshold} {self.stats.xp.level} "
                                 f"{type(self.char_class)} {self.char_class.name}")
                    await context.send(text.CLASSES_AVAILABLE_MESSAGE)
                    break

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
