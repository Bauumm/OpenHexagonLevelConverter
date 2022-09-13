from extended_dict import ExtendedDict
from config import CONVERTER_PREFIX
from lua_file import LuaFile
import shutil
import os


COLOR_OBJECTS = [
    "main",
    "player_color",
    "text_color",
    "wall_color"
]

styles_lua = LuaFile(os.path.join(os.path.dirname(__file__), "styles.lua"))
filepath = os.path.realpath(__file__)
colors3D = ExtendedDict()


def convert_color(color):
    # Set defaults
    color["dynamic"] = color.get("dynamic", False)
    color["dynamic_darkness"] = color.get("dynamic_darkness", 0)
    color["dynamic_offset"] = color.get("dynamic_offset", False)
    color["offset"] = color.get("offset", 0)
    color["main"] = color.get("main", False)
    color["value"] = color.get("value", [0, 0, 0, 0])
    color["pulse"] = color.get("pulse", [0, 0, 0, 0])
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
            color["pulse"][i] = color["pulse"][i] % 256
    return color


def convert_style(style_json):
    for color in COLOR_OBJECTS:
        if color in style_json:
            style_json[color] = convert_color(style_json[color])
    for i in range(len(style_json.get("colors", []))):
        if style_json["colors"][i] is None:
            del style_json["colors"][i]
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

    # Save style for use in lua
    os.makedirs("Scripts/" + CONVERTER_PREFIX + "Styles", exist_ok=True)
    lua_file = LuaFile()
    lua_file.set_text(CONVERTER_PREFIX + "style=" + style_json.to_table())
    lua_file.save("Scripts/" + CONVERTER_PREFIX + "Styles/" +
                  style_json["id"] + ".lua")

    # Set some properties to fixed values in order to remake them with lua
    style_json["3D_override_color"] = [0, 0, 0, 255]


def convert_lua(level_lua, level_json):
    level_lua.mixin_line(CONVERTER_PREFIX + "style_id=\"" +
                         level_json["styleId"] + "\"", "onInit")
    if not os.path.exists("Shaders/" + CONVERTER_PREFIX + "wall3D.frag"):
        os.makedirs("Shaders")
        # 3D alpha falloff overflow reimplementation using shaders
        shutil.copyfile(os.path.join(os.path.dirname(filepath), "wall3D.frag"),
                        "Shaders/" + CONVERTER_PREFIX + "wall3D.frag")
        # more efficient way to set colors
        shutil.copyfile(os.path.join(os.path.dirname(filepath), "solid.frag"),
                        "Shaders/" + CONVERTER_PREFIX + "solid.frag")


def save():
    styles_lua.replace("prefix_", CONVERTER_PREFIX)
    styles_lua.save("Scripts/" + CONVERTER_PREFIX + "styles.lua")
