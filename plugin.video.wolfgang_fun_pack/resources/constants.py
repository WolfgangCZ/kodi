
from dataclasses import dataclass

@dataclass
class SettingsAccount:
    USERNAME = "username"
    PASSWORD = "password"

@dataclass
class SettingsSystem:
    FIRST_RUN = "first_run"

@dataclass
class UrlItems:
    SEARCH_GLOBAL = "search_global"
    PLAY_VIDEO = "play_video"
    LAST_SEARCH = "last_search"

@dataclass
class UrlKeys:
    ACTION = "action"
    IDENTIFIER = "ident"
