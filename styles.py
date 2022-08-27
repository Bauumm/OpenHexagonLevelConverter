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
    # set dynamic_darkness to 0 by default
    color["dynamic_darkness"] = color.get("dynamic_darkness", 0)
    if color.get("dynamic", False) and \
       color.get("dynamic_offset", False) and \
       not color.get("main", False) and \
       color.get("offset", 0) == 0:
        # If these values are set this way the original color is due to
        # division by 0 which results in inf being added to the main color
        # (except for the alpha component) reset to black
        for i in range(3):
            color["value"][i] = 0
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

    # save fixed 3D override colors for use in lua
    color = style_json.get("3D_override_color")
    if color is not None:
        colors3D[style_json["id"]] = color
    style_json["3D_override_color"] = [0, 0, 0, 255]

    # Limit depth to 100 like 1.92 does with unmodified config and subtract 1
    # because the steam version adds one too much
    depth = style_json.get("3D_depth", 15) - 1
    if depth < 0:
        depth = 0
    if depth > 100:
        depth = 100
    style_json["3D_depth"] = depth

    # Divide 3D_spacing by 1.4 because the steam version multiplies it by 1.4
    style_json["3D_spacing"] = style_json.get("3D_spacing", 1) / 1.4


def convert_lua(level_lua, level_json):
    level_lua.mixin_line(CONVERTER_PREFIX + "current_style=\"" +
                         level_json["styleId"] + "\"", "onInit")
    # 3D alpha falloff overflow reimplementation using shaders
    if not os.path.exists("Shaders/" + CONVERTER_PREFIX + "wall3D.frag"):
        os.makedirs("Shaders")
        shutil.copyfile(os.path.join(os.path.dirname(filepath), "wall3D.frag"),
                        "Shaders/" + CONVERTER_PREFIX + "wall3D.frag")


def save():
    styles_lua.replace("prefix_", CONVERTER_PREFIX)
    styles_lua.mixin_line(CONVERTER_PREFIX + "3D_colors=" +
                          colors3D.to_table())
    styles_lua.save("Scripts/" + CONVERTER_PREFIX + "styles.lua")
