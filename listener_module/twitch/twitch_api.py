from typing import Optional, Iterable, List, Dict, Union
from datetime import datetime, timedelta
from aiohttp import ClientSession
import logging

TOKEN_URL = "https://id.twitch.tv/oauth2/token"
HELIX_STREAMS_URL = "https://api.twitch.tv/helix/streams"
HELIX_USERS_URL = "https://api.twitch.tv/helix/users"
HELIX_CHANNELS_URL = "https://api.twitch.tv/helix/channels"


logger = logging.getLogger("main_bot")


class TwitchInvalidClientID(Exception):
    pass


class TwitchInvalidClientSecret(Exception):
    pass


class TwitchInvalidClientOther(Exception):
    pass


class TwitchStreamData:
    def __init__(self, data: dict):
        self.game_id: str = data["game_id"]
        self.game_name: str = data["game_name"]
        self.id: int = int(data["id"])
        self.language: str = data["language"]
        self.tag_ids: str = data["tag_ids"]
        self.thumbnail_url: str = data["thumbnail_url"]
        self.title: str = data["title"]
        self.type: str = data["type"]
        self.user_id: int = int(data["user_id"])
        self.user_login: str = data["user_login"]
        self.viewer_count: int = data["viewer_count"]
        self.started_at: datetime = datetime.strptime(data["started_at"], "%Y-%m-%dT%H:%M:%SZ")
        self.raw: dict = data


class TwitchUserData:
    def __init__(self, data: dict):
        self.broadcaster_type: str = data["broadcaster_type"]
        self.description: str = data["description"]
        self.display_name: str = data["display_name"]
        self.id: int = int(data["id"])
        self.login: str = data["login"]
        self.offline_image_url: str = data["offline_image_url"]
        self.profile_image_url: str = data["profile_image_url"]
        self.type: str = data["type"]
        self.view_count: int = data["view_count"]
        self.created_at: str = data["created_at"]
        self.raw: dict = data


class TwitchChannelData:
    def __init__(self, data: dict):
        self.broadcaster_id: int = int(data["broadcaster_id"])
        self.broadcaster_name: str = data["broadcaster_name"]
        self.game_name: str = data["game_name"]
        self.game_id: int = int(data["game_id"])
        self.broadcaster_language: str = data["broadcaster_language"]
        self.title: str = data["title"]


class AppAccessToken:
    def __init__(self, expiration: datetime, token: str):
        self.expiration: datetime = expiration
        self.token: str = token

    def __str__(self):
        return self.token


class TwitchAPI:
    def __init__(self, session: ClientSession, client_id: str, client_secret: str):
        self._session = session
        self._id: str = client_id
        self._secret: str = client_secret
        self._app_token: Optional[AppAccessToken] = None
        self._streamer_name_to_id: Dict[str, int] = dict()
        self._streamer_display_name_cache: Dict[int, str] = dict()
        self._user_data_cache: Dict[int, TwitchUserData] = dict()
        self._channel_cache: Dict[int, Optional[TwitchChannelData]] = dict()

    async def _fetch_app_token(self) -> AppAccessToken:
        # logger.debug(f"Client: {self._id}, SECRET {self._secret}")
        response = await self._session.post(TOKEN_URL, params={"client_id": self._id, "client_secret": self._secret,
                                                               "grant_type": "client_credentials"})
        response_json = await response.json()
        # logger.debug(response_json)
        if status := response_json.get("status", None):
            if status == 400:
                raise TwitchInvalidClientID("Invalid Client ID, is the twitch config properly setup?")
            elif status == 403:
                raise TwitchInvalidClientSecret("Invalid Client Secret, is the twitch config properly setup?")
            else:
                raise TwitchInvalidClientOther(f"Invalid Client something, status {status}, FIXME.")
        else:
            app_token = AppAccessToken(datetime.utcnow() + timedelta(seconds=response_json["expires_in"]),
                                       response_json["access_token"])
            return app_token

    async def get_app_token(self) -> AppAccessToken:
        if self._app_token is None or self._app_token.expiration < datetime.utcnow():
            # logger.debug("Getting new app token.")
            self._app_token = await self._fetch_app_token()
        return self._app_token

    async def get_stream_data(self, streamer_ids: List[int]) -> List[TwitchStreamData]:
        if len(streamer_ids) <= 100:
            url = HELIX_STREAMS_URL
            headers = {"Authorization": f"Bearer {await self.get_app_token()}", "Client-Id": self._id}
            params = [("user_id", user_id) for user_id in streamer_ids]
            response = await self._session.get(url, params=params, headers=headers)
            response_json = await response.json()
            # logger.debug(response_json)
            ret = [TwitchStreamData(raw_data) for raw_data in response_json["data"]]
            return ret
        else:
            raise IndexError("Maximum of 100 streamer IDs.")

    async def _fetch_user_data(self, names: List[str], ids: List[int]) -> List[TwitchUserData]:
        if len(names) + len(ids) <= 100:
            url = HELIX_USERS_URL
            headers = {"Authorization": f"Bearer {await self.get_app_token()}", "Client-Id": self._id}
            # params = dict()
            params = []
            if names:
                # params["login"] = names
                params.extend([("login", user_name) for user_name in names])
            if ids:
                # params["id"] = ids
                params.extend([("id", user_id) for user_id in ids])
            if params:
                response = await self._session.get(url, params=params, headers=headers)
                response_json = await response.json()
                # logger.debug(response_json)
                # logger.debug(response.url)
                ret = [TwitchUserData(raw_data) for raw_data in response_json["data"]]
                return ret
            else:
                raise TypeError("No valid inputs given!")
        else:
            raise IndexError("Maximum of 100 streamer names/IDs.")

    def _apply_user_data(self, data: TwitchUserData):
        self._user_data_cache[data.id] = data
        self._streamer_name_to_id[data.display_name.lower()] = data.id

    def _apply_channel_data(self, data: TwitchChannelData):
        self._channel_cache[data.broadcaster_id] = data

    async def get_user_data(self, streamer: Union[int, str], use_cache: bool = True) -> Optional[TwitchUserData]:
        if isinstance(streamer, int):
            if use_cache and streamer in self._user_data_cache:
                return self._user_data_cache[streamer]
            else:
                # f ret := await self._fetch_user_data_by_id([streamer]):
                if ret := await self._fetch_user_data([], [streamer]):
                    # self._user_data_cache[ret[0].id] = ret[0]
                    # self._streamer_name_to_id[ret[0].display_name.lower()] = ret[0].id
                    self._apply_user_data(ret[0])
                    return ret[0]
                else:
                    return None
        else:
            if use_cache and streamer.lower() in self._streamer_name_to_id and streamer in self._user_data_cache:
                return self._user_data_cache[self._streamer_name_to_id[streamer.lower()]]
            else:
                # if ret := await self._fetch_user_data_by_name([streamer]):
                if ret := await self._fetch_user_data([streamer], []):
                    # self._user_data_cache[ret[0].id] = ret[0]
                    # self._streamer_name_to_id[ret[0].display_name.lower()] = ret[0].id
                    self._apply_user_data(ret[0])
                    return ret[0]
                else:
                    return None

    async def get_bulk_user_data(self, names: List[str], ids: List[int], use_cache: bool = True) -> List[TwitchUserData]:
        if use_cache:
            ret = list()
            names_to_grab = names.copy()
            ids_to_grab = ids.copy()
            for user_name in names:
                if (name_id := self._streamer_name_to_id.get(user_name.lower(), None)) and \
                        name_id in self._user_data_cache:
                    ret.append(self._user_data_cache[name_id])
                    names_to_grab.remove(user_name)
            for user_id in ids:
                if user_data := self._user_data_cache.get(user_id, None):
                    ret.append(user_data)
                    ids_to_grab.remove(user_id)
            if names_to_grab or ids_to_grab:
                new_data = await self._fetch_user_data(names_to_grab, ids_to_grab)
                for user_data in new_data:
                    self._apply_user_data(user_data)
                ret.extend(new_data)
                return ret
        else:
            ret = await self._fetch_user_data(names, ids)
            for user_data in ret:
                self._apply_user_data(user_data)
            return ret

    async def _fetch_channel_data(self, broadcaster_id: int) -> Optional[TwitchChannelData]:
        url = HELIX_CHANNELS_URL
        headers = {"Authorization": f"Bearer {await self.get_app_token()}", "Client-Id": self._id}
        response = await self._session.get(url, params={"broadcaster_id": broadcaster_id}, headers=headers)
        response_json = await response.json()
        if response_json.get("error", None):
            return None
        else:
            return TwitchChannelData(response_json["data"][0])

    async def get_channel_data(self, broadcaster_id: int, use_cache: bool = True) -> Optional[TwitchChannelData]:
        if use_cache and broadcaster_id in self._channel_cache:
            return self._channel_cache[broadcaster_id]
        else:
            channel_data = await self._fetch_channel_data(broadcaster_id)
            self._channel_cache[broadcaster_id] = channel_data
            return channel_data








# async def get_streamer_id(streamer_name: str) -> Optional[int]:
#     url = "https://api.twitch.tv/helix/users"
#     response = await self.session.get(url, params={"login": streamer_name},
#                                       headers={"Authorization":
#                                       f"Bearer {await self.cache.get_token(self.config, self.session)}",
#                                                "Client-ID": self.config.client_id})
#     response_json = await response.json()
#     if response_json["data"]:
#         return int(response_json["data"][0]["id"])
#     else:
#         return None


# async def get_streamer_data(streamer_id: int):
#     url = "https://api.twitch.tv/helix/channels"
#     response = await self.session.get(url, params={"broadcaster_id": streamer_id},
#                                       headers={"Authorization":
#                                       f"Bearer {await self.cache.get_token(self.config, self.session)}",
#                                                "Client-ID": self.config.client_id})
#     response_json = await response.json()
#     return response_json["data"][0]






