from alento_bot import user_data_transformer
from mmo_module.mmo_core import get_display_bar
from typing import Optional, Dict
from datetime import datetime
import logging


BASE_HEALTH = 10
BASE_MANA = 10
BASE_PHYSICAL_ATTACK = 2.5
BASE_MAGICAL_ATTACK = 2.5
BASE_HEALTH_REGEN = 5
BASE_MANA_REGEN = 5
NAME_LENGTH_LIMIT = 32
BASE_SPEED = 1.0


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
        self.default_spell: Optional[str] = None


@user_data_transformer(name="mmo_char_save")
class CharacterSaveData(DefaultSaveData):
    def __init__(self):
        DefaultSaveData.__init__(self)


class ResistanceStats:
    def __init__(self):
        self.phys_flat: float = 0
        self.phys_amp: float = 1.0
        self.magi_flat: float = 0
        self.magi_amp: float = 1.0


class HealthHandler:
    def __init__(self, save_data: DefaultSaveData):
        self._save_data = save_data
        self.max: Optional[float] = None
        self.per_min: Optional[float] = None

    @property
    def current(self) -> float:
        return self._save_data.health

    @current.setter
    def current(self, amount: float):
        self._save_data.health = amount
        if self.current > self.max:
            self._save_data.health = self.max
        elif self.current < 0:
            self._save_data.health = 0

    def get_display(self, adjustment: int = 0, regen: bool = False) -> str:
        if regen:
            return get_display_bar("Health", self.current, self.max, adjustment, f", at {round(self.per_min, 1)}/m")
        else:
            return get_display_bar("Health", self.current, self.max, adjustment)


class ManaHandler:
    def __init__(self, save_data: DefaultSaveData):
        self._save_data = save_data
        self.max: Optional[float] = None
        self.per_min: Optional[float] = None

    @property
    def current(self) -> float:
        return self._save_data.mana

    @current.setter
    def current(self, amount: float):
        self._save_data.mana = amount
        if self.current > self.max:
            self._save_data.mana = self.max
        elif self.current < 0:
            self._save_data.mana = 0

    def get_display(self, adjustment: int = 0, regen: bool = False) -> str:
        if regen:
            return get_display_bar("Mana", self.current, self.max, adjustment, f", at {round(self.per_min, 1)}/m")
        else:
            return get_display_bar("Mana", self.current, self.max, adjustment)


class ExperienceHandler:
    def __init__(self, save_data: DefaultSaveData):
        self._save_data = save_data
        self._xp_to_next_level: Optional[int] = None
        self.leveled_up: bool = False

    @property
    def level(self) -> int:
        return self._save_data.level

    @property
    def xp_to_next_level(self) -> int:
        self._xp_to_next_level = 100 + 20 * self._save_data.level
        return self._xp_to_next_level

    @property
    def current(self) -> int:
        return self._save_data.xp

    @current.setter
    def current(self, amount: int):
        self._save_data.xp = amount

    @property
    def worth(self) -> int:
        return 50 + 10 * self.level

    def _level_up(self):
        if self._save_data.xp >= self.xp_to_next_level:
            self._save_data.xp -= self.xp_to_next_level
            self._save_data.level += 1
            self.leveled_up = True

    def tick(self):
        while self.current >= self.xp_to_next_level:
            self._level_up()

    def get_display(self, adjustment: int = 0):
        return get_display_bar("XP", self.current, self.xp_to_next_level, adjustment, f", LV {self._save_data.level}")


class AttackStats:
    def __init__(self):
        self.speed: Optional[float] = None
        self.physical: Optional[float] = None
        self.magical: Optional[float] = None


class BaseCharStats:
    def __init__(self, save_data: DefaultSaveData):
        self._save_data = save_data
        self.hp: HealthHandler = HealthHandler(save_data)
        self.mp: ManaHandler = ManaHandler(save_data)
        self.xp: ExperienceHandler = ExperienceHandler(save_data)
        self.resists: ResistanceStats = ResistanceStats()
        self.attack: AttackStats = AttackStats()

    def calculate_stats(self):
        self.calculate_health()
        self.calculate_mana()
        self.calculate_speed()
        self.calculate_phys_dmg()
        self.calculate_magi_dmg()

    def calculate_health(self):
        self.hp.max = BASE_HEALTH * (self.xp.level + 1)
        self.hp.per_min = BASE_HEALTH_REGEN
        if not self.hp.current or self.hp.current > self.hp.max:
            self.hp.current = self.hp.max

    def calculate_mana(self):
        self.mp.max = BASE_MANA * (self.xp.level + 1)
        self.mp.per_min = BASE_MANA_REGEN
        if not self.mp.current or self.mp.current > self.mp.max:
            self.mp.current = self.mp.max

    def calculate_speed(self):
        self.attack.speed = BASE_SPEED

    def calculate_phys_dmg(self):
        self.attack.physical = BASE_PHYSICAL_ATTACK * (self.xp.level + 1)

    def calculate_magi_dmg(self):
        self.attack.magical = BASE_MAGICAL_ATTACK * (self.xp.level + 1)

    def tick(self, finish_tick: bool = True):
        self.calculate_stats()
        if self._save_data.last_tick:
            time_now = datetime.utcnow()
            time_diff_sec = round((time_now - self._save_data.last_tick).total_seconds())
            self.xp.tick()
            self.calculate_stats()

            if self.hp.current is not self.hp.max:
                self.hp.current += self.hp.per_min * time_diff_sec / 60
            if self.mp.current is not self.mp.max:
                self.mp.current += self.mp.per_min * time_diff_sec / 60
            if finish_tick:
                self._save_data.last_tick = time_now
        else:
            self._save_data.last_tick = datetime.utcnow()

    def deal_damage(self, amount: float, offset_amp: float = 1.0, offset_flat: float = 0, physical: bool = False,
                    magical: bool = False) -> float:
        damage_amount = amount
        if physical:
            damage_amount = damage_amount * self.resists.phys_amp - self.resists.phys_flat
        if magical:
            damage_amount = damage_amount * self.resists.magi_amp - self.resists.magi_flat

        damage_amount = damage_amount * offset_amp - offset_flat
        if damage_amount < 0:
            damage_amount = 0
        self.hp.current -= damage_amount
        return damage_amount

    def get_damage(self) -> float:
        return self.attack.physical
