from json_file import JsonFile
from lua_file import LuaFile
import level_properties
import lua_functions
import dpath.util
import timeline
import shutil
import events
import styles
import log
import sys
import os


def all_dict_values(dictionary):
    for value in dictionary.values():
        if type(value) == dict:
            for new_value in all_dict_values(value):
                yield new_value
        else:
            yield value


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


def convert_level(files, sounds):
    log.info("Converting level json and lua files...")
    levels = files.get("Levels")
    level_luas = []
    for level in levels:
        level_json = levels[level]
        lua_path = os.path.join("Scripts", level_json.get("lua_file"))
        lua_file = dpath.util.get(files, lua_path)
        if lua_file.saved and level_json.saved:
            continue
        if lua_file.saved and not level_json.saved:
            # There is a 2nd level using the same lua file, so since level
            # parameters have been moved into lua, a new lua file needs to
            # be created
            lua_file = LuaFile(lua_file.path)
            count = 0
            while True:
                lua_path = lua_path[:-4] + str(count) + ".lua"
                count += 1
                try:
                    dpath.util.get(files, lua_path)
                except KeyError:
                    break
            dpath.util.new(files, lua_path, lua_file)
            level_json["lua_file"] = lua_path
            log.info("Created", lua_path, "due to", level_json.path,
                     "reusing the script.")
        level_luas.append(lua_file.path)
        events.convert_level(level_json, lua_file)
        level_properties.convert(level_json, lua_file)
        lua_functions.convert_level_lua(lua_file, sounds)
        timeline.convert(lua_file)
        level_json.save("Levels/" + level)
        lua_file.save(lua_path)
    return level_luas


def convert_sound(path):
    sounds = []
    try:
        sounds = os.listdir(os.path.join(path, "Sounds"))
        log.info("Processing custom sounds...")
    except FileNotFoundError:
        pass
    if len(sounds) > 0:
        os.makedirs("Sounds", exist_ok=True)
    for sound in sounds:
        shutil.copyfile(os.path.join(path, "Sounds", sound), "Sounds/" + sound)
    return sounds


def convert_event(files):
    event_files = files.get("Events")
    if event_files is not None:
        log.info("Converting Events...")
        for event in event_files:
            events.convert_external(event_files[event])
    events.save()


def convert_lua(files, level_luas, path):
    log.info("Converting other lua files...")
    scripts = files.get("Scripts")
    if scripts is not None:
        for script in all_dict_values(scripts):
            if script.path not in level_luas:
                lua_functions.convert_lua(script)
                script.save(os.path.relpath(script.path, path))


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
        sounds = convert_sound(path)
        level_luas = convert_level(files, sounds)
        convert_event(files)
        convert_lua(files, level_luas, path)
        log.info("Converting styles")
        for file in all_dict_values(files.get("Styles", {})):
            styles.convert(file)
            file.save(os.path.relpath(file.path, path))
        log.info("Copying Music and pack.json...")
        copy_files = [*all_dict_values(files.get("Music", {})),
                      files.get("pack.json")]
        for file in copy_files:
            file.save(os.path.relpath(file.path, path))
        for file in os.listdir(os.path.join(path, "Music")):
            if not file.endswith(".json"):
                shutil.copyfile(os.path.join(path, "Music", file),
                                "Music/" + file)
        log.info("Done")


if __name__ == "__main__":
    convert_pack(sys.argv[1], sys.argv[2])
