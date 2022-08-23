from config import CONVERTER_PREFIX
from lua_file import LuaFile


lua_timeline = LuaFile("timeline.lua")


def convert(level_lua):
    if level_lua.get_function("onUpdate") is None:
        level_lua.mixin_line("\nfunction onUpdate(frametime)\nend", line=-1)
    function_source = level_lua.get_function("onUpdate")
    parameters = function_source.split("function onUpdate(")[1].split(")")[0]
    if parameters.replace("\n", "").replace("\t", "").replace(" ", "") == "":
        function_source.replace("function onUpdate(" + parameters + ")",
                                "function onUpdate(frametime)")
    level_lua.mixin_line(CONVERTER_PREFIX + "update_timeline(" + parameters +
                         ")", "onUpdate")
    level_lua.mixin_line("u_execScript(\"" + CONVERTER_PREFIX +
                         "timeline.lua\")")
    level_lua.mixin_line("u_haltTime(-6)", "onLoad")
    if not lua_timeline.saved:
        lua_timeline.replace("prefix_", CONVERTER_PREFIX)
        lua_timeline.save("Scripts/" + CONVERTER_PREFIX + "timeline.lua")
