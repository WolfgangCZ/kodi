from resources.encrypt import encrypt_password
import requests # type: ignore
import xmltodict # type: ignore
from typing import Tuple, Optional
from pprint import pprint
from resources.logger import logger
from resources.enums import ConnectionStatus

API_URL = "https://webshare.cz/api"


class WebshareClient:
    """
    Client for https://webshare.cz/api
    """
    def __init__(self) -> None:
        self.session = requests.Session()
        self._auth_token: str = ""
    
    @property
    def auth_token(self) -> str:
        if not self._auth_token:
            raise ValueError("Not logged in")
        return self._auth_token
    
    def _post(self, api_target: str, data: Optional[dict] = None):
        if data is None:
            data = {}
        if self._auth_token:
            data["wst"] = self._auth_token
        url = f"{API_URL}/{api_target}/"
        return self.session.post(url, data=data)
    
    def check_connection(self) -> ConnectionStatus:
        try:
            response = self.session.get(f"{API_URL}/help/")
        except requests.exceptions.ConnectionError as e:
            logger.error("Connection error: %s", e)
            return ConnectionStatus.NO_INTERNET
        if response.status_code == 200:
            return ConnectionStatus.OK
        return ConnectionStatus.NO_WEBSHARE

    def login(self, user_name: str, password: str) -> Tuple[dict, requests.Response]:
        data = {
            "username_or_email": user_name,
            "password": password,
            "keep_logged_in": 1,
        }
        response = self.session.post(f"{API_URL}/login/", data=data)
        response.raise_for_status()
        response_content = xmltodict.parse(response.text)
        self._auth_token = response_content.get("response", {}).get("token")
        return response_content, response
    
    def file_link(self, 
                  identifier: str, 
                  wst_token: str
                  ) -> Tuple[dict, requests.Response]:
        self._auth_token = wst_token
        data = {
            "ident": identifier,
            "wst": wst_token,
        }
        response = self._post("file_link", data)
        response.raise_for_status()
        return xmltodict.parse(response.text), response
    
    def search(self, query: str, sort: str = "recent", offset: int = 0, category: str = "video", limit: int = 20) -> Tuple[dict, requests.Response]:
        data = {
            "what": query,
            "sort": sort,
            "limit": limit,
            "offset": offset,
            "category": category,
        }
        response = self._post("search", data) 
        response.raise_for_status()
        return xmltodict.parse(response.text), response

    def salt(self, user_name: str) -> Tuple[dict, requests.Response]:
        data = {
            "username_or_email": user_name,
        }
        response = self._post("salt", data)
        response.raise_for_status()
        return xmltodict.parse(response.text), response

    
if __name__ == "__main__":
    client = WebshareClient()
    login_file = open("login.key", "r").readlines()
    login = login_file[0].strip()
    password_raw = login_file[1].strip()
    salt_data, _ = client.salt(login)
    pprint(salt_data)
    salt = salt_data["response"]["salt"]
    pprint(f"salt: {salt}")
    password = encrypt_password(password_raw, salt)

    print(f"login: {login} password: {password} raw: {password_raw}")
    # password = login_file[1].strip()
    login_res = client.login(login, password)
    print("========================================")
    search_data, _ = client.search(query="chronicles", limit=3)
    pprint(search_data)
    # print("========================================")
    # search_res = client.search(query="chronicles", limit=3)
    # pprint(search_res)
    # print("========================================")
