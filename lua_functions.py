from level_properties import LEVEL_PROPERTY_MAPPING
from extended_dict import ExtendedDict
from config import CONVERTER_PREFIX
from lua_file import LuaFile
from slpp import slpp
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
    "3D_depth": ["s_get3dDepth", "s_set3dDepth"],
    "3D_skew": ["s_get3dSkew", "s_set3dSkew"],
    "3D_pulse_min": ["s_get3dPulseMin", "s_set3dPulseMin"],
    "3D_pulse_max": ["s_get3dPulseMax", "s_set3dPulseMax"],
    "3D_pulse_speed": ["s_get3dPulseSpeed", "s_set3dPulseSpeed"],
    "3D_spacing": ["s_get3dSpacing", "s_set3dSpacing"],
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
lua_functions = LuaFile(os.path.join(os.path.dirname(__file__),
                                     "lua_functions.lua"))
core_wrapper = LuaFile(os.path.join(os.path.dirname(__file__),
                                    "core_wrapper.lua"))


def convert_lua(lua_file):
    lua_file.replace("math.randomseed(os.time())", "")
    rename_core_functions(lua_file)


def rename_core_functions(lua_file):
    for function in CORE_FUNCTIONS:
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
                         "core_wrapper.lua\")")
    convert_lua(level_lua)


def save(sounds):
    lua_functions.mixin_line(CONVERTER_PREFIX + "SOUNDS=" + slpp.encode(sounds)
                             + "\n" + CONVERTER_PREFIX +
                             "LEVEL_PROPERTY_MAPPING=" +
                             LEVEL_PROPERTY_MAPPING.to_table() + "\n" +
                             CONVERTER_PREFIX + "STYLE_PROPERTY_MAPPING=" +
                             STYLE_PROPERTY_MAPPING.to_table() + "\n")
    lua_functions.replace("prefix_", CONVERTER_PREFIX)
    lua_functions.save("Scripts/" + CONVERTER_PREFIX + "lua_functions.lua")
    core_wrapper.replace("prefix_", CONVERTER_PREFIX)
    core_wrapper.save("Scripts/" + CONVERTER_PREFIX + "core_wrapper.lua")
