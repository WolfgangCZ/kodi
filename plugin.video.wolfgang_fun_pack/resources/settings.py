from typing import Union
from dataclasses import dataclass
from resources import config

@dataclass
class SettingTag:
    name: str
    type: Union[str, int, bool]
    public: bool

@dataclass
class SettingKeys:
    USER_NAME = SettingTag(name="username", type=str, public=True)
    PASSWORD = SettingTag(name="password", type=str, public=True)
    HASHED_PASSWORD  = SettingTag(name="hashed_password", type=str, public=False)
    LAST_SEARCH = SettingTag(name="last_search", type=str, public=False)
    FIRST_RUN = SettingTag(name="first_run", type=bool, public=False)

class Settings:
    @classmethod
    def _check_type(cls, key: SettingTag, typ: type) -> None:
        if key.type is not typ:
            raise TypeError("key.type must be %s" % typ)
        
    @classmethod
    def _check_value(cls, key: SettingTag, value) -> None:
        if not isinstance(value, key.type):
            raise TypeError("key.type must be %s" % type(value))

    @classmethod
    def get_str(cls, key: SettingTag) -> str:
        cls._check_type(key, str)
        return config.ADDON.getSetting(key.name)
    
    @classmethod
    def get_bool(cls, key: SettingTag) -> bool:
        cls._check_type(key, bool)
        return config.ADDON.getSettingBool(key.name)
    
    @classmethod
    def get_int(cls, key: SettingTag) -> int:
        cls._check_type(key, int)
        return config.ADDON.getSettingInt(key.name)
    
    @classmethod
    def set_str(cls, key: SettingTag, value: str) -> None:
        cls._check_type(key, str)
        cls._check_value(key, value)
        config.ADDON.setSetting(key.name, value)
    
    @classmethod
    def set_bool(cls, key: SettingTag, value: bool) -> None:
        cls._check_type(key, bool)
        cls._check_value(key, value)
        config.ADDON.setSettingBool(key.name, value)
    
    @classmethod
    def set_int(cls, key: SettingTag, value: int) -> None:
        cls._check_type(key, int)
        cls._check_value(key, value)
        config.ADDON.setSettingInt(key.name, value)
