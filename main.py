from json_file import JsonFile
from lua_file import LuaFile
import level_properties
import lua_functions
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


def convert_pack(path, newpath):
    path = os.path.abspath(path)
    log.info("Parsing files...")
    files = get_files(path)
    os.makedirs(newpath, exist_ok=True)
    os.chdir(newpath)
    if files.get("pack.json") is None:
        log.error("No pack.json found in", path)
        exit(1)
    else:
        levels = files.get("Levels")
        level_luas = []
        log.info("Converting level json and lua files...")
        for level in levels:
            level_json = levels[level]
            lua_path = os.path.join("Scripts", level_json.get("lua_file"))
            lua_file = dpath.util.get(files, lua_path)
            level_luas.append(lua_file.path)
            level_properties.convert(level_json, lua_file)
            lua_functions.convert_level_lua(lua_file)
            level_json.save("Levels/" + level)
            lua_file.save(lua_path)
        scripts = files.get("Scripts")
        log.info("Converting other lua files...")
        if scripts is not None:
            def convert_scripts(script_files):
                for script in script_files.values():
                    if type(script) == dict:
                        convert_scripts(script)
                        continue
                    if script.path in level_luas:
                        continue
                    lua_functions.convert_lua(script)
                    script.save(os.path.relpath(script.path, path))
            convert_scripts(scripts)
        log.info("Copying Music and Styles and pack.json...")
        copy_files = [*files.get("Music", {}).values(),
                      *files.get("Styles", {}).values(),
                      files.get("pack.json")]
        for file in copy_files:
            file.save(os.path.relpath(file.path, path))
        log.info("Done")


if __name__ == "__main__":
    convert_pack(sys.argv[1], sys.argv[2])
