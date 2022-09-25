u_execScript("prefix_JSON.lua")
log = u_log
getSides = l_getSides
getSpeedMult = u_getSpeedMultDM
getDelayMult = u_getDelayMultDM
getDifficultyMult = u_getDifficultyMult
execScript = u_execScript
forceIncrement = u_forceIncrement


function prefix_resolve_function(func)
	if type(func) == "string" then
		return _G[func]
	else
		return function(...)
			return _G[func[1]][func[2]](_G[func[1]], ...)
		end
	end
end


function prefix_setField(file, field, value)
	local functions
	if file == "level" then
		functions = prefix_LEVEL_PROPERTY_MAPPING[field]
	elseif file == "style" then
		functions = prefix_STYLE_PROPERTY_MAPPING[field]
	end
	if file == "style" then
		prefix_style[field] = value
	end
	if functions == nil then
		if file == "level" then
			prefix_custom_keys[field] = value
		end
	else
		prefix_resolve_function(functions[2])(value)
	end
end

function prefix_getField(file, field, default)
	local functions
	if file == "level" then
		functions = prefix_LEVEL_PROPERTY_MAPPING[field]
	elseif file == "style" then
		functions = prefix_STYLE_PROPERTY_MAPPING[field]
	end
	if functions == nil then
		local value
		if file == "level" then
			value = prefix_custom_keys[field]
		end
		if value == nil then
			value = default
		end
		return value
	else
		if file == "style" and prefix_style[field] ~= nil then
			return prefix_style[field]
		end
		return prefix_resolve_function(functions[1])()
	end
end

function getLevelValueInt(field)
	return prefix_getField("level", field, 0)
end
function getLevelValueFloat(field)
	return prefix_getField("level", field, 0)
end
function getLevelValueString(field)
	return prefix_getField("level", field, "")
end
function getLevelValueBool(field)
	return prefix_getField("level", field, false)
end
function setLevelValueInt(field, value)
	return prefix_setField("level", field, value)
end
function setLevelValueFloat(field, value)
	return prefix_setField("level", field, value)
end
function setLevelValueString(field, value)
	return prefix_setField("level", field, value)
end
function setLevelValueBool(field, value)
	return prefix_setField("level", field, value)
end
function getStyleValueInt(field)
	return prefix_getField("style", field, 0)
end
function getStyleValueFloat(field)
	return prefix_getField("style", field, 0)
end
function getStyleValueString(field)
	return prefix_getField("style", field, "")
end
function getStyleValueBool(field)
	return prefix_getField("style", field, false)
end
function setStyleValueInt(field, value)
	return prefix_setField("style", field, value)
end
function setStyleValueFloat(field, value)
	return prefix_setField("style", field, value)
end
function setStyleValueString(field, value)
	return prefix_setField("style", field, value)
end
function setStyleValueBool(field, value)
	return prefix_setField("style", field, value)
end

function playSound(id)
	if prefix_SOUNDS[id] == nil then
		a_playSound(id)
	else
		a_playPackSound(id)
	end
end

-- make os.clock work as expected, even if the os module worked it would be windows specific
os = {}
os.clock = prefix_get_actual_time

-- make config appear the same as in 1.92 in case a script reads it
prefix_config_keys = {
	"3D_enabled",
	"3D_max_depth",
	"3D_multiplier",
	"auto_restart",
	"auto_zoom_factor",
	"beatpulse_enabled",
	"black_and_white",
	"change_music",
	"change_styles",
	"debug",
	"flash_enabled",
	"fullscreen",
	"fullscreen_auto_resolution",
	"fullscreen_height",
	"fullscreen_width",
	"invincible",
	"limit_fps",
	"music_volume",
	"no_background",
	"no_music",
	"no_rotation",
	"no_sound",
	"official",
	"online",
	"pixel_multiplier",
	"player_focus_speed",
	"player_size",
	"player_speed",
	"pulse_enabled",
	"show_messages",
	"sound_volume",
	"static_frametime",
	"static_frametime_value",
	"t_exit",
	"t_focus",
	"t_force_restart",
	"t_restart",
	"t_rotate_ccw",
	"t_rotate_cw",
	"t_screenshot",
	"vsync",
	"windowed_auto_resolution",
	"windowed_height",
	"windowed_width",
	"zoom_factor"
}
prefix_io_open = io.open
io.open = function(path)
	if path == "config.json" then
		local config_file = prefix_io_open("config.json")
		local config = JSON:decode(config_file:read("*a"))
		config_file:close()
		local new_config = {}
		for _, key in pairs(prefix_config_keys) do
			if config[key] ~= nil then
				new_config[key] = config[key]
			end
		end

		-- Set default controls, so onInput can be used to replace isKeyPressed whenever possible
		new_config.t_rotate_ccw = {{"kLeft"}}
		new_config.t_rotate_cw = {{"kRight"}}
		new_config.t_focus = {{"kShift"}}

		local new_file = io.tmpfile()
		new_file:write(JSON:encode_pretty(new_config))
		return new_file
	else
		return prefix_io_open(path)
	end
end


prefix_key_mapping = {
	[38] = "prefix_focus",
	[71] = "prefix_movement == -1",
	[72] = "prefix_movement == 1"
}
function isKeyPressed(key)
	if prefix_key_mapping[key] == nil then
		return u_isKeyPressed(key)
	else
		return loadstring("return " .. prefix_key_mapping[key])()
	end
end
