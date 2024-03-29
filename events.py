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
    "time_stop": "u_haltTime(<duration>)",
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
    "music_set": CONVERTER_PREFIX + "next_music={id=\"<id>\"}",
    "music_set_segment": CONVERTER_PREFIX + "next_music={id=\"<id>\", segment_index=\
<segment_index>)",
    "music_set_seconds": CONVERTER_PREFIX + "next_music={id=\"<id>\", seconds=\
<seconds>}",
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


id_file_mapping = ExtendedDict()


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
            while event["value_name"].endswith(" "):
                event["value_name"] = event["value_name"][:-1]
            real_path = fix_utils.match_capitalization(
                os.path.join(pack_path, "Scripts", event["value_name"]))
            if real_path is None:
                log.warn("Script", os.path.join(pack_path, "Scripts",
                                                event["value_name"]),
                         "not found!")
                return "u_log(\"" + event["value_name"] + " not found!\")"
            else:
                event["value_name"] = os.path.relpath(real_path, os.path.join(
                    pack_path, "Scripts"))
        for prop in event:
            function = function.replace("<" + prop + ">", str(event[prop]))
        return function.replace("\\", "\\\\\\\\").replace("\n", "\\\\n")
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
        filename = os.path.basename(json_file.path)[:-5]
        id_file_mapping[json_file["id"]] = filename
        new_event_lua = LuaFile()
        new_event_lua.set_text(CONVERTER_PREFIX + "EVENT_FILES[\"" + json_file["id"] +
                               "\"]=" + convert_events(json_file.get("events", []),
                                                       pack_path).to_table() + "\n")
        new_event_lua.save("Scripts/" + CONVERTER_PREFIX + "Events/" +
                           filename + ".lua")
    else:
        log.error("Event file", json_file.path, "has no id!")


def convert_level(level_json, level_lua):
    pack_path = os.path.dirname(level_json.path)
    while not os.path.exists(os.path.join(pack_path, "pack.json")):
        pack_path = os.path.dirname(pack_path)
    if level_lua.get_function(CONVERTER_PREFIX + "onInit") is None:
        level_lua.mixin_line("function " + CONVERTER_PREFIX + "onInit()\nend")
    main_events = ExtendedDict({"events": convert_events(level_json.get("events", []),
                                                         pack_path)})
    level_lua.mixin_line(CONVERTER_PREFIX + "MAIN_EVENTS=" + main_events.to_table(),
                         CONVERTER_PREFIX + "onInit")
    level_json.delete("events")


def save(packdata):
    packdata.mixin_line(CONVERTER_PREFIX + "EVENT_ID_FILE_MAPPING=" + id_file_mapping
                        .to_table(), line=1)
