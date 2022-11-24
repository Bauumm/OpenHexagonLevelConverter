from extended_dict import ExtendedDict
from config import CONVERTER_PREFIX
from base_file import BaseFile
from lua_file import LuaFile
import os


COLOR_OBJECTS = [
    "main",
    "player_color",
    "text_color",
    "wall_color"
]

filepath = os.path.realpath(__file__)
colors3D = ExtendedDict()


def ensure_item_count(items, count=4, default=0):
    length = len(items)
    if length > 4:
        return items[:4]
    elif length < 4:
        while len(items) < 4:
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

    if color["dynamic"] and color["dynamic_offset"] and not color["main"] and \
       color["offset"] == 0:
        # If these values are set this way the original color is due to
        # division by 0 which results in inf being added to the main color
        # (except for the alpha component) reset to black
        for i in range(3):
            color["value"][i] = 0
    # Let pulse values underflow/overflow like in 1.92
    if color.get("pulse") is not None:
        for i in range(4):
            color["pulse"][i] %= 256
    return color


def convert_style(style_json):
    for color in COLOR_OBJECTS:
        if color in style_json:
            style_json[color] = convert_color(style_json[color])
    has_none = False
    no_colors = True
    for i in range(len(style_json.get("colors", []))):
        no_colors = False
        if style_json["colors"][i] is None:
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

    # This way the first 3D layer is rendered inside the main layer just like
    # in 1.92
    style_json["3D_layer_offset"] = -1

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
    os.makedirs("Scripts/" + CONVERTER_PREFIX + "Styles", exist_ok=True)
    lua_file = LuaFile()
    lua_file.set_text(CONVERTER_PREFIX + "style=" + style_json.to_table())
    lua_file.save("Scripts/" + CONVERTER_PREFIX + "Styles/" +
                  style_json["id"] + ".lua")

    # Save it now for use in menu
    style_json["id"] += "-menu"
    style_json.save("Styles/" + os.path.basename(style_json.path)[:-5] +
                    "-menu.json")
    style_json.saved = False
    style_json["id"] = style_json["id"][:-5]

    # Set some properties to fixed values in order to remake them with lua
    style_json["3D_override_color"] = [0, 0, 0, 255]
    style_json["pulse_increment"] = 0
    style_json["pulse_min"] = 0
    style_json["pulse_max"] = 0
    style_json["hue_increment"] = 0
    style_json["hue_min"] = 0
    style_json["hue_max"] = 0
    style_json["max_swap_time"] = 0
    style_json["text_color"] = {
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
    code = "const ColorData colors[] = ColorData[" + str(i + 1) + "](\n"
    for i in range(len(style_json.get("colors", []))):
        color_data = style_json["colors"][i]
        code += "\tColorData(" + ", ".join([
            str(color_data["dynamic"]).lower(),
            str(color_data["dynamic_darkness"]),
            str(color_data["dynamic_offset"]).lower(),
            str(color_data["offset"]),
            str(color_data["main"]).lower(),
            "vec4" + "(" +
            ", ".join([str(f / 255) for f in color_data["value"]]) + ")",
            "vec4" + "(" +
            ", ".join([str(f / 255) for f in color_data["pulse"]]) + ")",
            str(color_data["hue_shift"])
        ]) + "),\n"
        style_json["colors"][i]["value"] = [14, *i.to_bytes(3, 'big')]
        style_json["colors"][i]["pulse"] = [0, 0, 0, 0]
        style_json["colors"][i]["dynamic"] = False
    code = code[:-2] + "\n);\n\n"
    os.makedirs("Shaders", exist_ok=True)
    background_shader = BaseFile(
        os.path.join(os.path.dirname(filepath), "background.frag"))
    background_shader.mixin_line(code, 19)
    background_shader.save("Shaders/" + style_json["id"] + "-background.frag")


def convert_lua(level_lua, level_json):
    level_lua.mixin_line(CONVERTER_PREFIX + "style_id=\"" +
                         level_json["styleId"] + "\"", "onInit")
    level_json["styleId"] += "-menu"
