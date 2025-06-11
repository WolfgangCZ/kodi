import sys
import xbmcaddon

ADDON = xbmcaddon.Addon()
SETTINGS = xbmcaddon.Settings

FIRST_RUN = False
DEBUG = True

BASE_URL = sys.argv[0]
HANDLE = int(sys.argv[1])
CURRENT_URL = sys.argv[2]
WHAT_IS_THIS = sys.argv[3]
