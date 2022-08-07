from colorama import Fore


def _log(*text, color=Fore.RESET, level="INFO"):
    print(color + "[" + level + "]", *text, Fore.RESET)


def info(*text): _log(*text)
def warn(*text): _log(*text, color=Fore.YELLOW, level="WARN")
def error(*text): _log(*text, color=Fore.RED, level="ERROR")
