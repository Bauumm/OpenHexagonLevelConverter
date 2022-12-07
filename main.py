from config import CONVERTER_PREFIX, DISAMBIGUATOR
from extended_dict import ExtendedDict
from json_file import JsonFile
from lua_file import LuaFile
import level_properties
import lua_functions
import dpath.util
import luaparser
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
    misc = []
    for file in os.listdir(folder):
        path = os.path.join(folder, file)
        if os.path.isdir(path):
            structure[file], extra = get_files(path)
            for path in extra:
                misc.append(path)
        else:
            parent_folder = os.path.basename(os.path.dirname(path))
            if (path.endswith(".json") or parent_folder == "Events") and \
                    parent_folder != "Scripts":
                structure[file] = JsonFile(path)
            elif path.endswith(".lua"):
                try:
                    structure[file] = LuaFile(path)
                except Exception as error:
                    log.warn("Lua file:", path, "failed to parse:", error)
            else:
                misc.append(path)
    return structure, misc


def get_lua_file(files, level_json, lua_path, args):
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
        lua_file = get_lua_file(files, level_json, lua_path, args)
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
        pack_name = os.path.basename(args.source_pack)
        level_json["id"] = CONVERTER_PREFIX + pack_name + "_" + level_json["id"]
        if level_json.get("selectable", True):
            level_json.save("Levels/" + level)
        else:
            level_json.save("Levels/" + level + ".notselectable")
        level_json["id"] = level_json["id"][len(CONVERTER_PREFIX) + len(pack_name) + 1:]
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


def convert_event(files):
    event_files = files.get("Events")
    if event_files is not None:
        log.info("Converting Events...")
        for event in event_files:
            events.convert_external(event_files[event])


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
            if music["segments"][i] is None or "time" not in music["segments"][i]:
                del music["segments"][i]
                continue
            music["segments"][i]["time"] = int(music["segments"][i]["time"])
        music.save(os.path.relpath(music.path, path))


def convert_pack(args):
    args.source_pack = os.path.abspath(args.source_pack)
    log.info("Parsing files in", args.source_pack + "...")
    files, misc_files = get_files(args.source_pack)
    os.makedirs(args.destination_folder, exist_ok=True)
    os.chdir(args.destination_folder)
    if files.get("pack.json") is None:
        log.error("No pack.json found in", args.source_pack)
        exit(1)
    else:
        sounds = convert_sound(args.source_pack)
        level_luas = convert_level(files, args)
        packdata = LuaFile(os.path.join(os.path.dirname(filepath),
                                        "packdata.lua"))
        packdata.replace("prefix_", CONVERTER_PREFIX)
        packdata.mixin_line(CONVERTER_PREFIX + "DISAMBIGUATOR=\"" + DISAMBIGUATOR +
                            "\"")
        lua_functions.save(packdata, sounds, all_dict_values(files["Levels"]),
                           args.quiet)
        convert_event(files)
        convert_lua(files, level_luas, args.source_pack)
        log.info("Converting styles...")
        for file in all_dict_values(files.get("Styles", {})):
            styles.convert_style(file)
            file.save(os.path.relpath(file.path, args.source_pack))
        log.info("Copying Music and misc files...")
        convert_music(all_dict_values(files.get("Music", {})), args.source_pack)
        for path in misc_files:
            dst_path = os.path.relpath(path, args.source_pack)
            if os.path.dirname(dst_path) != "":
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            shutil.copyfile(path, dst_path)
        log.info("Adjusting pack.json...")
        for key in files["pack.json"]:
            str_val = str(files["pack.json"][key])
            if str_val.endswith("inf"):
                files["pack.json"][key] = int(str_val.replace(
                    "inf", "9999999999999999999999999999999999999999"
                ))
        files["pack.json"]["disambiguator"] = DISAMBIGUATOR
        files["pack.json"]["author"] = DISAMBIGUATOR
        files["pack.json"]["dependencies"] = [{
            "disambiguator": DISAMBIGUATOR,
            "name": "192_runtime",
            "author": "Baum",
            "min_version": 1
        }]
        files["pack.json"].save(os.path.relpath(files["pack.json"].path,
                                                args.source_pack))
        log.info("Done")


def convert_runtime(args):
    runtime_path = os.path.join(os.path.dirname(filepath), "192_runtime")
    shutil.copytree(runtime_path, args.destination_folder)

    def convert_dir(path):
        for filename in os.listdir(path):
            filename = os.path.join(path, filename)
            if os.path.isdir(filename):
                convert_dir(filename)
            else:
                with open(filename, "r") as lua_file:
                    content = lua_file.read()
                with open(filename, "w") as lua_file:
                    lua_file.write(content.replace("prefix_", CONVERTER_PREFIX)
                                   )

    convert_dir(os.path.join(args.destination_folder, "Scripts"))
    pack = JsonFile(os.path.join(args.destination_folder, "pack.json"))
    pack["disambiguator"] = DISAMBIGUATOR
    pack.save(os.path.join(args.destination_folder, "pack.json"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert packs for Open Hexagon 1.92 to be compatible \
        with the steam version."
    )
    sub_parsers = parser.add_subparsers(dest="command")
    pack_parser = sub_parsers.add_parser("convert-pack",
                                         help="converts a pack",
                                         formatter_class=argparse.
                                         ArgumentDefaultsHelpFormatter)
    pack_parser.add_argument("source_pack", type=str, help="the 1.92 pack to \
                             be converted")
    pack_parser.add_argument("destination_folder", type=str, help="the path \
                             the converted pack will be created at")
    pack_parser.add_argument("--timing-options", nargs=4, metavar=(
                                "level", "performance_level",
                                "fps_limit_lower", "fps_limit_upper"
                            ), help="set timing options for a level that may \
                                    depend on it", action="append")
    pack_parser.add_argument("--default-timing-options", nargs=3, metavar=(
                                "performance_level", "fps_limit_lower",
                                "fps_limit_upper"
                            ), help="set the default timing options",
                            default=[0.03, 240, 960])
    pack_parser.add_argument("--quiet", action="store_true", help="with this \
                             option converted packs will not print out error \
                             messages from the original lua")
    lib_parser = sub_parsers.add_parser("convert-runtime", help="converts the \
                                        192_runtime to use the correct prefix")
    lib_parser.add_argument("destination_folder", type=str, help="the path \
                            the converted pack will be created at")
    args = parser.parse_args()
    if os.path.exists(args.destination_folder):
        log.error("Destination path exists!")
        exit(1)
    if args.command == "convert-pack":
        if not os.path.exists(args.source_pack):
            log.error("Source pack doesn't exist!")
            exit(1)
        convert_pack(args)
    elif args.command == "convert-runtime":
        convert_runtime(args)
