from extended_dict import ExtendedDict
from config import CONVERTER_PREFIX


LEVEL_PROPERTY_MAPPING = ExtendedDict({
    "speed_multiplier": ["l_getSpeedMult", "l_setSpeedMult"],
    "speed_increment": ["l_getSpeedInc", "l_setSpeedInc"],
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
    "beatpulse_max": ["l_getBeatPulseMax", "l_setBeatPulseMax"],
    "beatpulse_delay_max": ["l_getBeatPulseDelayMax",
                            "l_setBeatPulseDelayMax"],
    "radius_min": ["l_getRadiusMin", "l_setRadiusMin"],
    "wall_skew_left": ["l_getWallSkewLeft", "l_setWallSkewLeft"],
    "wall_skew_right": ["l_getWallSkewRight", "l_setWallSkewRight"],
    "wall_angle_left": ["l_getWallAngleLeft", "l_setWallAngleLeft"],
    "wall_angle_right": ["l_getWallAngleRight", "l_setWallAngleRight"],

    # keys that arent set in onInit but may be set with lua in the actual level
    "styleId": [None, CONVERTER_PREFIX + "style_module:set_style"],
    "musicId": [None, "a_setMusic"]
})

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
    keys = list(level_json.keys())
    for key in keys:
        if key in PROPERTY_NAME_MAPPING:
            level_json.rename(key, PROPERTY_NAME_MAPPING[key])
            key = PROPERTY_NAME_MAPPING[key]
        if key == "luaFile":
            # steam version starts from pack folder
            level_json[key] = "Scripts/" + level_json[key]
        if key not in NOT_SET_IN_ONINIT:
            level_json.delete(key)
