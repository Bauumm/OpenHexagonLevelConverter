from extended_dict import ExtendedDict
from config import CONVERTER_PREFIX


LEVEL_PROPERTY_MAPPING = ExtendedDict({
    "speed_multiplier": ["l_getSpeedMult", "l_setSpeedMult"],
    "speed_increment": ["l_getSpeedInc", "l_setSpeedInc"],
    "rotation_speed": ["l_getRotationSpeed", "l_setRotationSpeed"],
    "rotation_increment": ["l_getRotationSpeedInc", "l_setRotationSpeedInc"],
    "rotation_speed_max": ["l_getRotationSpeedMax", "l_setRotationSpeedMax"],
    "delay_multiplier": ["l_getDelayMult", "l_setDelayMult"],
    "delay_increment": ["l_getDelayInc", "l_setDelayInc"],
    "fast_spin": ["l_getFastSpin", "l_setFastSpin"],
    "sides": ["l_getSides", "l_setSides"],
    "sides_max": ["l_getSidesMax", "l_setSidesMax"],
    "sides_min": ["l_getSidesMin", "l_setSidesMin"],
    "increment_time": ["l_getIncTime", "l_setIncTime"],
    "pulse_min": ["l_getPulseMin", "l_setPulseMin"],
    "pulse_max": ["l_getPulseMax", "l_setPulseMax"],
    "pulse_speed": ["l_getPulseSpeed", "l_setPulseSpeed"],
    "pulse_speed_r": ["l_getPulseSpeedR", "l_setPulseSpeedR"],
    "pulse_delay_max": ["l_getPulseDelayMax", "l_setPulseDelayMax"],
    "pulse_delay_half_max": [None, None],
    "beatpulse_max": ["l_getBeatPulseMax", "l_setBeatPulseMax"],
    "beatpulse_delay_max": ["l_getBeatPulseDelayMax",
                            "l_setBeatPulseDelayMax"],
    "radius_min": ["l_getRadiusMin", "l_setRadiusMin"],
    "wall_skew_left": ["l_getWallSkewLeft", "l_setWallSkewLeft"],
    "wall_skew_right": ["l_getWallSkewRight", "l_setWallSkewRight"],
    "wall_angle_left": ["l_getWallAngleLeft", "l_setWallAngleLeft"],
    "wall_angle_right": ["l_getWallAngleRight", "l_setWallAngleRight"],

    # keys that arent set in onInit but may be set with lua in the actual level
    "styleId": [None, CONVERTER_PREFIX + "setStyle"],
    "musicId": [None, "s_setMusic"]
})

LEVEL_PROPERTY_DEFAULTS = {
    "pulse_min": 75,
    "pulse_max": 80,
    "pulse_speed": 0,
    "pulse_speed_r": 0,
    "pulse_delay_max": 0,
    # "pulse_delay_half_max": 0, this property does not exist in steam version
    "beatpulse_max": 0,
    "beatpulse_delay_max": 0,
    "radius_min": 72,
}

PROPERTY_NAME_MAPPING = {
    "menu_priority": "menuPriority",
    "difficulty_multipliers": "difficultyMults",
    "style_id": "styleId",
    "music_id": "musicId",
    "lua_file": "luaFile"
}

NOT_SET_IN_ONINIT = [
    "id",
    "name",
    "description",
    "author",
    "menuPriority",
    "selectable",
    "difficultyMults",
    "styleId",
    "musicId",
    "luaFile"
]


def convert(level_json, level_lua):
    if level_lua.get_function("onInit") is None:
        level_lua.mixin_line("\nfunction onInit()\nend", line=-1)
    # 1.92 doesnt have music DM sync, so with that call we can overwrite the
    # users preference to behave like 1.92. Increments are disabled because the
    # system can't deal with custom walls
    code = "a_syncMusicToDM(false)\nl_setIncEnabled(false)"
    required_defaults = LEVEL_PROPERTY_DEFAULTS.copy()
    keys = list(level_json.keys())
    custom_keys = ExtendedDict()
    for key in keys:
        if key in PROPERTY_NAME_MAPPING:
            level_json.rename(key, PROPERTY_NAME_MAPPING[key])
            key = PROPERTY_NAME_MAPPING[key]
        if key in NOT_SET_IN_ONINIT:
            if key == "luaFile":
                # steam version starts from pack folder
                level_json[key] = "Scripts/" + level_json[key]
            continue
        if key in required_defaults:
            del required_defaults[key]
        functions = LEVEL_PROPERTY_MAPPING.get(key)
        if functions is None or functions[1] is None:
            custom_keys[key] = level_json[key]
        else:
            function = functions[1]
            if level_json.get(key) == float("inf"):
                str_key = "1/0"
            else:
                str_key = str(level_json.get(key))
            code += "\n" + function + "(" + str_key + ")"
            level_json.delete(key)
    for key in required_defaults.keys():
        function = LEVEL_PROPERTY_MAPPING.get(key)[1]
        code += "\n" + function + "(" + str(LEVEL_PROPERTY_DEFAULTS[key]) + ")"
    code += "\nl_setRotationSpeed(l_getRotationSpeed() * \
        (math.random(0, 1) * 2 - 1))"
    code += "\n" + CONVERTER_PREFIX + "custom_keys=" + custom_keys.to_table()
    level_lua.mixin_line(code, "onInit")
