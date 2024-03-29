from extended_dict import ExtendedDict
from config import CONVERTER_PREFIX
from lua_file import LuaFile
import json
import log
import os


COLOR_OBJECTS = [
    "main",
    "player_color",
    "text_color",
    "wall_color"
]

CALCULATION_METHODS = [
    {"dynamic": False},
    {"dynamic": True, "main": True},
    {"dynamic": True, "main": False, "dynamic_offset": True, "offset": 0},
    {"dynamic": True, "main": False, "dynamic_offset": True},
    {"dynamic": True, "main": False, "dynamic_offset": False, "dynamic_darkness": 0},
    {"dynamic": True, "main": False, "dynamic_offset": False}
]

filepath = os.path.realpath(__file__)
colors3D = ExtendedDict()
id_file_mapping = ExtendedDict()


def ensure_item_count(items, count=4, default=0):
    if not isinstance(items, list):
        items = [items]
    length = len(items)
    if length > count:
        return items[:count]
    elif length < count:
        while len(items) < count:
            items.append(default)
    return items


def convert_color(color):
    # Set defaults to not get unexpected nils in lua
    color["dynamic"] = color.get("dynamic", False)
    color["dynamic_darkness"] = color.get("dynamic_darkness", 0)
    color["dynamic_offset"] = color.get("dynamic_offset", False)
    color["offset"] = color.get("offset", 0)
    color["main"] = color.get("main", False)
    color["value"] = ensure_item_count(color.get("value", [0, 0, 0, 0]))
    color["pulse"] = ensure_item_count(color.get("pulse", [0, 0, 0, 0]))
    color["hue_shift"] = color.get("hue_shift", 0)

    calculation_method = 0
    for method in CALCULATION_METHODS:
        calculation_method += 1
        got_match = True
        for key in method:
            if method[key] != color[key]:
                got_match = False
        if got_match:
            break
    color["calculation_method"] = calculation_method

    if color["dynamic"] and color["dynamic_offset"] and not color["main"] and \
       color["offset"] == 0:
        # If these values are set this way the original color is due to division by 0
        # which results in inf being added to the main color (except for the alpha
        # component) reset to black
        for i in range(3):
            color["value"][i] = 0
    # Let pulse values underflow/overflow like in 1.92
    if color.get("pulse") is not None:
        for i in range(4):
            color["pulse"][i] %= 256
    for i in range(4):
        color["value"][i] %= 256
    return color


def convert_style(style_json):
    if style_json.get("id") is None:
        log.error("Style file", style_json.path, "has no id!")
        return
    for color in COLOR_OBJECTS:
        if color in style_json:
            style_json[color] = convert_color(style_json[color])
    has_none = False
    no_colors = True
    for i in range(len(style_json.get("colors", []))):
        no_colors = False
        if not isinstance(style_json["colors"][i], dict):
            del style_json["colors"][i]
            has_none = True
        else:
            style_json["colors"][i] = convert_color(style_json["colors"][i])

    # Limit depth to 100 like 1.92 does with unmodified config
    depth = style_json.get("3D_depth", 15)
    if depth < 0:
        depth = 0
    if depth > 100:
        depth = 100
    style_json["3D_depth"] = depth

    # Divide 3D_spacing by 1.4 because the steam version multiplies it by 1.4
    style_json["3D_spacing"] = style_json.get("3D_spacing", 1) / 1.4

    # This way the first 3D layer is rendered inside the main layer just like in 1.92
    style_json["3D_layer_offset"] = -1
    style_json["3D_alpha_mirror"] = True

    # 1.92 casts float depths to int while the steam version just crashes
    style_json["3D_depth"] = int(style_json["3D_depth"])

    # Set defaults
    style_json["max_swap_time"] = style_json.get("max_swap_time", 100)
    style_json["3D_pulse_speed"] = style_json.get("3D_pulse_speed", 0.01)
    style_json["3D_pulse_min"] = style_json.get("3D_pulse_min", 0)
    style_json["3D_pulse_max"] = style_json.get("3D_pulse_max", 3.2)
    style_json["pulse_min"] = style_json.get("pulse_min", 0)
    style_json["pulse_max"] = style_json.get("pulse_max", 0)
    style_json["pulse_increment"] = style_json.get("pulse_increment", 0)
    style_json["hue_min"] = style_json.get("hue_min", 0)
    style_json["hue_max"] = style_json.get("hue_max", 0)
    style_json["hue_ping_pong"] = style_json.get("hue_ping_pong", False)
    style_json["hue_increment"] = style_json.get("hue_increment", 0)

    # Save style for use in lua
    filename = os.path.basename(style_json.path)[:-5]
    id_file_mapping[style_json["id"]] = filename
    os.makedirs("Scripts/" + CONVERTER_PREFIX + "Styles", exist_ok=True)
    lua_file = LuaFile()
    lua_file.set_text(CONVERTER_PREFIX + "style=" + style_json.to_table())
    lua_file.save("Scripts/" + CONVERTER_PREFIX + "Styles/" + filename + ".lua")

    # Save it now for use in menu
    menu_style = style_json.copy()
    # Make styles with weird hues look correct most of the time (workaround for menu)
    if menu_style["hue_min"] < 0 and menu_style["hue_max"] <= 0:
        for color in [*menu_style.get("colors", []), menu_style["main"]]:
            if color["dynamic"] and color["hue_shift"] == 0:
                color["dynamic"] = False
                color["value"] = [0, 0, 0, 0]
    menu_style["id"] += "-menu"
    os.makedirs("Styles", exist_ok=True)
    with open("Styles/" + filename + "-menu.json", "w") as menu_style_file:
        json.dump(menu_style, menu_style_file, indent=4)

    # Set some properties to fixed values in order to remake them with lua
    style_json["3D_override_color"] = [0, 0, 0, 0]
    style_json["pulse_increment"] = 0
    style_json["pulse_min"] = 0
    style_json["pulse_max"] = 0
    style_json["hue_increment"] = 0
    style_json["hue_min"] = 0
    style_json["hue_max"] = 0
    style_json["max_swap_time"] = 0
    for name in "text_color", "main":
        style_json[name] = {
            "dynamic": False,
            "dynamic_offset": False,
            "dynamic_darkness": 1,
            "offset": 0,
            "main": False,
            "hue_shift": 0,
            "value": [0, 0, 0, 0],
            "pulse": [0, 0, 0, 0]
        }
    style_json["cap_color"] = {
        "legacy": False,
        "dynamic": False,
        "dynamic_offset": False,
        "dynamic_darkness": 1,
        "offset": 0,
        "main": False,
        "hue_shift": 0,
        "value": [0, 0, 0, 0],
        "pulse": [0, 0, 0, 0]
    }
    if "main" in style_json:
        style_json["main"]["dynamic"] = False
    if has_none:
        i -= 1
    if no_colors:
        i = 0
        style_json["colors"] = [{
            "dynamic": False,
            "dynamic_offset": False,
            "dynamic_darkness": 1,
            "offset": 0,
            "main": False,
            "hue_shift": 0,
            "value": [0, 0, 0, 0],
            "pulse": [0, 0, 0, 0]
        }]
    for i in range(len(style_json.get("colors", []))):
        style_json["colors"][i]["value"] = [0, 0, 0, 0]
        style_json["colors"][i]["pulse"] = [0, 0, 0, 0]
        style_json["colors"][i]["dynamic"] = False


def convert_lua(level_lua, level_json):
    level_lua.mixin_line(CONVERTER_PREFIX + "style_id=\"" + level_json["styleId"] +
                         "\"", CONVERTER_PREFIX + "onInit")
    level_json["styleId"] += "-menu"


def save(packdata):
    packdata.mixin_line(CONVERTER_PREFIX + "STYLE_ID_FILE_MAPPING=" + id_file_mapping
                        .to_table(), line=1)
    packdata.save("Scripts/" + CONVERTER_PREFIX + "packdata.lua")
