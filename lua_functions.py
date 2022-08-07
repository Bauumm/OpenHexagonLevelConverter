DIRECT_REPLACEMENTS = {
    "log": "u_log",
    "wall": "w_wall",
    "getSides": "l_getSides",
    "getSpeedMult": "l_getSpeedMult",
    "getDelayMult": "l_getDelayMult",
    "getDifficultyMult": "u_getDifficultyMult",
    "execScript": "u_execScript",
    "wait": "t_wait",
    "playSound": "u_playSound",
    "forceIncrement": "u_forceIncrement",
    "messageAdd": "e_messageAdd",
    "messageImportantAdd": "e_messageAddImportant",
    "isKeyPressed": "u_isKeyPressed",
    "isFastSpinning": "u_isFastSpinning",
    "wallAdj": "w_wallAdj",
    "wallAcc": "w_wallAcc"
}
VAR_PREFIX = "_converter_internal_variable_do_not_use_"


# has to be called before level property conversion
def convert(level_json, style_json, lua_file):
    lua_file.mixin_line(VAR_PREFIX + "level_json=" + level_json.to_table())
    lua_file.mixin_line(VAR_PREFIX + "style_json=" + style_json.to_table())
    for function, newfunction in DIRECT_REPLACEMENTS.items():
        lua_file.replace_function_calls(function, newfunction)
    # TODO: Add Implementations for level and style property getters and
    #        setters which will need to compromise in some places

# unhandled:
#   execEvent
#   enqueueEvent
#   getLevelValueInt
#   getLevelValueFloat
#   getLevelValueString
#   getLevelValueBool
#   setLevelValueInt
#   setLevelValueFloat
#   setLevelValueString
#   setLevelValueBool
#   getStyleValueInt
#   getStyleValueFloat
#   getStyleValueString
#   getStyleValueBool
#   setStyleValueInt
#   setStyleValueFloat
#   setStyleValueString
#   setStyleValueBool
