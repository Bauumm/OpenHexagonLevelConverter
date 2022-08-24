from extended_dict import ExtendedDict
from json_fixer import fix_json
import json
import log
import os


class JsonFile(ExtendedDict):
    def __init__(self, path):
        self.saved = False
        self.path = path
        content = fix_json(path) \
            .replace("\n", "\\n") \
            .replace(":inf,", ":Infinity,") \
            .replace(":-inf,", ":-Infinity,")
        while content[-1] != "}":
            content = content[:-1]
        json_dict = json.loads(content)
        for key in json_dict:
            self[key] = json_dict[key]

    def save(self, path):
        if self.saved:
            log.warn("Saving", os.path.basename(self.path), "twice!")
        if "/" in path:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as file:
            json.dump(self, file, indent=4)
