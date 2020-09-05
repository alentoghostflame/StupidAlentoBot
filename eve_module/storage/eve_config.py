from alento_bot import cache_transformer


@cache_transformer(name="eve_config")
class EVEConfig:
    def __init__(self):
        self.refresh_token: str = ""
        self.client_id: str = ""
        self.secret_key: str = ""
        self.callback_url: str = ""
        self.scopes: str = ""
        self.unique_state: str = "NotAUniqueState"
        self.auth_code: str = ""

        self.sde_location: str = "sde"

        self.tracked_structure_markets: list = []
