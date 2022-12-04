from extended_dict import ExtendedDict
from json_fixer import fix_json_string
import chardet
import json
import log
import os


class JsonFile(ExtendedDict):
    def __init__(self, path):
        self.saved = False
        self.path = path
        with open(path, "rb") as file:
            encoding = chardet.detect(file.read())["encoding"]
        with open(path, encoding=encoding) as json_file:
            json_string = json_file.read()
            if len(json_string) == 0:
                json_string = "{}"
            content = fix_json_string(json_string) \
                .replace("\n", "\\n") \
                .replace(":inf", ":Infinity") \
                .replace(":-inf", ":-Infinity") \
                .replace(",inf", ",Infinity") \
                .replace(",-inf", ",-Infinity")
        while content[-1] != "}":
            content = content[:-1]
        json_dict = json.loads(content)
        for key in json_dict:
            self[key] = json_dict[key]

    def copy(self):
        def copy_value(value):
            if isinstance(value, dict):
                value = recursive_dict_copy(value)
            elif isinstance(value, list):
                value = recursive_list_copy(value)
            return value

        def recursive_list_copy(obj):
            copy = []
            for value in obj:
                copy.append(copy_value(value))
            return copy

        def recursive_dict_copy(obj):
            copy = {}
            for key in obj.keys():
                copy[key] = copy_value(obj[key])
            return copy
        return recursive_dict_copy(self)

    def save(self, path):
        if self.saved:
            log.warn("Saving", os.path.basename(self.path), "twice!")
        if "/" in path:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as file:
            json.dump(self, file, indent=4)
