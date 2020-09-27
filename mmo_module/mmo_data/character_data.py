from alento_bot import user_data_transformer
from mmo_module.mmo_data.char_class_data import BaseCharClass, StarterClass, get_character_class
from mmo_module.mmo_data.equipment_data import BaseEquipment
from mmo_module.mmo_data.small_data import BaseResists
from mmo_module.mmo_data import text
from typing import Optional, Dict
from discord.ext import commands, tasks
from datetime import datetime
import logging


logger = logging.getLogger("main_bot")


class DefaultSaveData:
    def __init__(self):
        self.char_class: Optional[str] = None
        self.name: Optional[str] = None
        self.health: Optional[float] = None
        self.mana: Optional[float] = None
        self.xp: int = 0
        self.level: int = 0
        self.equipment: Dict[dict] = dict()
        self.last_tick: Optional[datetime] = None


@user_data_transformer(name="mmo_char_save")
class CharacterSaveData(DefaultSaveData):
    def __init__(self):
        DefaultSaveData.__init__(self)


class HealthHandler:
    def __init__(self, save_data: DefaultSaveData):
        self._save_data = save_data
        self.max: Optional[float] = None
        self.per_min: Optional[float] = None

    def set(self, amount: float):
        self._save_data.health = amount
        if self._save_data.health > self.max:
            self._save_data.health = self.max
        elif self._save_data.health < 0:
            self._save_data.health = 0

    def adjust(self, amount: float):
        self._save_data.health += amount
        if self._save_data.health < 0:
            self._save_data.health = 0
        elif self._save_data.health > self.max:
            self._save_data.health = self.max

    def get(self) -> float:
        return self._save_data.health

    def get_display(self, adjustment: int = 0, regen: bool = False) -> str:
        if regen:
            return get_display_bar("Health", self.get(), self.max, adjustment, f", at {round(self.per_min, 1)}/m")
        else:
            return get_display_bar("Health", self.get(), self.max, adjustment)


class ManaHandler:
    def __init__(self, save_data: DefaultSaveData):
        self._save_data = save_data
        self.max: Optional[float] = None
        self.per_min: Optional[float] = None

    def set(self, amount: float):
        self._save_data.mana = amount
        if self._save_data.mana > self.max:
            self._save_data.mana = self.max
        elif self._save_data.mana < 0:
            self._save_data.mana = 0

    def adjust(self, amount: float):
        self._save_data.mana += amount
        if self._save_data.mana < 0:
            self._save_data.mana = 0
        elif self._save_data.mana > self.max:
            self._save_data.mana = self.max

    def get(self) -> float:
        return self._save_data.mana

    def get_display(self, adjustment: int = 0, regen: bool = False) -> str:
        if regen:
            return get_display_bar("Mana", self.get(), self.max, adjustment, f", at {round(self.per_min, 1)}/m")
        else:
            return get_display_bar("Mana", self.get(), self.max, adjustment)


class XPHandler:
    def __init__(self, save_data: DefaultSaveData):
        self._save_data = save_data
        self._xp_to_next_level: Optional[int] = None
        self.leveled_up: bool = False

    def calc_xp_to_next_level(self) -> int:
        self._xp_to_next_level = 100 + 20 * self._save_data.level
        return self._xp_to_next_level

    def _level_up(self):
        if self._save_data.xp >= self._xp_to_next_level:
            self._save_data.xp -= self._xp_to_next_level
            self._save_data.level += 1
            self.leveled_up = True
            self.calc_xp_to_next_level()

    def tick(self):
        while self._save_data.xp >= self.calc_xp_to_next_level():
            self._level_up()

    def adjust(self, amount: int):
        self._save_data.xp += amount

    def get(self) -> int:
        return self._save_data.xp

    def get_level(self) -> int:
        return self._save_data.level

    def get_display(self, adjustment: int = 0):
        return get_display_bar("XP", self.get(), self.calc_xp_to_next_level(), adjustment,
                               f", LV {self._save_data.level}")

    def get_worth(self) -> int:
        return 50 + 10 * self.get_level()


class CombatHandler:
    def __init__(self):
        self.active: bool = False
        self.alive: bool = True
        self.target: Optional[int] = None
        self.task: Optional[tasks.Loop] = None
        self.on_team1: Optional[bool] = None
        self.attack: Optional[str] = None


class BaseCharacter:
    def __init__(self, save_data: CharacterSaveData = None, load: bool = True):
        if save_data:
            self._save_data: CharacterSaveData = save_data
        else:
            self._save_data = DefaultSaveData()

        self.equipment: dict = dict()
        self.char_class: BaseCharClass = StarterClass()

        self.resists: BaseResists = BaseResists()
        self.xp: XPHandler = XPHandler(self._save_data)
        self.health: HealthHandler = HealthHandler(self._save_data)
        self.mana: ManaHandler = ManaHandler(self._save_data)
        self.combat: CombatHandler = CombatHandler()
        self.attack_speed: Optional[float] = self.char_class.attack_speed
        self.physical_damage: Optional[float] = self.char_class.physical_damage
        self.magical_damage: Optional[float] = self.char_class.magical_damage

        if load:
            if not self._save_data.name:
                self._save_data.name = "[PH]Player"
            if save_data:
                self.load_from_save_data()
            else:
                # self.char_class = CHARACTER_CLASSES.get("starter", StarterClass)()
                self.char_class = get_character_class("starter")
                self.tick()

    def get_name(self) -> str:
        return self._save_data.name

    def load_from_save_data(self):
        # self.char_class = CHARACTER_CLASSES.get(self._save_data.char_class, StarterClass)()
        if self._save_data.char_class:
            self.char_class = get_character_class(self._save_data.char_class)
        # self.equipment = save_data.equipment
        self.tick()

    def calculate_stats(self):
        self.health.max = self.char_class.base_health + (self.xp.get_level() * self.char_class.health_per_level)
        self.health.per_min = self.char_class.health_per_min
        self.mana.max = self.char_class.base_mana + (self.xp.get_level() * self.char_class.mana_per_level)
        self.mana.per_min = self.char_class.mana_per_min
        self.attack_speed = self.char_class.attack_speed
        self.physical_damage = self.char_class.physical_damage + \
            (self.xp.get_level() * self.char_class.physical_damage_per_level)
        self.magical_damage = self.char_class.magical_damage + \
            (self.xp.get_level() * self.char_class.magical_damage_per_level)

        if self._save_data.health is None:
            self.health.set(self.health.max)
        if self._save_data.mana is None:
            self.mana.set(self.mana.max)

    def tick(self):
        if self._save_data.last_tick:
            time_now = datetime.utcnow()
            time_diff_sec = round((time_now - self._save_data.last_tick).total_seconds())
            self.xp.tick()
            self.calculate_stats()

            if self.health.get() is not self.health.max:
                self.health.adjust(self.health.per_min * time_diff_sec / 60)
            if self.mana.get() is not self.mana.max:
                self.mana.adjust(self.mana.per_min * time_diff_sec / 60)
            self._save_data.last_tick = time_now
        else:
            self._save_data.last_tick = datetime.utcnow()

    async def context_tick(self, context: commands.Context, do_tick: bool = True):
        if do_tick:
            self.tick()

        if self.xp.leveled_up:
            await context.send(text.LEVEL_UP_MESSAGE.format(self._save_data.name, self.xp.get_level()))
            self.xp.leveled_up = False


def get_display_bar(value_name: str, current_value: float, max_value: float, adjustment: int = 0,
                    suffix: str = "") -> str:
    string_value = str(round(current_value, 1))
    if max_value > 0:
        value_offset = int(10 * current_value / max_value)
    else:
        value_offset = 0
    output = f"{value_name}: {' ' * adjustment}{string_value}{' ' * (4 - len(string_value))} " \
             f"╓{'▄' * value_offset}{'─' * (10 - value_offset)}╖ {round(max_value, 1)}{suffix}"
    return output  # "Health: 24.3 ╓▄▄────────╖ 100 at 10/m"
