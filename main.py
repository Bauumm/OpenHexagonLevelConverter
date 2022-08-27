from config import CONVERTER_PREFIX
from json_file import JsonFile
from lua_file import LuaFile
import level_properties
import lua_functions
import dpath.util
import argparse
import shutil
import events
import styles
import log
import os


filepath = os.path.realpath(__file__)


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


def convert_level(files, args):
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
            level_json["lua_file"] = lua_path[8:]
            log.info("Created", lua_path, "due to", level_json.path,
                     "reusing the script.")
        level_luas.append(lua_file.path)
        lua_functions.convert_level_lua(lua_file)
        events.convert_level(level_json, lua_file)
        level_properties.convert(level_json, lua_file)
        styles.convert_lua(lua_file, level_json)
        if args.fps_limit is not None:
            for fps_limit in args.fps_limit:
                if level_json["id"] == fps_limit[0]:
                    lua_file.mixin_line(CONVERTER_PREFIX + "limit_fps=" +
                                        str(fps_limit[1]))
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


def convert_custom_lua(name):
    lua_file = LuaFile(os.path.join(os.path.dirname(filepath), name))
    lua_file.replace("prefix_", CONVERTER_PREFIX)
    lua_file.save("Scripts/" + CONVERTER_PREFIX + name)


def convert_music(music_files, path):
    for music in music_files:
        for i in range(len(music.get("segments", []))):
            if music["segments"][i] is None:
                del music["segments"][i]
                continue
            music["segments"][i]["time"] = int(music["segments"][i]["time"])
        music.save(os.path.relpath(music.path, path))


def convert_pack(args):
    path = os.path.abspath(args.source_pack)
    log.info("Parsing files...")
    files = get_files(path)
    os.makedirs(args.destination_folder, exist_ok=True)
    os.chdir(args.destination_folder)
    if files.get("pack.json") is None:
        log.error("No pack.json found in", path)
        exit(1)
    else:
        sounds = convert_sound(path)
        level_luas = convert_level(files, args)
        lua_functions.save(sounds, all_dict_values(files["Levels"]))
        convert_event(files)
        convert_lua(files, level_luas, path)
        convert_custom_lua("timeline.lua")
        convert_custom_lua("increment.lua")
        convert_custom_lua("message_timeline.lua")
        convert_custom_lua("walls.lua")
        log.info("Converting styles...")
        for file in all_dict_values(files.get("Styles", {})):
            styles.convert_style(file)
            file.save(os.path.relpath(file.path, path))
        styles.save()
        log.info("Copying Music and pack.json...")
        convert_music(all_dict_values(files.get("Music", {})), path)
        files["pack.json"].save(os.path.relpath(files["pack.json"].path, path))
        for file in os.listdir(os.path.join(path, "Music")):
            if file.endswith(".ogg"):
                shutil.copyfile(os.path.join(path, "Music", file),
                                "Music/" + file)
        log.info("Done")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert packs for Open \
                                     Hexagon 1.92 to be compatible with the \
                                     steam version.")
    parser.add_argument("source_pack", type=str, help="the 1.92 pack to be \
                        converted")
    parser.add_argument("destination_folder", type=str, help="the path the \
                        converted pack will be created at")
    parser.add_argument("--fps-limit", nargs=2, metavar=("level", "fps_limit"),
                        help="limit fps for a level that may depend on it",
                        action="append")
    args = parser.parse_args()
    if not os.path.exists(args.source_pack):
        log.error("Source pack doesn't exist!")
    if os.path.exists(args.destination_folder):
        log.error("Destination path exists!")
    convert_pack(args)
