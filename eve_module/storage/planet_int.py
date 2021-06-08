from alento_bot import user_data_transformer, ConfigData, StorageManager
from evelib import EVEManager, SolarSystemData, PlanetData, TypeData, TypeManager, UniverseManager
from eve_module.storage.eve_config import EVEConfig
from eve_module.storage.user_auth import EVEUserAuthManager
from discord.ext import commands
from datetime import datetime
import logging
import aiohttp
import typing
from ruamel.yaml import YAML


logger = logging.getLogger("main_bot")
EVE_DATETIME_STRING = "%Y-%m-%dT%H:%M:%SZ"


class PIBadResponse(Exception):
    pass


class SchematicInfo:
    def __init__(self, schematic: dict = None):
        self.cycle_time: int = 0
        self.id: int = 0
        self.name: str = ""

        if schematic:
            self.from_schematic(schematic)

    def from_schematic(self, state: dict):
        self.cycle_time = state["cycleTime"]
        self.id = state["schematicID"]
        self.name = state["schematicName"]


class SchematicManager:
    def __init__(self, eve_config: EVEConfig):
        self.eve_config = eve_config

        self.items: typing.Dict[int, SchematicInfo] = dict()

    def load(self):
        logger.debug("Loading EVE schematics from disk...")
        schematic_file_location = f"{self.eve_config.sde_location}/bsd/planetSchematics.yaml"
        schematic_file = open(schematic_file_location, "r")
        raw_data = YAML(typ="rt").load(schematic_file)
        schematic_file.close()

        for item in raw_data:
            schematic = SchematicInfo(schematic=item)
            self.items[schematic.id] = schematic
        logger.debug("Loaded.")


class BasicPIPlanetInfo:
    def __init__(self, universe: UniverseManager, pi_info: dict = None):
        self._datetime_string = "%Y-%m-%dT%H:%M:%SZ"
        self._universe = universe
        self.last_update: datetime = datetime.utcnow()
        self.num_pins: int = 0
        self.owner_id: int = 0
        self.planet_id: int = 0
        self.planet_type: str = ""
        self.solar_system_id: int = 0
        self.upgrade_level: int = 0
        self.solar_system: SolarSystemData = SolarSystemData()
        self.planet: PlanetData = PlanetData()

        if pi_info:
            self.from_pi_info(pi_info)

    def from_pi_info(self, state: dict):
        self.last_update = datetime.strptime(state["last_update"], self._datetime_string)
        self.num_pins = state["num_pins"]
        self.owner_id = state["owner_id"]
        self.planet_id = state["planet_id"]
        self.planet_type = state["planet_type"]
        self.solar_system_id = state["solar_system_id"]
        self.upgrade_level = state["upgrade_level"]

        self.solar_system = self._universe.get_any(self.solar_system_id)
        self.planet = self.solar_system.planets[self.planet_id]


class PlanetPIInfo:
    # def __init__(self, universe: UniverseStorage, items: ItemStorage, schematics: SchematicManager,
    #              from_pi: dict = None):
    def __init__(self, eve_manager: EVEManager, schematics: SchematicManager, from_pi: dict = None):
        # self._universe = universe
        # self._items = items
        self._eve_manager = eve_manager
        self._schematics = schematics
        self.pins: list = []

        if from_pi:
            self.from_pi(from_pi)

    def from_pi(self, state: dict):
        for pin in state["pins"]:
            if "extractor_details" in pin:
                self.pins.append(ExtractorInfo(self._eve_manager.types, from_planet=pin))
            elif "schematic_id" in pin:
                self.pins.append(FactoryInfo(self._eve_manager.types, self._schematics, from_planet=pin))
            else:
                self.pins.append(BasicPinInfo(self._eve_manager.types, from_planet=pin))


class BasicPinInfo:
    def __init__(self, items: TypeManager, from_planet: dict = None):
        self._items = items
        self.pin_id: int = 0
        self.type_id: int = 0
        self.type: typing.Optional[TypeData] = None

        if from_planet:
            self.from_planet(from_planet)

    def from_planet(self, state: dict):
        self.pin_id = state["pin_id"]
        self.type_id = state["type_id"]
        self.type = self._items.get_type(self.type_id)


class FactoryInfo:
    def __init__(self, items: TypeManager, schematics: SchematicManager, from_planet: dict = None):
        self._items = items
        self._schematics = schematics
        self.contents: list = []
        self.last_cycle_start: typing.Optional[datetime] = None
        self.pin_id: int = 0
        self.schematic_id: int = 0
        self.schematic: typing.Optional[SchematicInfo] = None
        self.type_id: int = 0
        self.type: typing.Optional[TypeData] = None

        if from_planet:
            self.from_planet(from_planet)

    def from_planet(self, state: dict):
        self.contents = state["contents"]
        self.last_cycle_start = datetime.strptime(state["last_cycle_start"], EVE_DATETIME_STRING)
        self.pin_id = state["pin_id"]
        self.schematic_id = state.get("schematic_id", 0)
        self.schematic = self._schematics.items.get(self.schematic_id, None)
        self.type_id = state["type_id"]
        self.type = self._items.get_type(self.type_id)


class ExtractorInfo:
    def __init__(self, items: TypeManager, from_planet: dict = None):
        self._items = items
        self.contents: list = []
        self.expiry_time: typing.Optional[datetime] = None
        self.head_count: int = 0
        self.cycle_time: int = 0
        self.product_type_id: int = 0
        self.product_type: typing.Optional[TypeData] = None
        self.quantity_per_cycle: int = 0
        self.install_time: typing.Optional[datetime] = None
        self.last_cycle_start: typing.Optional[datetime] = None
        self.pin_id: int = 0
        self.type_id: int = 0
        self.type: typing.Optional[TypeData] = None

        if from_planet:
            self.from_planet(from_planet)

    def from_planet(self, state: dict):
        self.contents = state["contents"]
        self.expiry_time = datetime.strptime(state["expiry_time"], EVE_DATETIME_STRING)
        self.head_count = len(state["extractor_details"]["heads"])
        self.cycle_time = state["extractor_details"]["cycle_time"]
        self.product_type_id = state["extractor_details"]["product_type_id"]
        self.product_type = self._items.get_type(self.product_type_id)
        self.quantity_per_cycle = state["extractor_details"]["qty_per_cycle"]
        self.install_time = datetime.strptime(state["install_time"], EVE_DATETIME_STRING)
        self.last_cycle_start = datetime.strptime(state["last_cycle_start"], EVE_DATETIME_STRING)
        self.pin_id = state["pin_id"]
        self.type_id = state["type_id"]
        self.type = self._items.get_type(self.type_id)


class PlanetIntManager:
    # def __init__(self, storage: StorageManager, eve_config: EVEConfig, auth: EVEUserAuthManager, items: ItemStorage,
    #              universe: UniverseStorage, session: aiohttp.ClientSession):
    def __init__(self, storage: StorageManager, eve_config: EVEConfig, auth: EVEUserAuthManager,
                 eve_manager: EVEManager, session: aiohttp.ClientSession):
        self.storage = storage
        self.eve_config = eve_config
        self.auth = auth
        # self.items = items
        # self.universe = universe
        self.eve_manager = eve_manager
        # self.session = session

        self.storage.users.register_data_name("planetary_interaction_data", PlanetIntData)
        self.schematics = SchematicManager(self.eve_config)

    def load(self):
        self.schematics.load()

    async def update_pi(self, user_id: int, character_id: int, context: commands.Context):
        planet_int_data: PlanetIntData = self.storage.users.get(user_id, "planetary_interaction_data")

        bot_message = await context.send("Gathering basic PI info...")
        await self.update_pi_info(user_id, character_id)
        for basic_planet in planet_int_data.pi_info[character_id]:
            solar_system = self.eve_manager.universe.get_any(basic_planet["solar_system_id"])
            planet = solar_system.planets[basic_planet["planet_id"]]
            await bot_message.edit(content=f"Grabbing info about {solar_system.name} {planet.index}")
            await self.update_pi_planet(user_id, character_id, basic_planet["planet_id"])
        await bot_message.edit(content="PI info is fully updated.")

    async def update_pi_info(self, user_id: int, character_id: int):
        # url = f"https://esi.evetech.net/latest/characters/{character_id}/planets/"
        token = await self.auth.get_access_token(user_id, character_id)
        # response = await self.session.get(url=url, params={"token": token})
        # raw_pi_info = await response.json()
        # response.close()
        raw_pi_info = await self.eve_manager.esi.pi.get_basic_pi_raw(character_id, token)

        planet_int_data: PlanetIntData = self.storage.users.get(user_id, "planetary_interaction_data")
        planet_int_data.pi_info[character_id] = raw_pi_info

    async def update_pi_planet(self, user_id: int, character_id: int, planet_id: int) -> bool:
        # url = f"https://esi.evetech.net/latest/characters/{character_id}/planets/{planet_id}/"
        token = await self.auth.get_access_token(user_id, character_id)
        raw_data = await self.eve_manager.esi.pi.get_planet_pi_raw(character_id, planet_id, token)
        if raw_data:
            planet_int_data: PlanetIntData = self.storage.users.get(user_id, "planetary_interaction_data")
            if character_id not in planet_int_data.planet_pi:
                planet_int_data.planet_pi[character_id] = dict()

            planet_int_data.planet_pi[character_id][planet_id] = raw_data
            return True
        else:
            return False
        # response = await self.session.get(url=url, params={"token": token})
        # pi_response = await response.json()
        # response.close()
        #
        # if response.status == 200:
        #     planet_int_data: PlanetIntData = self.storage.users.get(user_id, "planetary_interaction_data")
        #     if character_id not in planet_int_data.planet_pi:
        #         planet_int_data.planet_pi[character_id] = dict()
        #
        #     planet_int_data.planet_pi[character_id][planet_id] = pi_response
        #     return True
        #
        # elif response.status == 404:
        #     return False
        # else:
        #     raise PIBadResponse(f"UPDATE_PI_PLANET: BAD RESPONSE CODE, {user_id} {character_id} {planet_id} "
        #                         f"{response.status}")

    def get_planet_pi(self, user_id: int, character_id: int, planet_id: int) -> typing.Optional[PlanetPIInfo]:
        planet_int_data: PlanetIntData = self.storage.users.get(user_id, "planetary_interaction_data")
        # return planet_int_data.planet_pi.get(character_id, dict()).get(planet_id, None)
        # return PlanetPIInfo(self.universe, self.items, self.schematics,
        #                     from_pi=planet_int_data.planet_pi.get(character_id, dict()).get(planet_id, None))
        return PlanetPIInfo(self.eve_manager, self.schematics,
                            from_pi=planet_int_data.planet_pi.get(character_id, dict()).get(planet_id, None))

    def get_pi_info(self, user_id: int, character_id: int) -> typing.Optional[typing.Dict[int, BasicPIPlanetInfo]]:
        planet_int_data: PlanetIntData = self.storage.users.get(user_id, "planetary_interaction_data")
        if character_id in planet_int_data.pi_info:
            output_dict = {}
            for basic_pi in planet_int_data.pi_info[character_id]:
                basic_planet_pi = BasicPIPlanetInfo(self.eve_manager.universe, basic_pi)
                output_dict[basic_planet_pi.planet_id] = basic_planet_pi
            return output_dict
        else:
            return None

@user_data_transformer(name="planetary_interaction_data")
# class PlanetIntData(BaseUserCache, name="planetary_interaction_data"):
class PlanetIntData:
    # def __init__(self, config: ConfigData, user_id: int):
    def __init__(self):
        # super().__init__(config, user_id)
        self.planet_pi: typing.Dict[int, typing.Dict[int, dict]] = dict()
        self.pi_info: typing.Dict[int, dict] = dict()
