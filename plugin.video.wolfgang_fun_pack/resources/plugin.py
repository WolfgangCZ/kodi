import os
import sys
import re
import time
from typing import Tuple, List, Dict

sys.path.append(os.path.join(os.path.dirname(__file__), "packages"))

import xbmc
from dataclasses import dataclass
from resources.constants import UrlItems, UrlKeys
from resources import config
import xbmcplugin # type: ignore
import xbmcaddon # type: ignore
import xbmcgui # type: ignore
from urllib.parse import urlparse, parse_qs
from resources.client import WebshareClient
from resources.encrypt import encrypt_password
from resources.strings import InputStrings, PopUpStrings
from resources.logger import logger, KodiLoggger
from resources.enums import ConnectionStatus
from resources.settings import Settings, SettingKeys
from resources.authentication import Authentication

@dataclass
class UrlParams:
    key: str
    name: str

# TODO: instead of this create some kind of tree, this seems dumb
@dataclass
class UrlPaths:
    MAIN_SEARCH = [
        (UrlKeys.ACTION, UrlItems.SEARCH_GLOBAL)
        ]
    PLAY_VIDEO = [
        (UrlKeys.ACTION, UrlItems.PLAY_VIDEO),
    ]
    LAST_SEARCH = [
        (UrlKeys.ACTION, UrlItems.LAST_SEARCH)
    ]


class MenuItem:
    def __init__(self, label: str, url: str, is_folder: bool = False) -> None:
        self.label = label
        self.url = url
        self.is_folder = is_folder

class MainMenuItems:
    SEARCH = "search"


@dataclass
class SearchResult:
    file_name: str
    img: str
    identifier: str
    type: str

class Plugin:
    def __init__(self):
        self.client = WebshareClient()
        self._auth_token: str = ""

    def run(self):
        # because first time we get false then we set it to true
        first_run: bool = Settings.get_bool(SettingKeys.FIRST_RUN)
        logger.info("Is first run: %s", first_run)
        if Authentication.check_connection():
            if first_run:
                username, password = self.first_run()
                Authentication._login(username=username, password=password, first_time=True)
        self.resolve_url(config.CURRENT_URL)

    def get_file_link(self, identifier: str, auth_token: str) -> str:
        file_data, _ = self.client.file_link(identifier, auth_token) 
        if file_data.get("response", {}).get("status") != "OK":
            return ""
        return file_data["response"]["link"]
    
    def url_check(self, params: List[UrlParams], checks: List[Tuple[str, str]]) -> bool:
        # TODO: this feels dumb
        if len(params) < len(checks):
            return False
        if not params:
            return False
        for param, check in zip(params, checks):
            if param.key != check[0] or param.name != check[1]:
                return False
        return True
    
    def find_subtitles(self, video_name: str) -> str:
        video_name = os.path.splitext(video_name)[0]
        subtitles_data, _ = self.client.search(video_name + ".srt", category="")
        if subtitles_data.get("response", {}).get("status") != "OK":
            return ""
        files = subtitles_data["response"]["file"]
        for file in files:
            if file["password"] == 1:
                continue
            if file["name"] == video_name + ".srt":
                return file["ident"]
        return ""
    
    def resolve_url(self, current_url: str) -> str:
        logger.info("Resolving URL: %s", current_url)
        params = self.get_url_params(current_url)
        logger.info("Input url params: %s", params)
        if self.url_check(params, UrlPaths.MAIN_SEARCH):
            defaultt = self.get_last_searched()
            query = xbmcgui.Dialog().input("Hledat:", defaultt=defaultt)
            if not query:
                self.show_main_menu()
                return
            logger.info("Showing results for: %s", query)
            self.show_search_results(query)
            self.set_last_search(query)
        elif self.url_check(params, UrlPaths.LAST_SEARCH):
            query = self.get_last_searched()
            logger.info("Showing last search for: %s", query)
            # TODO: do list of last searches as Seznam poslednich hledani
            self.show_search_results(query)
        elif self.url_check(params, UrlPaths.PLAY_VIDEO):
            video_identifier = params[1].name
            subtitle_identifier = self.find_subtitles(params[2].name)
            logger.info("Playing video: %s", video_identifier)
            self.play_video(video_identifier, subtitle_identifier)
        else:
            logger.info("Showing main menu")
            self.show_main_menu()
        
    def play_video(self, video_identifier: str, subtitle_identifier: str) -> None:
        token = Authentication.get_auth_token()
        logger.info("token: %s", token)
        if not token:
            return
        video_link = self.get_file_link(video_identifier, token)
        subtitle_link = self.get_file_link(subtitle_identifier, token)
        logger.info("Playing video, link: %s", video_link)
        player = xbmc.Player()
        player.play(video_link)
        while not player.isPlaying():
            xbmc.sleep(500)
        if subtitle_link:
            logger.info("Playing subtitles, link: %s", subtitle_link)
            player.setSubtitles(subtitle_link)

    def show_main_menu(self):
        url = self.construct_url([UrlParams(key=UrlKeys.ACTION, name=UrlItems.SEARCH_GLOBAL)])
        li = xbmcgui.ListItem(label="Hledej")
        xbmcplugin.addDirectoryItem(
            handle=config.HANDLE, url=url, listitem=li, isFolder=True
        )
        if self.get_last_searched():
            url = self.construct_url([UrlParams(key=UrlKeys.ACTION, name=UrlItems.LAST_SEARCH)])
            li = xbmcgui.ListItem(label="Poslední hledání")
            xbmcplugin.addDirectoryItem(
                handle=config.HANDLE, url=url, listitem=li, isFolder=True
            )
        xbmcplugin.endOfDirectory(handle=config.HANDLE)
    
    def get_last_searched(self) -> str:
        return Settings.get_str(SettingKeys.LAST_SEARCH)
    
    def set_last_search(self, query: str):
        Settings.set_str(SettingKeys.LAST_SEARCH, query)
    
    def search_for_videos(self, query: str, limit: int = 1000) -> List[SearchResult]:
        search_data, _ =  self.client.search(query=query, limit=limit)
        if search_data.get("response", {}).get("status") != "OK" or not search_data.get("response", {}).get("file"):
            return []
        results = search_data["response"]["file"]
        valid_results = []
        for result in results:
            if result["password"] == 1:
                continue
            valid = SearchResult(
                file_name = result["name"],
                img = result["img"],
                identifier=result["ident"],
                type=result["type"]
            )
            valid_results.append(valid)
        return valid_results
        
    def get_url_params(self, url: str) -> List[UrlParams]:
        if not url:
            return []
        url = url[1:]
        params: List[UrlParams] = []
        for item in url.split("&"):
            key, value = item.split("=")
            params.append(UrlParams(key=key, name=value))
        return params
    
    def construct_url(self, params: List[UrlParams]):
        url = f"{config.BASE_URL}?"
        for param in params:
            url += f"{param.key}={param.name}&"
        return url[:-1]

    def tokenize(self, text: str):
        # Lowercase and split on common separators
        return re.split(r'[\s._\-()\[\]]+', text.lower())

    def custom_sort(self, query: str, results: List[SearchResult]) -> List[SearchResult]:
        query_words = set(self.tokenize(query))
        ranked_results: Dict[int, List[SearchResult]] = {}
        for result in results:
            tokenized_result = set(self.tokenize(result.file_name))
            score = len(query_words.intersection(tokenized_result))
            ranked_results.setdefault(score, []).append(result)
        sorted_results: List[SearchResult] = []
        for score, results in ranked_results.items():
            ranked_results[score] = list(sorted(results, key=lambda x: x.file_name))
        scores = sorted(ranked_results.keys(), reverse=True)
        for score in scores:
            sorted_results.extend(ranked_results[score])
        return sorted_results

    def show_search_results(self, query: str):
        videos = self.search_for_videos(query)
        if not videos:
            xbmcgui.Dialog().ok("Nenalezeno", "Fakt.. přísahám, díval jsem se i pod polštář")
            return
        # sorted_videos = self.custom_sort(query, videos)
        for video in videos:
            li = xbmcgui.ListItem(label=video.file_name)
            params = [
                UrlParams(key=UrlKeys.ACTION, name=UrlItems.PLAY_VIDEO),
                UrlParams(key=UrlKeys.IDENTIFIER, name=video.identifier),
                UrlParams(key=UrlKeys.FILE_NAME, name=video.file_name),
                ]
            play_url = self.construct_url(params)
            xbmcplugin.addDirectoryItem(handle=config.HANDLE, url=play_url, listitem=li ,isFolder=False)
        xbmcplugin.endOfDirectory(handle=config.HANDLE)
