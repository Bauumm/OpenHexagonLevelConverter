from config import SAVE_LOG_LEVELS
import coloredlogs
import inspect
import logging
import atexit
import os


coloredlogs.install(level=logging.INFO,
                    fmt="[%(asctime)s] [%(name)s/%(levelname)s] %(message)s",
                    datefmt="%H:%M:%S")
if len(SAVE_LOG_LEVELS) > 0:
    log_file = open("log.txt", "a")
    atexit.register(log_file.close)


def _log(*text, level=logging.INFO):
    string = " ".join([str(i) for i in text])
    if level in SAVE_LOG_LEVELS:
        log_file.write(string + "\n")
    logging.getLogger(os.path.basename(
        inspect.getouterframes(inspect.currentframe())[2].filename)
    ).log(level, string)


def info(*text): _log(*text)
def warn(*text): _log(*text, level=logging.WARNING)
def error(*text): _log(*text, level=logging.ERROR)
