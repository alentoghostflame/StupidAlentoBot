from eve_module.storage.eve_config import EVEConfig
from alento_bot import StorageManager
import urllib.parse
import requests
import logging
import typing
import base64


logger = logging.getLogger("main_bot")


"""
PROBLEM WITH ALL OF THIS: NAMING IS INCONSISTENT.
AUTH CODE IS WHAT YOU GET FROM THE OAUTH WEBSITES RETURN URL
REFRESH TOKEN IS WHAT YOU GET BY USING THE AUTH CODE
ACCESS TOKEN IS WHAT YOU GET BY (RE)USING THE REFRESH TOKEN
"""


class EVEAuthManager:
    def __init__(self, storage: StorageManager):
        self.storage: StorageManager = storage
        self.eve_config: EVEConfig = self.storage.caches.get_cache("eve_config")

    def load(self):
        if not self.eve_config.loaded() or not self.eve_config.refresh_token:
            self.create_refresh_token_guide()

    def create_refresh_token_guide(self):
        if not self.eve_config.auth_code and self.create_eve_auth_url_checks():
            self.create_eve_auth_url()
        elif self.eve_config.auth_code and not self.eve_config.refresh_token:
            self.create_refresh_token()

    def create_eve_auth_url_checks(self) -> bool:
        passed_checks = True
        if not self.eve_config.client_id:
            logger.error("Missing EVE App client ID in config.")
            passed_checks = False
        if not self.eve_config.callback_url:
            logger.error("Missing EVE App callback URL in config.")
            passed_checks = False
        if not self.eve_config.scopes:
            logger.error("Missing EVE App scopes in config.")
            passed_checks = False
        if not self.eve_config.unique_state:
            logger.error(
                "Missing EVE App unique state. You're supposed to replace the default with something unique, not"
                " remove it.")
            passed_checks = False

        if not passed_checks:
            logger.error("Cannot create EVE App authorization URL, missing components.")
        return passed_checks

    def create_eve_auth_url(self):
        base_url = "https://login.eveonline.com/oauth/authorize/?response_type=code&redirect_uri={}&client_id={}" \
                   "&scope={}&state={}"
        redirect_uri = urllib.parse.quote_plus(self.eve_config.callback_url)
        client_id = urllib.parse.quote_plus(self.eve_config.client_id)
        scope = urllib.parse.quote_plus(self.eve_config.scopes)
        state = urllib.parse.quote_plus(self.eve_config.unique_state)

        auth_url = base_url.format(redirect_uri, client_id, scope, state)
        logger.info("Authorization URL: {}\nGo to that website, and authorize your account. You will get redirected"
                    " to the callback_url (which may result in a 404), but what you want is the access code in the"
                    " URL. Look for \"?code=<code here>\" and paste that code in auth_code in the eve_config."
                    "".format(auth_url))

    def create_refresh_token(self):
        response_dict = self.fetch_refresh_token()
        if response_dict.get("error", "") == "invalid_request":
            logger.error("Failed to get access token: {}".format(response_dict.get("error_description",
                                                                                   "No description found??")))
        elif response_dict.get("refresh_token", ""):
            self.eve_config.refresh_token = response_dict["refresh_token"]
            logger.info("Received refresh token.")
            self.eve_config.save()
        else:
            # logger.critical("Unexpected response given:\n{}".format(response_dict))
            logger.critical(f"Unexpected response given:\n{response_dict}")

    def fetch_refresh_token(self) -> typing.Optional[dict]:
        auth_key = base64.b64encode(bytes("{}:{}".format(self.eve_config.client_id,
                                                         self.eve_config.secret_key), "utf-8")).decode("utf-8")
        headers = {"Authorization": f"Basic {auth_key}", "Content-Type": "application/x-www-form-urlencoded",
                   "Host": "login.eveonline.com"}
        data_bits = {"grant_type": "authorization_code", "code": self.eve_config.auth_code}
        response = requests.post(url="https://login.eveonline.com/oauth/token", headers=headers, data=data_bits)
        return response.json()

    def get_access_token(self) -> typing.Optional[str]:
        if self.eve_config.refresh_token:
            auth_key = base64.b64encode(bytes("{}:{}".format(self.eve_config.client_id,
                                                             self.eve_config.secret_key), "utf-8")).decode("utf-8")
            headers = {"Authorization": "Basic {}".format(auth_key),
                       "Content-Type": "application/x-www-form-urlencoded", "Host": "login.eveonline.com"}
            data_bits = {"grant_type": "refresh_token", "refresh_token": self.eve_config.refresh_token}
            # print(f"EVE_AUTH GET ACCESS TOKEN {data_bits}")
            response = requests.post(url="https://login.eveonline.com/oauth/token", headers=headers, data=data_bits)
            # print(f'EVE_AUTH RESPONSE {response.json()}')
            if response.content:
                return response.json().get("access_token", None)
            else:
                return None
        else:
            logger.warning("Attempt to get access token failed, you need to set up authorization!")
            return None
