from extended_dict import ExtendedDict
from config import CONVERTER_PREFIX
from lua_file import LuaFile
import log
import os


EVENT_TYPES = {
    "level_change": None,
    "menu": "e_kill()",  # There is no way to exit to menu in steam version
    "message_add": "messageAdd(\"<message>\", <duration>)",
    "message_important_add":
        "messageImportantAdd(\"<message>\", <duration>)",
    "message_clear": "e_messageAddImportantSilent(\"\", 0)",
    "time_stop": "e_stopTime(<duration>)",  # TODO: make stopTime work the same
    "timeline_wait": "wait(<duration>)",
    "timeline_clear": CONVERTER_PREFIX + "timeline = {}",
    "level_float_set": "setLevelValueFloat(\"<valueName>\", <value>)",
    "level_float_add": "setLevelValueFloat(\"<valueName>\", \
getLevelValueFloat(\"<valueName>\") + <value>)",
    "level_float_subtract": "setLevelValueFloat(\"<valueName>\", \
getLevelValueFloat(\"<valueName>\") - <value>)",
    "level_float_multiply": "setLevelValueFloat(\"<valueName>\", \
getLevelValueFloat(\"<valueName>\") * <value>)",
    "level_float_divide": "setLevelValueFloat(\"<valueName>\", \
getLevelValueFloat(\"<valueName>\") / <value>)",
    "level_int_set": "setLevelValueInt(\"<valueName>\", <value>)",
    "level_int_add": "setLevelValueInt(\"<valueName>\", \
getLevelValueFloat(\"<valueName>\") + <value>)",
    "level_int_subtract": "setLevelValueInt(\"<valueName>\", \
getLevelValueFloat(\"<valueName>\") - <value>)",
    "level_int_multiply": "setLevelValueInt(\"<valueName>\", \
getLevelValueFloat(\"<valueName>\") * <value>)",
    "level_int_divide": "setLevelValueInt(\"<valueName>\", \
getLevelValueFloat(\"<valueName>\") / <value>)",
    "style_float_set": "setStyleValueFloat(\"<valueName>\", <value>)",
    "style_float_add": "setStyleValueFloat(\"<valueName>\", \
getLevelValueFloat(\"<valueName>\") + <value>)",
    "style_float_subtract": "setStyleValueFloat(\"<valueName>\", \
getLevelValueFloat(\"<valueName>\") - <value>)",
    "style_float_multiply": "setStyleValueFloat(\"<valueName>\", \
getLevelValueFloat(\"<valueName>\") * <value>)",
    "style_float_divide": "setStyleValueFloat(\"<valueName>\", \
getLevelValueFloat(\"<valueName>\") / <value>)",
    "style_int_set": "setStyleValueInt(\"<valueName>\", <value>)",
    "style_int_add": "setStyleValueInt(\"<valueName>\", \
getLevelValueFloat(\"<valueName>\") + <value>)",
    "style_int_subtract": "setStyleValueInt(\"<valueName>\", \
getLevelValueFloat(\"<valueName>\") - <value>)",
    "style_int_multiply": "setStyleValueInt(\"<valueName>\", \
getLevelValueFloat(\"<valueName>\") * <value>)",
    "style_int_divide": "setStyleValueInt(\"<valueName>\", \
getLevelValueFloat(\"<valueName>\") / <value>)",
    "music_set": "a_setMusic(\"<id>\")",
    "music_set_segment": "a_setMusicSegment(\"<id>\", \"<segment_index>\")",
    "music_set_seconds": "a_setMusicSeconds(\"<id>\", \"<seconds>\")",
    "style_set": CONVERTER_PREFIX + "setStyle(\"<id>\")",
    "side_changing_stop": "l_enableRndSideChanges(false)",
    "side_changing_start": "l_enableRndSideChanges(true)",
    "increment_stop": "l_setIncEnabled(false)",
    "increment_start": "l_setIncEnabled(true)",
    "event_exec": "execEvent(\"<id>\")",
    "event_enqueue": "enqueueEvent(\"<id>\")",
    "script_exec": "u_execScript(\"<valueName>\")",
    "play_sound": "playSound(\"<id>\")"
}

event_lua = LuaFile(os.path.join(os.path.dirname(__file__), "events.lua"))
event_lua.replace("prefix_", CONVERTER_PREFIX)


def convert_event(event_json):
    event = {
        "type": event_json.get("type", ""),
        "duration": event_json.get("duration", 0),
        "valueName": event_json.get("value_name", ""),
        "value": event_json.get("value", 0),
        "message": event_json.get("message", ""),
        "id": event_json.get("id", ""),

        # Only used in music events
        "segment_index": event_json.get("segment_index", None),
        "seconds": event_json.get("seconds", None)
    }
    if event["type"] in EVENT_TYPES:
        function = EVENT_TYPES[event["type"]]
        if function is None:
            log.error("Unimplemented event:", event["type"])
            return ""
        for prop in event:
            function = function.replace("<" + prop + ">", str(event[prop]))
        return function.replace("\n", "\\\\n")
    else:
        return "u_log(\"unkown event type: " + event["type"] + "\")"


def convert_events(events):
    event_dict = ExtendedDict()
    for event in events:
        if event is not None:  # this can happen with faulty json
            event_function = convert_event(event)
            event_list = event_dict.get(event.get("time", 0), [])
            event_list.append(event_function)
            event_dict[event.get("time", 0)] = event_list
    return event_dict


def convert_external(json_file):
    if "id" in json_file:
        new_event_lua = LuaFile()
        new_event_lua.set_text("_G[\"" + CONVERTER_PREFIX + json_file["id"] +
                               "_EVENTS\"]=" + convert_events(
                                   json_file.get("events", []))
                               .to_table() + "\n")
        new_event_lua.save("Scripts/" + CONVERTER_PREFIX + "Events/" +
                           json_file["id"] + ".lua")
    else:
        log.error("Event file", json_file.path, "has no id!")


def convert_level(level_json, level_lua):
    level_lua.mixin_line("if " + CONVERTER_PREFIX + "was_defined == nil then\n"
                         + CONVERTER_PREFIX + "MAIN_EVENTS=" +
                         convert_events(level_json.get("events", []))
                         .to_table() + "\nend")
    level_json.delete("events")


def save():
    event_lua.save("Scripts/" + CONVERTER_PREFIX + "events.lua")
