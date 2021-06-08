from dnd_constants import Stats, Languages, Sizes
from typing import List, Dict


class DnDRace:
    stats: Dict[str, int] = dict()
    size: str = ""
    speed: int = 0
    languages: List[str] = list()
    traits: List[str] = list()


class Human(DnDRace):
    stats = {Stats.STR: 1, Stats.DEX: 1, Stats.CON: 1, Stats.INT: 1, Stats.WIS: 1, Stats.CHA: 1}
    size = Sizes.MEDIUM
    speed = 30
    languages = [Languages.COMMON, Languages.BLANK]


class Tiefling(DnDRace):
    stats = {Stats.INT: 1, Stats.CHA: 2}
    size = Sizes.MEDIUM
    speed = 30
    languages = [Languages.COMMON, Languages.INFERNAL]
    traits = ["Darkvision", "Hellish Resistance", "Infernal Legacy"]
