from alento_bot import user_data_transformer, DictConfig
from typing import Optional, Dict, List, Tuple


@user_data_transformer(name="dnd_data")
class DndUserData:
    def __init__(self):
        self.chars: Dict[str, DnDCharData] = dict()
        self.selected_char: Optional[str] = None

    def pre_save(self):
        char_dict = dict()
        for char_name in self.chars:
            char_dict[char_name] = self.chars[char_name].to_dict()
        self.chars = char_dict

    def post_save(self):
        char_dict = dict()
        for char_name in self.chars:
            # char_dict[char_name] = DnDCharData(self.chars[char_name].to_dict())
            char_dict[char_name] = DnDCharData(dict(self.chars[char_name]))
        self.chars = char_dict

    def post_load(self):
        self.post_save()

    def create_character(self, name: str):
        self.chars[name.lower()] = DnDCharData()
        self.chars[name.lower()].name = name


class PVDictConfig(DictConfig):
    def from_dict(self, state: dict):
        for key in state:
            if key in self.__dict__:
                if isinstance(state[key], dict) and "value" in state[key] and "proficient" in state[key]:
                    self.__dict__[key].from_dict(state[key])
                else:
                    self.__dict__[key] = state[key]

    def to_dict(self) -> dict:
        output_dict = dict()
        for key in self.__dict__:
            if not key.startswith("_") or key.startswith("_c_"):
                if isinstance(self.__dict__[key], ProfValue):
                    output_dict[key] = self.__dict__[key].to_dict()
                else:
                    output_dict[key] = self.__dict__[key]
        return output_dict


class ProfValue(DictConfig):
    def __init__(self, state: dict = None):
        self.proficient: bool = False
        self.value: int = 0
        if state:
            self.from_dict(state)


class DnDItem(DictConfig):
    def __init__(self, state: Dict):
        self.name = ""
        self.quantity = 0
        self.weight = 0.0
        if state:
            self.from_dict(state)

    @classmethod
    def make(cls, name: str, quantity: int, weight: float):
        return cls({"name": name, "quantity": quantity, "weight": weight})

    @property
    def total_weight(self) -> float:
        return self.weight * self.quantity


class DnDCharData(DictConfig):
    def __init__(self, state: dict = None):
        self.name = "None"
        self.basic = DnDBasicData()
        self.inv = DnDInventory()
        self.stats = DnDCharStats()
        if state:
            self.from_dict(state)

    def from_dict(self, state: dict):
        self.name = state.get("name", "None")
        self.basic.from_dict(state.get("basic", dict()))
        self.inv.from_dict(state.get("inv", dict()))
        self.stats.from_dict(state.get("stats", dict()))

    def to_dict(self) -> dict:
        return {"name": self.name, "basic": self.basic.to_dict(), "inv": self.inv.to_dict(),
                "stats": self.stats.to_dict()}


class DnDBasicData(DictConfig):
    def __init__(self):
        self.level = 0
        self.xp = 0
        self.race = "None"
        self.char_class = "None"
        self.background = "None"
        self.alignment = "None"

    def text(self) -> str:
        ret = f"Background: {self.background}, Race: {self.race}, Alignment: {self.alignment}\n"
        ret += f"Class: {self.char_class}, LVL: {self.level}, XP: {self.xp}"
        return ret


class DnDInventory(DictConfig):
    def __init__(self):
        self.money = DnDCurrency()
        self.items: List[DnDItem] = list()

    def swap_item_int(self, index1: int, index2: int) -> Tuple[Optional[DnDItem], Optional[DnDItem]]:
        """
        Swaps the items at the two given indexes for sorting purposes.

        :param index1: Index of the first item to swap, starting at 0.
        :param index2: Index of the second item to swap, starting at 0.
        :return: DnDItem's swapped if successfully swapped items, None otherwise.
        """
        if index1 != index2 and index1 != (-index2 + 1) and index2 != (-index1 + 1) and \
                -len(self.items) <= index1 < len(self.items) and -len(self.items) <= index2 < len(self.items):
            self.items[index1], self.items[index2] = self.items[index2], self.items[index1]
            return self.items[index1], self.items[index2]
        else:
            return None, None

    def swap_item_str(self, name1: str, name2: str) -> Tuple[Optional[DnDItem], Optional[DnDItem]]:
        """
        Swaps the items with the 2 given names for sorting purposes.

        :param name1: Case insensitive name of the first item to swap.
        :param name2: Case insensitive name of the second item to swap.
        :return: DnDItem's swapped if successfully swapped items, None otherwise.
        """
        if name1.lower() != name2.lower() and (index1 := self.find_index(name1)) and (index2 := self.find_index(name2)):
            return self.swap_item_int(index1, index2)
        else:
            return None, None

    def add_item_int(self, index: int, quantity: int) -> Optional[DnDItem]:
        """
        Adds a quantity to an existing item.

        :param index: Index of the item in the list, starting at 0.
        :param quantity: Quantity to add.
        :return: DnDItem at the given index if in bounds, None otherwise.
        """
        if -len(self.items) <= index < len(self.items):
            self.items[index].quantity += quantity
            return self.items[index]
        else:
            return None

    def add_item_str(self, name: str, quantity: int, weight: float) -> DnDItem:
        """
        Add an item with a name and quantity to the characters inventory. Auto-stacks with existing items.

        :param name: Name of item. Case insensitive when stacking with other items.
        :param quantity: Amount of the item to add.
        :param weight: Weight of a single quantity of the item.
        :return: DnDItem item with the given name.
        """
        if item := self.find_item(name):
            item.quantity += quantity
        else:
            item = DnDItem.make(name, quantity, weight)
            self.items.append(item)
        return item

    def edit_name_item_int(self, index: int, new_name: str) -> bool:
        """
        Rename the item at the given index to the new name.

        :param index: Index of the item in the list, starting at 0.
        :param new_name: New name to replace the old name.
        :return: True if item found and renamed, False if not found.
        """
        # if index < len(self.items):
        if -len(self.items) <= index < len(self.items):
            self.items[index].name = new_name
            return True
        else:
            return False

    def edit_name_item_str(self, old_name: str, new_name: str) -> bool:
        """
        Rename the given old name to the new name. Case insensitive on the old name.

        :param old_name: Case insensitive name to find.
        :param new_name: New name to replace the old name.
        :return: True if name found and renamed, False if not found.
        """
        if item := self.find_item(old_name):
            item.name = new_name
            return True
        else:
            return False

    def edit_weight_item_int(self, index: int, weight: float) -> bool:
        """
        Sets the weight of the item at the given index to the given weight.

        :param index: Index of the item in the list, starting at 0.
        :param weight: New weight of the item.
        :return: True if the item found and reweighed, False if not found.
        """
        # if index < len(self.items):
        if -len(self.items) <= index < len(self.items):
            self.items[index].weight = weight
            return True
        else:
            return False

    def edit_weight_item_str(self, name: str, weight: float) -> bool:
        """
        Sets the weight of the given item to the given weight.

        :param name: Case insensitive item name to edit.
        :param weight: New weight of the item.
        :return: True if the item found and reweighed, False if not found.
        """
        if item := self.find_item(name):
            item.weight = weight
            return True
        else:
            return False

    def rm_item_int(self, index: int, quantity: int) -> Tuple[Optional[DnDItem], int]:
        """
        Removes the given quantity from the item at the given index. Removing all (or more) of the item will remove the
        item from the inventory.

        :param index: Index of the item in the list, starting at 0.
        :param quantity: Quantity to remove from the item.
        :return: DnDItem if index in range, None otherwise, AND amount of items removed.
        """
        # if index < len(self.items):
        if -len(self.items) <= index < len(self.items):
            item = self.items[index]
            orig_quantity = item.quantity
            item.quantity = max(0, item.quantity - quantity)
            if item.quantity == 0:
                self.items.pop(index)
            return item, min(orig_quantity, quantity)
        else:
            return None, 0

    def rm_item_str(self, name: str, quantity: int) -> Tuple[Optional[DnDItem], int]:
        """
        Removes the given quantity of items from the given item. Removing all (or more) of the item will remove the item
        from the inventory.

        :param name: Case insensitive item to remove.
        :param quantity: Quantity to remove.
        :return: DnDItem if index in found, None otherwise, AND amount of items removed.
        """
        if item := self.find_item(name):
            orig_quantity = item.quantity
            item.quantity = max(0, item.quantity - quantity)
            if item.quantity == 0:
                self.items.remove(item)
            return item, min(orig_quantity, quantity)
        else:
            return None, 0

    def del_item_int(self, index: int) -> Optional[DnDItem]:
        """
        Removes the item at the given index from the list.

        :param index: Index of the item in the list, starting at 0.
        :return: True if item removed, False if not found.
        """
        if -len(self.items) <= index < len(self.items):
            return self.items.pop(index)
        else:
            return None

    def del_item_str(self, name: str) -> Optional[DnDItem]:
        """
        Removes the item that has the given name.

        :param name: Case insensitive item to remove.
        :return: True if item removed, false if not found.
        """
        if item := self.find_item(name):
            self.items.remove(item)
            return item
        else:
            return None

    def from_dict(self, state: dict):
        self.money.from_dict(state.get("money", dict()))
        for item in state.get("items", list()):
            self.items.append(DnDItem(item))

    def to_dict(self) -> dict:
        ret = dict()
        ret["money"] = self.money.to_dict()
        ret["items"] = [item.to_dict() for item in self.items]
        return ret

    def item_text(self) -> str:
        if self.items:
            ret = "\n".join(f"{i}: {self.items[i].quantity} x {self.items[i].name} - {self.items[i].weight * self.items[i].quantity}" for i in range(len(self.items)))
            return f"{ret}\nTotal Weight: {self.get_weight()}"
        else:
            return "No items.\nTotal Weight: 0.0"

    def text(self) -> str:
        ret = f"{self.money.text()}\n"
        ret += f"`{'═' * (len(ret.strip()) - 16)}`\n"
        ret += self.item_text()
        return ret

    def find_item(self, name: str) -> Optional[DnDItem]:
        """
        Quickly find an item in the inventory with the given case insensitive name.

        :param name: Case insensitive item name to find.
        :return: DnDItem if the item name was found, None if not.
        """
        for item in self.items:
            if name.lower() == item.name.lower():
                return item
        return None

    def find_index(self, name: str) -> Optional[int]:
        """
        Quickly find the index of an item in the inventory with the given case insensitive name.

        :param name: Case insensitive item name to find.
        :return: Index of the item if found, None otherwise.
        """
        for i in range(len(self.items)):
            if name.lower() == self.items[i].name.lower():
                return i
        return None

    def get_weight(self) -> float:
        ret = 0.0
        for item in self.items:
            ret += item.weight * item.quantity
        return ret


class DnDCurrency(DictConfig):
    def __init__(self):
        self.cp = 0
        self.sp = 0
        self.ep = 0
        self.gp = 0
        self.pp = 0

    def text(self) -> str:
        return f"CP: `{self.cp}`, SP: `{self.sp}`, EP: `{self.ep}`, GP: `{self.gp}`, PP: `{self.pp}`"


# class DnDCharData(DictConfig):
#     def __init__(self, state: dict = None):
#         self.core: DnDCharCore = DnDCharCore()
#         self.stats: DnDStats = DnDStats()
#         if dict:
#             self.from_dict(state)
#
#     def from_dict(self, state: dict):
#         self.core.from_dict(state.get("details", None))
#         self.stats.from_dict(state.get("stats", None))
#
#     def to_dict(self) -> dict:
#         return {"core": self.core.to_dict(), "stats": self.stats.to_dict()}
#
#
# class DnDCharCore(DictConfig):
#     def __init__(self, state: dict = None):
#         self.char_class: Optional[str] = None
#         self.background: Optional[str] = None
#         self.name: Optional[str] = None
#         self.race: Optional[str] = None
#         self.alignment: Optional[str] = None
#         self.experience: Optional[int] = None
#         if state:
#             self.from_dict(state)
#
#
# class DnDCharDetails(DictConfig):
#     def __init__(self, state: dict = None):
#         self.personality: Optional[str] = None
#         self.ideals: Optional[str] = None
#         self.bonds: Optional[str] = None
#         self.flaws: Optional[str] = None
#         self.features_traits: Optional[str] = None
#         if state:
#             self.from_dict(state)
#
#
# class DnDCharInventory(DictConfig):
#     def __init__(self, state: dict = None):
#         self.equipment: List[str] = list()
#         if state:
#             self.from_dict(state)
#
#
# class DnDCharSkills(PVDictConfig):
#     def __init__(self, state: dict = None):
#         self.acrobatics: ProfValue = ProfValue()
#         self.animal_handling: ProfValue = ProfValue()
#         self.arcana: ProfValue = ProfValue()
#         self.athletics: ProfValue = ProfValue()
#         self.deception: ProfValue = ProfValue()
#         self.history: ProfValue = ProfValue()
#         self.insight: ProfValue = ProfValue()
#         self.intimidation: ProfValue = ProfValue()
#         self.investigation: ProfValue = ProfValue()
#         self.medicine: ProfValue = ProfValue()
#         self.nature: ProfValue = ProfValue()
#         self.perception: ProfValue = ProfValue()
#         self.performance: ProfValue = ProfValue()
#         self.persuasion: ProfValue = ProfValue()
#         self.religion: ProfValue = ProfValue()
#         self.sleight_of_hand: ProfValue = ProfValue()
#         self.stealth: ProfValue = ProfValue()
#         self.survival: ProfValue = ProfValue()
#         if state:
#             self.from_dict(state)
#
#
# class DnDCharSavingThrows(PVDictConfig):
#     def __init__(self, state: dict = None):
#         self.str: ProfValue = ProfValue()
#         self.dex: ProfValue = ProfValue()
#         self.con: ProfValue = ProfValue()
#         self.int: ProfValue = ProfValue()
#         self.wis: ProfValue = ProfValue()
#         self.cha: ProfValue = ProfValue()
#         if state:
#             self.from_dict(state)
#
#
class DnDCharStats(DictConfig):
    def __init__(self, state: dict = None):
        self.str: int = 0
        self.dex: int = 0
        self.con: int = 0
        self.int: int = 0
        self.wis: int = 0
        self.cha: int = 0
        if state:
            self.from_dict(state)

    def text(self) -> str:
        return f"Str: `{self.str}`\nDex: `{self.dex}`\nCon: `{self.con}`\nInt: `{self.int}`\nWis: `{self.wis}`\n" \
               f"Cha: `{self.cha}`"
