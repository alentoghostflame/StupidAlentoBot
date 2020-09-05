from alento_bot import user_data_transformer
import typing


DEFAULT_SCOPES: typing.Dict[str, bool] = {
    "publicData": False,
    "esi-planets.manage_planets.v1": False,
    "esi-wallet.read_character_wallet.v1": False,
    "esi-search.search_structures.v1": False,
    "esi-universe.read_structures.v1": False,
    "esi-markets.structure_markets.v1": False,
    "esi-industry.read_character_mining.v1": False,
    "esi-industry.read_corporation_mining.v1": False,
    "esi-industry.read_character_jobs.v1": False,
}

DEFAULT_CHARACTER_DATA: dict = {
    "refresh_token": "",
    "id": 0,
    "name": "",
    "current_scopes": DEFAULT_SCOPES,
    "desired_scopes": DEFAULT_SCOPES
}


@user_data_transformer(name="eve_auth_storage")
class EVEUserAuthStorage:
    def __init__(self):
        self.characters: typing.Dict[int, dict] = dict()
        self.active_character: int = 0






