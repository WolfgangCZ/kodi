from dataclasses import dataclass


@dataclass
class SettingKeyStr:
    USER_NAME = "username"
    HASHED_PASSWORD  = "password"
    LAST_SEARCH = "last_search"

@dataclass
class SettingsKeyBool:
    FIRST_RUN = "first_run"