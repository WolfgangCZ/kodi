
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
    LAST_SEARCH_INPUTS = "last_search_inputs"
    PROMPT_LAST_SEARCH = "prompt_last_search"

@dataclass
class UrlKeys:
    ACTION = "action"
    IDENTIFIER = "ident"
    FILE_NAME = "video_name"
