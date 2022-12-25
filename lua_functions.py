from level_properties import LEVEL_PROPERTY_MAPPING
from extended_dict import ExtendedDict
from config import CONVERTER_PREFIX
import fix_utils
import log
import os


# not including color objects due to 1.92 only being able to get/set strings,
# ints, floats and bools in json
STYLE_PROPERTY_MAPPING = ExtendedDict({
    "hue_min": ["s_getHueMin", "s_setHueMin"],
    "hue_max": ["s_getHueMax", "s_setHueMax"],
    "hue_ping_pong": ["s_getHuePingPong", "s_setHuePingPong"],
    "hue_increment": ["s_getHueIncrement", "s_setHueIncrement"],
    "pulse_min": ["s_getPulseMin", "s_setPulseMin"],
    "pulse_max": ["s_getPulseMax", "s_setPulseMax"],
    "pulse_increment": ["s_getPulseIncrement", "s_setPulseIncrement"],
    "3D_depth": ["s_get3dDepth", [CONVERTER_PREFIX + "style_module",
                                  "set_3D_depth"]],
    "3D_skew": ["s_get3dSkew", "s_set3dSkew"],
    "3D_pulse_min": ["s_get3dPulseMin", "s_set3dPulseMin"],
    "3D_pulse_max": ["s_get3dPulseMax", "s_set3dPulseMax"],
    "3D_pulse_speed": ["s_get3dPulseSpeed", "s_set3dPulseSpeed"],
    "3D_spacing": [
        [CONVERTER_PREFIX + "style_module", "get_3D_spacing"],
        [CONVERTER_PREFIX + "style_module", "set_3D_spacing"]
    ],
    "3D_perspective_multiplier": ["s_get3dPerspectiveMult",
                                  "s_set3dPerspectiveMult"],
    "3D_darken_multiplier": ["s_get3dDarkenMult", "s_set3dDarkenMult"],
    "3D_alpha_multiplier": ["s_get3dAlphaMult", "s_set3dAlphaMult"],
    "3D_alpha_falloff": ["s_get3dAlphaFalloff", "s_set3dAlphaFalloff"],
})
CORE_FUNCTIONS = [
    "onUnload",
    "onLoad",
    "onIncrement",
    "onUpdate",
    "onStep"
]


def convert_lua(lua_file):
    lua_file.replace("math.randomseed(os.time())", "")
    script_path = lua_file.path
    while os.path.basename(script_path) != "Scripts":
        script_path = os.path.dirname(script_path)
    for node in lua_file._get_function_call_nodes("execScript"):
        path = os.path.join(script_path, node.args[0].s)
        if not os.path.exists(path):
            path = fix_utils.match_capitalization(path)
            if path is not None:
                old = lua_file._text[node.start_char:node.stop_char + 1]
                new = "execScript(\"" + os.path.relpath(path, script_path) + \
                    "\")"
                lua_file.replace(old, new)
    onInit = lua_file.get_function("onInit")
    if onInit is not None:
        log.warn(lua_file.path, "overwrites onInit, renaming...")
        lua_file.replace(onInit, "function " + CONVERTER_PREFIX + "old_onInit()\n" +
                         lua_file.get_function("onInit", False) + "\nend")
    rename_core_functions(lua_file)
    fix_utils.fix_block_loops(lua_file)


def rename_core_functions(lua_file):
    for function in CORE_FUNCTIONS:
        lua_file.replace_assigns(function, CONVERTER_PREFIX + function)
        lua_file.replace_function_calls(function, CONVERTER_PREFIX + function)
        function_source = lua_file.get_function(function)
        if function_source is None:
            continue
        actual_name = function_source \
            .split("function")[1] \
            .split("(")[0]
        new_source = function_source.replace(
            "function" + actual_name + "(",
            "function " + CONVERTER_PREFIX + function + "("
        )
        lua_file.replace(function_source, new_source)


def convert_level_lua(level_lua):
    level_lua.mixin_line("u_execScript(\"" + CONVERTER_PREFIX +
                         "packdata.lua\")")
    convert_lua(level_lua)


def save(packdata, sounds, level_jsons, quiet):
    packdata.mixin_line(CONVERTER_PREFIX + "SOUNDS=" + sounds.to_table() + "\n"
                        + CONVERTER_PREFIX + "LEVEL_PROPERTY_MAPPING=" +
                        LEVEL_PROPERTY_MAPPING.to_table() + "\n" +
                        CONVERTER_PREFIX + "STYLE_PROPERTY_MAPPING=" +
                        STYLE_PROPERTY_MAPPING.to_table() + "\n", line=1)
    code = ""
    for level_json in level_jsons:
        lua_file = level_json["luaFile"][8:]
        level_json.reset()
        level_json[CONVERTER_PREFIX + "lua_file"] = lua_file
        # Trust levels not to check for this cuz strings are pain
        level_json.delete("events")
        for prop in level_json:
            if type(level_json[prop]) == str:
                level_json[prop] = level_json[prop].replace("\\", "\\\\") \
                    .replace("\n", "\\n").replace("\t", "\\t") \
                    .replace("\r", "\\r")
        code += "_G[\"" + CONVERTER_PREFIX + "level_json_" + level_json["id"] \
            + "\"]=" + level_json.to_table() + "\n"
    code += CONVERTER_PREFIX + "quiet=" + str(quiet).lower() + "\n"
    packdata.mixin_line(code, line=1)
