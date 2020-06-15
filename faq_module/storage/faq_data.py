from alento_bot import StorageManager, guild_data_transformer
import logging
import typing


logger = logging.getLogger("main_bot")


class FAQData:
    def __init__(self, state: dict = None):
        self.keyword: str = ""
        self.phrase: str = ""
        self.image_url: str = ""

        if state:
            self.from_state(state)

    def from_state(self, state: dict):
        self.keyword = state.get("keyword", "")
        self.phrase = state.get("phrase", "")
        self.image_url = state.get("image_url", "")


class FAQManager:
    def __init__(self, storage: StorageManager):
        self.storage: StorageManager = storage
        self.storage.guilds.register_data_name("faq_storage", FAQStorage)

    def create(self, guild_id: int, keyword: str, phrase: str, image_url: str = ""):
        guild_data: FAQStorage = self.storage.guilds.get(guild_id, "faq_storage")
        faq_dict = {"keyword": keyword.lower(), "phrase": phrase, "image_url": image_url}
        guild_data.phrases[keyword.lower()] = faq_dict

    def get(self, guild_id: int, keyword: str) -> typing.Optional[FAQData]:
        guild_data: FAQStorage = self.storage.guilds.get(guild_id, "faq_storage")
        faq_data = guild_data.phrases.get(keyword.lower(), None)
        if faq_data:
            return FAQData(state=faq_data)
        else:
            return None

    def remove(self, guild_id: int, keyword: str):
        guild_data: FAQStorage = self.storage.guilds.get(guild_id, "faq_storage")
        guild_data.phrases.pop(keyword.lower(), None)

    def get_keywords(self, guild_id) -> typing.Set[str]:
        guild_data: FAQStorage = self.storage.guilds.get(guild_id, "faq_storage")
        return set(guild_data.phrases.keys())


@guild_data_transformer(name="faq_storage")
class FAQStorage:
    def __init__(self):
        self.phrases: typing.Dict[str, dict] = dict()


@guild_data_transformer(name="faq_config")
class FAQConfig:
    def __init__(self):
        self.enabled: bool = True
        self.edit_roles: typing.Set[int] = set()
