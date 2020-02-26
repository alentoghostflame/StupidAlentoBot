# import typing


class ConfigData:
    def __init__(self):
        self.token: str = ""
        self.data_storage_path = "data/"
        self.server_data_file_name = "server_data.yaml"

    def __setstate__(self, state: dict):
        self.__dict__ = state
        self.token = state.get("token", "")
        self.storage_path = state.get("data_storage_path", "data/")
        self.server_data_file_name = state.get("server_data_file_name", "server_data.yaml")
