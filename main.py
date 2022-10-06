from extended_dict import ExtendedDict
from config import CONVERTER_PREFIX
from json_file import JsonFile
from lua_file import LuaFile
import level_properties
import lua_functions
import dpath.util
import fix_utils
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


def get_lua_file(files, level_json, lua_path):
    try:
        lua_file = dpath.util.get(files, lua_path)
    except KeyError:
        # check for another file with different capitalization
        original_path = os.path.join(args.source_pack, lua_path)
        new_path_abs = fix_utils.match_capitalization(original_path)
        if new_path_abs is None:
            lua_file = LuaFile()
            lua_file.path = original_path
        else:
            lua_path = os.path.relpath(new_path_abs, args.source_pack)
            level_json["lua_file"] = lua_path[8:]
            lua_file = dpath.util.get(files, lua_path)
    return lua_file


def convert_level(files, args):
    log.info("Converting level json and lua files...")
    levels = files.get("Levels")
    level_luas = []
    for level in levels:
        level_json = levels[level]
        lua_path = os.path.join("Scripts", level_json.get("lua_file"))
        lua_file = get_lua_file(files, level_json, lua_path)
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
        lua_file.mixin_line(CONVERTER_PREFIX + "level_id=\"" + level_json["id"]
                            .replace("\n", "\\n") + "\"")
        events.convert_level(level_json, lua_file)
        level_properties.convert(level_json, lua_file)
        styles.convert_lua(lua_file, level_json)
        has_options = False
        if args.timing_options is not None:
            for options in args.timing_options:
                if level_json["id"] == options[0]:
                    options = options[1:]
                    has_options = True
                    break
        if not has_options:
            options = args.default_timing_options
        lua_file.mixin_line(CONVERTER_PREFIX + "timing_options={" +
                            str(60 / float(options[1])) + "," +
                            str(60 / float(options[2])) + "}\n" +
                            CONVERTER_PREFIX + "perf_const=" + str(options[0]))
        if level_json.get("selectable", True):
            level_json.save("Levels/" + level)
        else:
            level_json.save("Levels/" + level + ".notselectable")
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
    dict_sounds = ExtendedDict()
    for sound in sounds:
        shutil.copyfile(os.path.join(path, "Sounds", sound), "Sounds/" +
                        os.path.basename(path) + "_" + sound)
        dict_sounds[os.path.basename(path) + "_" + sound] = True
    return dict_sounds


def convert_font(path):
    os.makedirs("Fonts", exist_ok=True)
    shutil.copyfile(os.path.join(os.path.dirname(filepath), "imagine.ttf"),
                    "Fonts/imagine.ttf")


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


def convert_author(files):
    last_author = None
    for level in files.get("Levels").values():
        author = level.get("author")
        if last_author is not None:
            new_author = ""
            for i in range(len(last_author)):
                if i >= len(author):
                    break
                if author[i] != last_author[i]:
                    continue
                new_author += author[i]
            author = new_author
        last_author = author
    if author != "":
        return author
    author = None
    for level in files.get("Levels").values():
        new_authors = level.get("author").split(" & ")
        for new_author in new_authors:
            if author is None:
                author = new_author
            elif author.upper() != new_author.upper():
                if new_author.upper() not in author.upper():
                    author += " & " + new_author
    return author


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
    args.source_pack = os.path.abspath(args.source_pack)
    log.info("Parsing files in", args.source_pack + "...")
    files = get_files(args.source_pack)
    os.makedirs(args.destination_folder, exist_ok=True)
    os.chdir(args.destination_folder)
    if files.get("pack.json") is None:
        log.error("No pack.json found in", args.source_pack)
        exit(1)
    else:
        sounds = convert_sound(args.source_pack)
        level_luas = convert_level(files, args)
        lua_functions.save(sounds, all_dict_values(files["Levels"]))
        convert_event(files)
        convert_lua(files, level_luas, args.source_pack)
        convert_font(args.source_pack)
        convert_custom_lua("timeline.lua")
        convert_custom_lua("main_timeline.lua")
        convert_custom_lua("increment.lua")
        convert_custom_lua("message_timeline.lua")
        convert_custom_lua("walls.lua")
        convert_custom_lua("pulse.lua")
        convert_custom_lua("rotation.lua")
        convert_custom_lua("random.lua")
        convert_custom_lua("perfsim.lua")
        log.info("Converting styles...")
        for file in all_dict_values(files.get("Styles", {})):
            styles.convert_style(file)
            file.save(os.path.relpath(file.path, args.source_pack))
        styles.save()
        log.info("Copying Music and pack.json...")
        convert_music(all_dict_values(files.get("Music", {})),
                      args.source_pack)
        author = convert_author(files)
        if author is not None:
            log.info("Guessing author:", author)
            files["pack.json"]["author"] = author
        files["pack.json"].save(os.path.relpath(files["pack.json"].path,
                                                args.source_pack))
        for file in os.listdir(os.path.join(args.source_pack, "Music")):
            if file.endswith(".ogg"):
                shutil.copyfile(os.path.join(args.source_pack, "Music", file),
                                "Music/" + file)
        log.info("Done")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert packs for Open Hexagon 1.92 to be compatible \
        with the steam version.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("source_pack", type=str, help="the 1.92 pack to be \
                        converted")
    parser.add_argument("destination_folder", type=str, help="the path the \
                        converted pack will be created at")
    parser.add_argument("--timing-options", nargs=4, metavar=(
                            "level", "performance_level", "fps_limit_lower",
                            "fps_limit_upper"
                        ), help="set timing options for a level that may \
                        depend on it", action="append")
    parser.add_argument("--default-timing-options", nargs=3, metavar=(
                            "performance_level", "fps_limit_lower",
                            "fps_limit_upper"
                        ), help="set the default timing options",
                        default=[0.03, 240, 960])
    args = parser.parse_args()
    if not os.path.exists(args.source_pack):
        log.error("Source pack doesn't exist!")
        exit(1)
    if os.path.exists(args.destination_folder):
        log.error("Destination path exists!")
        exit(1)
    convert_pack(args)
