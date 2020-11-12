from typing import Optional


class BaseItem:
    def __init__(self, data_name: str, item_name: str):
        self._data_name: str = data_name
        self._item_name: str = item_name

    def to_dict(self) -> dict:
        return {"data_name": self.data_name, "item_name": self.item_name}

    def from_dict(self, state: dict):
        self._data_name = state.get("data_name", self.data_name)
        self._item_name = state.get("item_name", self.item_name)

    @property
    def data_name(self) -> str:
        return self._data_name

    @property
    def item_name(self) -> str:
        return self._item_name

