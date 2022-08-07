LEVEL_PROPERTY_MAPPING = {
    "speed_multiplier": "l_setSpeedMult",
    "speed_increment": "l_setSpeedInc",
    "rotation_speed": "l_setRotationSpeed",
    "rotation_increment": "l_setRotationSpeedInc",
    "rotation_speed_max": "l_setRotationSpeedMax",
    "delay_multiplier": "l_setDelayMult",
    "delay_increment": "l_setDelayInc",
    "fast_spin": "l_setFastSpin",
    "sides": "l_setSides",
    "sides_max": "l_setSidesMax",
    "sides_min": "l_setSidesMin",
    "increment_time": "l_setIncTime",
    "pulse_min": "l_setPulseMin",
    "pulse_max": "l_setPulseMax",
    "pulse_speed": "l_setPulseSpeed",
    "pulse_speed_r": "l_setPulseSpeedR",
    "pulse_delay_max": "l_setPulseDelayMax",
    "pulse_delay_half_max": "",
    "beatpulse_max": "l_setBeatPulseMax",
    "beatpulse_delay_max": "l_setBeatPulseDelayMax",
    "radius_min": "l_setRadiusMin",
    "wall_skew_left": "l_setWallSkewLeft",
    "wall_skew_right": "l_setWallSkewRight",
    "wall_angle_left": "l_setWallAngleLeft",
    "wall_angle_right": "l_setWallAngleRight",
}

LEVEL_PROPERTY_DEFAULTS = {
    "pulse_min": 75,
    "pulse_max": 80,
    "pulse_speed": 0,
    "pulse_speed_r": 0,
    "pulse_delay_max": 0,
    "pulse_delay_half_max": 0,
    "beatpulse_max": 0,
    "beatpulse_delay_max": 0,
    "radius_min": 72,
    "difficulty_multipliers": [1]
}


# TODO: either check and or manually add defaults
def convert(level_json, level_lua):
    if level_lua.get_function("onInit") is None:
        level_lua.mixin_line("function onInit()\nend", line=-1)
    for key in level_json.get_keys():
        function = LEVEL_PROPERTY_MAPPING.get(key)
        if function is not None:
            level_lua.mixin_line(
                function + "(" + str(level_json.get(key)) + ")",
                "onInit", -1
            )
            level_json.delete(key)
