from json_file import JsonFile
from lua_file import LuaFile
import level_properties
import dpath.util
import log
import sys
import os


def get_files(folder):
    structure = {}
    for file in os.listdir(folder):
        path = os.path.join(folder, file)
        if os.path.isdir(path):
            structure[file] = get_files(path)
        else:
            if path.endswith(".json"):
                structure[file] = JsonFile(path)
            elif path.endswith(".lua"):
                structure[file] = LuaFile(path)
    return structure


def convert_pack(path):
    files = get_files(path)
    if files.get("pack.json") is None:
        log.error("No pack.json found in", path)
        exit(1)
    else:
        levels = files.get("Levels")
        for level in levels:
            level_json = levels[level]
            lua_path = os.path.join("Scripts", level_json.get("lua_file"))
            lua_file = dpath.util.get(files, lua_path)
            level_properties.convert(level_json, lua_file)
            print(level_json._json)
            print("----------------")
            print(lua_file._text)
            exit()


if __name__ == "__main__":
    convert_pack(sys.argv[1])
