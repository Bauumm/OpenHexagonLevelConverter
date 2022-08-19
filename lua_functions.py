from level_properties import LEVEL_PROPERTY_MAPPING
from extended_dict import ExtendedDict
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
DIRECT_REPLACEMENTS = {
    "log": "u_log",
    "wall": "w_wall",
    "getSides": "l_getSides",
    "getSpeedMult": "u_getSpeedMultDM",
    "getDelayMult": "u_getDelayMultDM",
    "getDifficultyMult": "u_getDifficultyMult",
    "execScript": "u_execScript",
    "forceIncrement": "u_forceIncrement",
    "messageAdd": "e_messageAdd",
    "messageImportantAdd": "e_messageAddImportant",
    "isKeyPressed": "u_isKeyPressed",
    "isFastSpinning": "u_isFastSpinning",
    "wallAdj": "w_wallAdj",
    "wallAcc": "w_wallAcc"
}
CORE_FUNCTIONS = [
    "onUnload",
    "onLoad",
    "onIncrement",
    "onUpdate",
    "onStep"
]
CONVERTER_PREFIX = \
    "_converter_internal_do_not_use_unless_you_know_what_you_are_doing_"
reimplementations = LuaFile(os.path.join(os.path.dirname(__file__),
                                         "lua_functions.lua"))


def convert_lua(lua_file):
    for function, newfunction in DIRECT_REPLACEMENTS.items():
        lua_file.replace_function_calls(function, newfunction)
    lua_file.replace("math.randomseed(os.time())", "")


def convert_level_lua(level_lua, sounds):
    level_lua.mixin_line("execScript(\"" + CONVERTER_PREFIX +
                         "lua_reimplementations.lua\")")
    if level_lua.get_function("onStep") is None:
        level_lua.mixin_line("\nfunction onStep()\nend", line=-1)
    level_lua.mixin_line(CONVERTER_PREFIX + "timeline_wait_until=nil",
                         "onStep")
    convert_lua(level_lua)
    for function in CORE_FUNCTIONS:
        function_source = level_lua.get_function(function)
        if function_source is None:
            continue
        parameters = function_source \
            .split("function " + function + "(")[1] \
            .split(")")[0]
        new_source = function_source.replace(
            "function " + function + "(" + parameters + ")",
            "function " + CONVERTER_PREFIX + function + "(" + parameters + ")"
        )
        level_lua.replace(function_source, new_source)
        seperator = ", "
        if parameters \
                .replace("\n", "") \
                .replace("\t", "") \
                .replace(" ", "") == "":
            seperator = ""
        level_lua.mixin_line("function " + function + "(" + parameters + ")\n \
                             xpcall(" + CONVERTER_PREFIX + function +
                             ", print" + seperator + parameters + ")\nend",
                             line=-1)
    if not reimplementations.saved:
        reimplementations.mixin_line("SOUNDS=" + slpp.encode(sounds) + "\n")
        reimplementations.mixin_line("LEVEL_PROPERTY_MAPPING=" +
                                     LEVEL_PROPERTY_MAPPING.to_table() + "\n")
        reimplementations.mixin_line("STYLE_PROPERTY_MAPPING=" +
                                     STYLE_PROPERTY_MAPPING.to_table() + "\n")
        reimplementations.replace("_getField(", CONVERTER_PREFIX + "getField(")
        reimplementations.replace("_setField(", CONVERTER_PREFIX + "setField(")
        reimplementations.replace("LEVEL_PROPERTY_MAPPING", CONVERTER_PREFIX +
                                  "LEVEL_PROPERTY_MAPPING")
        reimplementations.replace("STYLE_PROPERTY_MAPPING", CONVERTER_PREFIX +
                                  "STYLE_PROPERTY_MAPPING")
        reimplementations.replace("SOUNDS", CONVERTER_PREFIX + "SOUNDS")
        reimplementations.replace("timeline_wait_until", CONVERTER_PREFIX +
                                  "timeline_wait_until")
        reimplementations.save("Scripts/" + CONVERTER_PREFIX +
                               "lua_reimplementations.lua")
