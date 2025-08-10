from typing import Tuple
import xbmcgui
import xbmc
from resources.logger import logger
from resources.settings import Settings, SettingKeys
from resources.strings import InputStrings, PopUpStrings
from resources.encrypt import encrypt_password
from resources.client import ConnectionStatus, WebshareClient

class Authentication:
    _auth_token = ""
    _client = WebshareClient()

    @classmethod
    def first_run(cls) -> Tuple[str, str]:
        logger.info("First run")
        xbmcgui.Dialog().ok('Nazdárek párek', InputStrings.WELCOME)
        Settings.set_bool(SettingKeys.FIRST_RUN, False)

        username = cls.prompt_username(first_time=True)
        password = cls.prompt_password(first_time=True)

        return username, password

    @classmethod
    def get_auth_token(cls) -> str:
        if cls._auth_token:
            return cls._auth_token
        username = Settings.get_str(SettingKeys.USER_NAME)
        password = Settings.get_str(SettingKeys.PASSWORD)
        hashed_password = Settings.get_str(SettingKeys.HASHED_PASSWORD)
        if not username or (not password and not hashed_password):
            logger.info("Missing username or password")
            xbmcgui.Dialog().ok('Wtf', PopUpStrings.INVALID_CREDENTIALS)
            username = cls.prompt_username(first_time=False)
            password = cls.prompt_password(first_time=False)
            if (hashed_password or password) and username:
                cls._auth_token = cls._login(username=username, password=password, hashed_password=hashed_password)
            else:
                return ""
        else:
            cls._auth_token = cls._login(username=username, hashed_password=hashed_password)
            return cls._auth_token
        if not cls._auth_token:
            xbmcgui.Dialog().ok('Wtf', PopUpStrings.COULDNT_LOGIN)
            Settings.set_str(SettingKeys.USER_NAME, "")
            Settings.set_str(SettingKeys.PASSWORD, "")
            Settings.set_str(SettingKeys.HASHED_PASSWORD, "")
        return cls._auth_token

    @classmethod    
    def prompt_credentials(cls, first_time: bool = False) -> Tuple[str, str]:
        username = cls.prompt_username(first_time)
        if username:
            password = cls.prompt_password(first_time)
        if not username or not password:
            return "", ""
        return username, password
    
    @staticmethod
    def prompt_username(first_time: bool = False) -> str:
        if first_time:
            xbmcgui.Dialog().ok('Uživatelské jméno', InputStrings.USERNAME_MISSING_FIRST_TIME)
        username = xbmcgui.Dialog().input('Username')
        if not username:
            xbmcgui.Dialog().ok('Tak si ho nech pro sebe', PopUpStrings.USERNAME_NOT_PROVIDED)
            return "", ""
        return username

    @staticmethod    
    def prompt_password(first_time: bool = False) -> str:
        if first_time:
            xbmcgui.Dialog().ok('Heslo', InputStrings.PASSWORD_MISSING_FIRST_TIME)
        keyboard = xbmc.Keyboard("", "heslo", True)
        keyboard.doModal()
        password = ""
        if keyboard.isConfirmed():
            password = keyboard.getText().strip()
        if not password:
            xbmcgui.Dialog().ok('To jsou teda tajnosti...', PopUpStrings.PASSWORD_NOT_PROVIDED)
        return password

    @classmethod
    def get_salt(cls, username: str) -> str:
        salt_data, _ = cls._client.salt(username)
        status = salt_data['response']['status']
        if status == "OK":
            return salt_data["response"]["salt"]
        message = salt_data['response']['message']
        if message == "User not found":
            xbmcgui.Dialog().ok('Wtf', PopUpStrings.USER_NOT_FOUND)
        return ""

    @classmethod
    def _login(cls, username: str, password: str = "", hashed_password: str = "", first_time: bool = False) -> str:
        """
        This also save credentials to settings
        Returns: token
        """
        if not hashed_password:
            salt = cls.get_salt(username)
            if not salt:
                return ""
            hashed_password = encrypt_password(password, salt)
        login_data, _ = cls._client.login(username, hashed_password)
        if login_data.get("response", {}).get("status") == "OK":
            Settings.set_str(SettingKeys.USER_NAME, username)
            Settings.set_str(SettingKeys.HASHED_PASSWORD, hashed_password)
            if password:
                Settings.set_str(SettingKeys.PASSWORD, password)
            if first_time:
                xbmcgui.Dialog().ok('', PopUpStrings.JOKE_1)
                xbmcgui.Dialog().ok('', PopUpStrings.JOKE_2)
                xbmcgui.Dialog().ok('Připojeno', PopUpStrings.FIRST_SUCCESFUL_LOGIN)
            return login_data["response"]["token"]
        return ""
    
    @classmethod    
    def check_connection(cls) -> bool:

        status = cls._client.check_connection()
        if status == ConnectionStatus.OK:
            return True
        if status == ConnectionStatus.NO_INTERNET:
            xbmcgui.Dialog().ok('Seš připojenej?', PopUpStrings.NO_INTERNET)
        elif status == ConnectionStatus.NO_WEBSHARE:
            xbmcgui.Dialog().ok('A kurva', PopUpStrings.NO_WEBSHARE)
        return False
    