from resources.logger import logger
# 2025-06-08 17:15:27,029 | default.py:2 | INFO: Arguments: plugin://plugin.video.wolfgang_webshare/ 1 
import sys
from resources.plugin import Plugin
from resources import config

if config.DEBUG:
    logger.info("DEBUG MODE ENABLED")
logger.info("====================")
logger.info("Arguments:")
for i, arg in enumerate(sys.argv):
    logger.info("Arg[%s]: '%s'", i, arg)
logger.info("====================")

plugin = Plugin()
plugin.run()
