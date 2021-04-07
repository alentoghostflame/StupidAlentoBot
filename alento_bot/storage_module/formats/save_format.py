from pathlib import Path
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap


class SaveLoadConfig:
    """
    A class that will automatically take any non-protected variables and allow them to be saved to and loaded from disk.
    While you could subclass this (untested), you should use the decorator instead.
    Variables prefixed with _c_ are treated as comments for the variable that comes after the prefix.
    Variables prefixed with _ are ignored.
    """
    def __init__(self):
        self._from_disk: bool = False
        self._yaml = YAML(typ="rt")
        self._yaml.indent = 4

    @classmethod
    def __init_subclass__(cls, path: str, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._data_path: str = path

    @property
    def from_disk(self) -> bool:
        return self._from_disk

    def save(self):
        self.pre_save()
        file = open(self._data_path, "w")
        self._yaml.dump(self._build_ruamel_map(), file)
        file.close()
        self.post_save()

    def load(self):
        self.pre_load()
        file_location = self._data_path
        if Path(file_location).is_file():
            file = open(file_location, "r")
            state = self._yaml.load(file)
            file.close()
            if state:
                self._from_dict(state)
                self._from_disk = True
        self.post_load()

    def _from_dict(self, state: dict):
        for key in state:
            if key in self.__dict__:
                self.__dict__[key] = state[key]

    def to_dict(self) -> dict:
        output_dict = dict()
        for key in self.__dict__:
            if key[0] != "_":
                output_dict[key] = self.__dict__[key]
        return output_dict

    def _build_ruamel_map(self) -> CommentedMap:
        ret = CommentedMap()
        self._recursive_build_dict(ret, self.__dict__, 0, 0)
        return ret

    def _recursive_build_dict(self, comment_map: CommentedMap, source_dict: dict, index: int, deepness: int) -> int:
        # If you find a way to sanely do this without going over it multiple times and not having it be recursive, be
        # my guest.
        cur_index = index
        for key in source_dict:
            if not key.startswith("_"):
                if isinstance(source_dict[key], dict):
                    new_map = CommentedMap()
                    comment_map.insert(cur_index, key, new_map)
                    cur_index += 1
                    cur_index = self._recursive_build_dict(new_map, source_dict[key], cur_index, deepness + 1)
                else:
                    comment_map.insert(cur_index, key, source_dict[key])
                    cur_index += 1
            # TODO: Change following if statement to use the walrus operator once 3.8+ becomes minimum.
            key_comment = source_dict.get(f"_c_{key}", None)
            if key_comment:
                comment_map.yaml_set_comment_before_after_key(key, key_comment, deepness * 4)
        return cur_index

    def pre_save(self):
        # Decorated class should override as needed.
        pass

    def post_save(self):
        # Decorated class should override as needed.
        pass

    def pre_load(self):
        # Decorated class should override as needed.
        pass

    def post_load(self):
        # Decorated class should override as needed.
        pass


def config_file(path: str):
    """
    Decorator that turns a given class into a config class with save and load methods.
    @param path: File path to save the class to.
    @return: Decorated class.
    """
    def decorator(cls):
        class ConfigWrapperClass(cls, SaveLoadConfig, path=path):
            def __init__(self, **kwargs):
                SaveLoadConfig.__init__(self)
                cls.__init__(self, **kwargs)
        return ConfigWrapperClass
    return decorator


class DictConfig:
    def from_dict(self, state: dict):
        for key in state:
            if key in self.__dict__:
                self.__dict__[key] = state[key]

    def to_dict(self) -> dict:
        output_dict = dict()
        for key in self.__dict__:
            if not key.startswith("_") or key.startswith("_c_"):
                output_dict[key] = self.__dict__[key]
        return output_dict
