from extended_dict import ExtendedDict
from config import CONVERTER_PREFIX
from lua_file import LuaFile
import fix_utils
import log
import os


EVENT_TYPES = {
    "level_change": CONVERTER_PREFIX + "change_level(\"<id>\")",
    "menu": "e_kill()",  # There is no way to exit to menu in steam version
    "message_add": "messageAdd(\"<message>\", <duration>)",
    "message_important_add":
        "messageImportantAdd(\"<message>\", <duration>)",
    "message_clear": "e_messageAddImportantSilent(\"\", 0)",
    "time_stop": CONVERTER_PREFIX + "time_stop = <duration>",
    "timeline_wait": "wait(<duration>)",
    "timeline_clear": CONVERTER_PREFIX + "clear_and_reset_timeline()",
    "level_float_set": "setLevelValueFloat(\"<value_name>\", <value>)",
    "level_float_add": "setLevelValueFloat(\"<value_name>\", \
getLevelValueFloat(\"<value_name>\") + <value>)",
    "level_float_subtract": "setLevelValueFloat(\"<value_name>\", \
getLevelValueFloat(\"<value_name>\") - <value>)",
    "level_float_multiply": "setLevelValueFloat(\"<value_name>\", \
getLevelValueFloat(\"<value_name>\") * <value>)",
    "level_float_divide": "setLevelValueFloat(\"<value_name>\", \
getLevelValueFloat(\"<value_name>\") / <value>)",
    "level_int_set": "setLevelValueInt(\"<value_name>\", <value>)",
    "level_int_add": "setLevelValueInt(\"<value_name>\", \
getLevelValueFloat(\"<value_name>\") + <value>)",
    "level_int_subtract": "setLevelValueInt(\"<value_name>\", \
getLevelValueFloat(\"<value_name>\") - <value>)",
    "level_int_multiply": "setLevelValueInt(\"<value_name>\", \
getLevelValueFloat(\"<value_name>\") * <value>)",
    "level_int_divide": "setLevelValueInt(\"<value_name>\", \
getLevelValueFloat(\"<value_name>\") / <value>)",
    "style_float_set": "setStyleValueFloat(\"<value_name>\", <value>)",
    "style_float_add": "setStyleValueFloat(\"<value_name>\", \
getLevelValueFloat(\"<value_name>\") + <value>)",
    "style_float_subtract": "setStyleValueFloat(\"<value_name>\", \
getLevelValueFloat(\"<value_name>\") - <value>)",
    "style_float_multiply": "setStyleValueFloat(\"<value_name>\", \
getLevelValueFloat(\"<value_name>\") * <value>)",
    "style_float_divide": "setStyleValueFloat(\"<value_name>\", \
getLevelValueFloat(\"<value_name>\") / <value>)",
    "style_int_set": "setStyleValueInt(\"<value_name>\", <value>)",
    "style_int_add": "setStyleValueInt(\"<value_name>\", \
getLevelValueFloat(\"<value_name>\") + <value>)",
    "style_int_subtract": "setStyleValueInt(\"<value_name>\", \
getLevelValueFloat(\"<value_name>\") - <value>)",
    "style_int_multiply": "setStyleValueInt(\"<value_name>\", \
getLevelValueFloat(\"<value_name>\") * <value>)",
    "style_int_divide": "setStyleValueInt(\"<value_name>\", \
getLevelValueFloat(\"<value_name>\") / <value>)",
    "music_set": "a_setMusic(\"<id>\")",
    "music_set_segment": "a_setMusicSegment(\"<id>\", \"<segment_index>\")",
    "music_set_seconds": "a_setMusicSeconds(\"<id>\", \"<seconds>\")",
    "style_set": CONVERTER_PREFIX + "style_module:set_style(\"<id>\")",
    "side_changing_stop": CONVERTER_PREFIX + "enable_rnd_side_changes = false",
    "side_changing_start": CONVERTER_PREFIX + "enable_rnd_side_changes = true",
    "increment_stop": CONVERTER_PREFIX + "increment_enabled = false",
    "increment_start": CONVERTER_PREFIX + "increment_enabled = true",
    "event_exec": "execEvent(\"<id>\")",
    "event_enqueue": "enqueueEvent(\"<id>\")",
    "script_exec": "u_execScript(\"<value_name>\")",
    "play_sound": "playSound(\"<id>\")"
}

event_lua = LuaFile(os.path.join(os.path.dirname(__file__), "events.lua"))
event_lua.replace("prefix_", CONVERTER_PREFIX)


def convert_event(event_json, pack_path):
    # set default values
    event = {
        "type": event_json.get("type"),
        "duration": event_json.get("duration", 0),
        "value_name": event_json.get("value_name", ""),
        "value": event_json.get("value", 0),
        "message": event_json.get("message", ""),
        "id": event_json.get("id", ""),

        # Only used in music events
        "segment_index": event_json.get("segment_index", None),
        "seconds": event_json.get("seconds", None)
    }
    if event["type"] is None:
        return  # Probably issues with json parsing
    if event["type"] in EVENT_TYPES:
        function = EVENT_TYPES[event["type"]]
        if function is None:
            log.error("Unimplemented event:", event["type"])
            return ""
        if event["type"] == "level_change":
            event["id"] = os.path.basename(event["id"])
        elif event["type"] == "script_exec":
            real_path = fix_utils.match_capitalization(
                os.path.join(pack_path, "Scripts", event["value_name"]))
            event["value_name"] = os.path.relpath(real_path, os.path.join(
                pack_path, "Scripts"))
        for prop in event:
            function = function.replace("<" + prop + ">", str(event[prop]))
        return function.replace("\n", "\\n").replace("\\", "\\\\")
    else:
        return "u_log(\"unkown event type: " + event["type"] + "\")"


def convert_events(events, pack_path):
    if events is None:
        events = []
    event_dict = ExtendedDict()
    for event in events:
        if event is not None:  # this can happen with faulty json
            event_function = convert_event(event, pack_path)
            if event_function is not None:
                event_list = event_dict.get(event.get("time", 0), [])
                event_list.append(event_function)
                event_dict[event.get("time", 0)] = event_list
    return event_dict


def convert_external(json_file):
    pack_path = os.path.dirname(json_file.path)
    while not os.path.exists(os.path.join(pack_path, "pack.json")):
        pack_path = os.path.dirname(pack_path)
    if "id" in json_file:
        new_event_lua = LuaFile()
        new_event_lua.set_text("_G[\"" + CONVERTER_PREFIX + json_file["id"] +
                               "_EVENTS\"]=" + convert_events(
                                   json_file.get("events", []), pack_path)
                               .to_table() + "\n")
        new_event_lua.save("Scripts/" + CONVERTER_PREFIX + "Events/" +
                           json_file["id"] + ".lua")
    else:
        log.error("Event file", json_file.path, "has no id!")


def convert_level(level_json, level_lua):
    pack_path = os.path.dirname(level_json.path)
    while not os.path.exists(os.path.join(pack_path, "pack.json")):
        pack_path = os.path.dirname(pack_path)
    if level_lua.get_function("onInit") is None:
        level_lua.mixin_line("function onInit()\nend")
    level_lua.mixin_line(CONVERTER_PREFIX + "MAIN_EVENTS=" +
                         convert_events(level_json.get("events", []),
                                        pack_path)
                         .to_table(), "onInit")
    level_json.delete("events")


def save():
    event_lua.save("Scripts/" + CONVERTER_PREFIX + "events.lua")
