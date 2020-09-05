from alento_bot import StorageManager
from eve_module.storage.user_auth.user_auth_data import EVEUserAuthStorage, DEFAULT_CHARACTER_DATA, DEFAULT_SCOPES
from eve_module.storage.eve_config import EVEConfig
import urllib.parse
import logging
import aiohttp
import typing
import base64
import copy


logger = logging.getLogger("main_bot")


class ESIUnauthorized(Exception):
    def __init__(self, message=""):
        self.message = message
        super().__init__(self.message)


class ESIInvalidAuthCode(Exception):
    def __init__(self, message=""):
        self.message = message
        super().__init__(self.message)


class EVEUserAuthManager:
    def __init__(self, storage: StorageManager, session: aiohttp.ClientSession):
        self.storage: StorageManager = storage
        self.eve_config: EVEConfig = self.storage.caches.get_cache("eve_config")
        self.storage.users.register_data_name("eve_auth_storage", EVEUserAuthStorage)

        self.session = session

    def create_character(self, user_id: int, character_id: int) -> dict:
        user_config: EVEUserAuthStorage = self.storage.users.get(user_id, "eve_auth_storage")
        user_config.characters[character_id] = copy.deepcopy(DEFAULT_CHARACTER_DATA)
        return user_config.characters[character_id]

    def delete_character(self, user_id: int, character_id: int) -> bool:
        user_config: EVEUserAuthStorage = self.storage.users.get(user_id, "eve_auth_storage")
        value = user_config.characters.pop(character_id, None)

        if value:
            return True
        else:
            return False

    def get_all_names(self, user_id: int) -> typing.Tuple[typing.List[int], typing.List[str]]:
        user_config: EVEUserAuthStorage = self.storage.users.get(user_id, "eve_auth_storage")
        id_list = list()
        name_list = list()
        for character_id in user_config.characters:
            id_list.append(character_id)
            name_list.append(user_config.characters[character_id].get("name", "NO NAME SET"))
        return id_list, name_list

    def get_current_scopes(self, user_id: int, character_id: int) -> typing.Optional[dict]:
        user_config: EVEUserAuthStorage = self.storage.users.get(user_id, "eve_auth_storage")
        return user_config.characters.get(character_id, dict()).get("current_scopes", None)

    def set_desired_scope(self, user_id: int, character_id: int, desired_scope: str, value: bool) -> bool:
        user_config: EVEUserAuthStorage = self.storage.users.get(user_id, "eve_auth_storage")
        self.update_scopes(user_id, character_id)
        if desired_scope in user_config.characters.get(character_id, dict()).get("desired_scopes", dict()):
            user_config.characters[character_id]["desired_scopes"][desired_scope] = value
            return True
        else:
            return False

    def update_scopes(self, user_id: int, character_id: int):
        character_scopes = self.get_current_scopes(user_id, character_id)
        desired_scopes = self.get_desired_scopes(user_id, character_id)
        for default_scope in DEFAULT_SCOPES:
            if default_scope not in character_scopes:
                character_scopes[default_scope] = DEFAULT_SCOPES.get(default_scope)
            if default_scope not in desired_scopes:
                desired_scopes[default_scope] = DEFAULT_SCOPES.get(default_scope)

    def get_desired_scopes(self, user_id: int, character_id: int) -> typing.Optional[typing.Dict[str, bool]]:
        user_config: EVEUserAuthStorage = self.storage.users.get(user_id, "eve_auth_storage")
        return user_config.characters.get(character_id, dict()).get("desired_scopes", None)

    def get_selected_desired_scopes(self, user_id: int) -> typing.Optional[typing.Dict[str, bool]]:
        user_config: EVEUserAuthStorage = self.storage.users.get(user_id, "eve_auth_storage")
        return self.get_desired_scopes(user_id, user_config.active_character)

    def set_selected_desired_scope(self, user_id: int, desired_scope: str, value: bool) -> bool:
        user_config: EVEUserAuthStorage = self.storage.users.get(user_id, "eve_auth_storage")
        self.update_scopes(user_id, user_config.active_character)
        return self.set_desired_scope(user_id, user_config.active_character, desired_scope, value)

    def get_selected_scopes(self, user_id: int) -> typing.Optional[dict]:
        user_config: EVEUserAuthStorage = self.storage.users.get(user_id, "eve_auth_storage")
        return user_config.characters.get(self.get_selected(user_id), dict()).get("current_scopes", None)

    def get_name(self, user_id: int, character_id: int) -> typing.Optional[str]:
        user_config: EVEUserAuthStorage = self.storage.users.get(user_id, "eve_auth_storage")
        return user_config.characters.get(character_id, dict()).get("name", None)

    def set_selected(self, user_id: int, character_id: int):
        user_config: EVEUserAuthStorage = self.storage.users.get(user_id, "eve_auth_storage")
        if character_id in user_config.characters or character_id == 0:
            user_config.active_character = character_id
        else:
            logger.warning(f"Tried to set active character id {character_id} to nonexistent character for user "
                           f"{user_id}")

    def get_selected(self, user_id: int) -> int:
        user_config: EVEUserAuthStorage = self.storage.users.get(user_id, "eve_auth_storage")
        return user_config.active_character

    def get_basic_eve_auth_url(self) -> str:
        base_url = "https://login.eveonline.com/oauth/authorize/?response_type=code&redirect_uri={}&client_id={}" \
                   "&scope={}&state={}"
        redirect_uri = urllib.parse.quote_plus(self.eve_config.callback_url)
        client_id = urllib.parse.quote_plus(self.eve_config.client_id)
        scope = urllib.parse.quote_plus("publicData")
        state = urllib.parse.quote_plus(self.eve_config.unique_state)

        return base_url.format(redirect_uri, client_id, scope, state)

    def get_desired_eve_auth_url(self, user_id: int, character_id: int) -> typing.Optional[str]:
        desired_scopes = self.get_desired_scopes(user_id, character_id)
        if desired_scopes:
            base_url = "https://login.eveonline.com/oauth/authorize/?response_type=code&redirect_uri={}&client_id={}" \
                       "&scope={}&state={}"
            redirect_uri = urllib.parse.quote_plus(self.eve_config.callback_url)
            client_id = urllib.parse.quote_plus(self.eve_config.client_id)
            scope_list = []

            for scope in desired_scopes:
                if desired_scopes[scope]:
                    scope_list.append(scope)
            scope_string = urllib.parse.quote_plus(" ".join(scope_list))
            state = urllib.parse.quote_plus(self.eve_config.unique_state)

            return base_url.format(redirect_uri, client_id, scope_string, state)
        else:
            return None

    async def get_access_token(self, user_id: int, character_id: int, refresh_token: str = "") -> typing.Optional[str]:
        user_config: EVEUserAuthStorage = self.storage.users.get(user_id, "eve_auth_storage")
        token = ""

        if refresh_token:
            token = refresh_token
        elif user_config.characters.get(character_id, dict()).get("refresh_token", None):
            token = user_config.characters[character_id]["refresh_token"]

        if token:
            auth_key = base64.b64encode(bytes("{}:{}".format(self.eve_config.client_id,
                                                             self.eve_config.secret_key), "utf-8")).decode("utf-8")

            headers = {"Authorization": "Basic {}".format(auth_key),
                       "Content-Type": "application/x-www-form-urlencoded", "Host": "login.eveonline.com"}
            data_bits = {"grant_type": "refresh_token", "refresh_token": token}
            response = await self.session.post(url="https://login.eveonline.com/oauth/token", headers=headers,
                                               data=data_bits)
            access_token = await response.json()
            response.close()
            return access_token.get("access_token", None)
        else:
            return None

    async def _get_refresh_token(self, auth_code: str) -> typing.Optional[str]:
        auth_key = base64.b64encode(bytes("{}:{}".format(self.eve_config.client_id,
                                                         self.eve_config.secret_key), "utf-8")).decode("utf-8")
        headers = {"Authorization": f"Basic {auth_key}", "Content-Type": "application/x-www-form-urlencoded",
                   "Host": "login.eveonline.com"}
        data_bits = {"grant_type": "authorization_code", "code": auth_code}
        response = await self.session.post(url="https://login.eveonline.com/oauth/token", headers=headers, data=data_bits)
        raw_response = await response.json()
        return raw_response.get("refresh_token", None)

    async def register_refresh_token(self, user_id: int, auth_code: str) -> typing.Optional[str]:
        refresh_token = await self._get_refresh_token(auth_code)
        if not refresh_token:
            raise ESIInvalidAuthCode
        access_token = await self.get_access_token(user_id, 0, refresh_token=refresh_token)
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await self.session.get(url="https://login.eveonline.com/oauth/verify", headers=headers)
        if response.status == 200:
            raw_data: dict = await response.json()
            if raw_data.get("CharacterID", None):
                character_config = self.create_character(user_id, raw_data["CharacterID"])
                character_config["refresh_token"] = refresh_token
                character_config["id"] = raw_data["CharacterID"]
                character_config["name"] = raw_data["CharacterName"]
                current_scopes = scope_string_to_dict(raw_data["Scopes"])
                character_config["current_scopes"] = copy.deepcopy(current_scopes)
                character_config["desired_scopes"] = copy.deepcopy(current_scopes)

                return character_config["name"]
            else:
                return None
        else:
            return None


def scope_string_to_dict(scope_string: str) -> typing.Dict[str, bool]:
    scope_list = scope_string.split(" ")
    output_scopes = copy.deepcopy(DEFAULT_SCOPES)
    for scope in output_scopes:
        if scope in scope_list:
            output_scopes[scope] = True
    return output_scopes
