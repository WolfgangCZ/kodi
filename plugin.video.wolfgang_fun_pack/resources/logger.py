import os
import sys
import logging

# Set log file path
this_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(this_dir, os.pardir, 'debug.log')
if os.path.exists(log_path):
    lines = open(log_path, 'r').readlines()
    if len(lines) > 1000:
        os.remove(log_path)
        file = open(log_path, 'w')
        file.writelines(lines[-1000:])

# ANSI escape codes for colors
COLORS = {
    'DEBUG': '\033[96m',    # Cyan
    'INFO': '\033[92m',     # Green
    'WARNING': '\033[93m',  # Yellow
    'ERROR': '\033[91m',    # Red
    'CRITICAL': '\033[95m', # Magenta
    'ENDC': '\033[0m'       # Reset
}

class ColorFormatter(logging.Formatter):
    def format(self, record):
        levelname = record.levelname
        color = COLORS.get(levelname, COLORS['ENDC'])
        record.levelname = f"{color}{levelname}{COLORS['ENDC']}"
        return super().format(record)

# Common format string
format_str = "%(asctime)s | %(filename)s:%(lineno)d | %(levelname)s: %(message)s"

# File handler (no color)
file_handler = logging.FileHandler(log_path)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(format_str))

# Console handler (with color)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(ColorFormatter(format_str))

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)


# Test output
if __name__ == "__main__":
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
