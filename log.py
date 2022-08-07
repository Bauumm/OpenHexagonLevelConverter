import coloredlogs
import inspect
import logging
import os


coloredlogs.install(level=logging.INFO,
                    fmt="[%(asctime)s] [%(name)s/%(levelname)s] %(message)s",
                    datefmt="%H:%M:%S")


def _log(*text, level=logging.INFO):
    logging.getLogger(os.path.basename(
        inspect.getouterframes(inspect.currentframe())[2].filename)
    ).log(level, " ".join([str(i) for i in text]))


def info(*text): _log(*text)
def warn(*text): _log(*text, level=logging.WARNING)
def error(*text): _log(*text, level=logging.ERROR)
