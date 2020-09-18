from alento_bot import user_data_transformer
from mmo_module.mmo_data.char_class_data import BaseCharClass, StarterClass, CHARACTER_CLASSES
from mmo_module.mmo_data.equipment_data import BaseEquipment
from mmo_module.mmo_data.small_data import BaseResists
from typing import Optional, Dict
import logging


logger = logging.getLogger("main_bot")


@user_data_transformer(name="mmo_char_save")
class CharacterSaveData:
    def __init__(self):
        self.char_class: Optional[str] = None
        self.health: Optional[float] = None
        self.mana: Optional[float] = None
        self.equipment: Dict[dict] = dict()


class DefaultSaveData:
    def __init__(self):
        self.char_class: Optional[str] = None
        self.health: Optional[float] = None
        self.mana: Optional[float] = None
        self.equipment: Dict[dict] = dict()


class BaseCharacter:
    def __init__(self, save_data: CharacterSaveData = None, load: bool = True):
        if save_data:
            self._save_data: CharacterSaveData = save_data
        else:
            self._save_data = DefaultSaveData()

        self.base_max_health: float = 100
        self.base_health_per_min: float = 10
        self.base_max_mana: float = 20
        self.base_mana_per_min: float = 2
        self.base_physical_attack: float = 10
        self.base_magical_attack: float = 10

        self.equipment: dict = dict()
        self.char_class: Optional[BaseCharClass] = None

        self.resists: BaseResists = BaseResists()
        self.max_health: Optional[float] = None
        self.health_per_min: Optional[float] = None
        self.max_mana: Optional[float] = None
        self.mana_per_min: Optional[float] = None
        self.physical_attack: Optional[float] = None
        self.magical_attack: Optional[float] = None

        if load:
            if save_data:
                self.load_from_save_data()
            else:
                self.char_class = CHARACTER_CLASSES.get("Starter")
                self.calculate_stats()

    def load_from_save_data(self):
        self.char_class = CHARACTER_CLASSES.get(self._save_data.char_class, StarterClass)()
        # self.equipment = save_data.equipment
        self.calculate_stats()

    def calculate_stats(self):
        self.max_health = self.base_max_health
        self.max_mana = self.base_max_mana
        self.health_per_min = self.base_health_per_min
        self.mana_per_min = self.base_mana_per_min
        self.physical_attack = self.base_physical_attack
        self.magical_attack = self.base_magical_attack

        if not self._save_data.health:
            self._save_data.health = self.max_health
        if not self._save_data.mana:
            self._save_data.mana = self.max_mana

    def set_health(self, amount: float):
        self._save_data.health = amount

    def modify_health(self, amount: float):
        self._save_data.health += amount
        if self._save_data.health < 0:
            self._save_data.health = 0

    def get_health(self) -> float:
        return self._save_data.health

    def set_mana(self, amount: float):
        self._save_data.mana = amount

    def modify_mana(self, amount: float):
        self._save_data.mana += amount

    def get_mana(self) -> float:
        return self._save_data.mana
