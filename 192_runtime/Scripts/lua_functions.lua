u_execScript("JSON.lua")
log = u_log
getSides = l_getSides
getSpeedMult = u_getSpeedMultDM
getDelayMult = u_getDelayMultDM
getDifficultyMult = u_getDifficultyMult
execScript = u_execScript


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
		if file == "style" and functions[2] == nil then
			return
		end
		local func = prefix_resolve_function(functions[2])
		if func ~= nil then
			func(value)
		end
	end
end

function prefix_getField(file, field, default, converter)
	local functions
	if file == "level" then
		functions = prefix_LEVEL_PROPERTY_MAPPING[field]
	elseif file == "style" then
		functions = prefix_STYLE_PROPERTY_MAPPING[field]
		if prefix_style[field] ~= nil then
			return prefix_style[field]
		end
	end
	local value
	if functions == nil then
		if file == "level" then
			value = prefix_custom_keys[field]
			if value == nil then
				value = _G["prefix_level_json_" .. prefix_level_id][field]
			end
		end
		if value == nil then
			value = default
		end
	else
		value = prefix_resolve_function(functions[1])()
	end
	if converter == nil then
		return value
	else
		return converter(value)
	end
end

function getLevelValueInt(field)
	return prefix_getField("level", field, 0, function(value)
		return round_to_even(tonumber(value))
	end)
end
function getLevelValueFloat(field)
	return prefix_getField("level", field, 0, tonumber)
end
function getLevelValueString(field)
	return prefix_getField("level", field, "", function(value)
		local str = tostring(value)
		if type(value) == "number" and str:match("[.]") then
			return str .. "0"
		else
			return str
		end
	end)
end
function getLevelValueBool(field)
	return prefix_getField("level", field, false)
end
function setLevelValueInt(field, value)
	value = round_to_even(value)
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
	return prefix_getField("style", field, 0, function(value)
		return round_to_even(tonumber(value))
	end)
end
function getStyleValueFloat(field)
	return prefix_getField("style", field, 0, tonumber)
end
function getStyleValueString(field)
	return prefix_getField("style", field, "", function(value)
		local str = tostring(value)
		if type(value) == "number" and str:match("[.]") then
			return str .. "0"
		else
			return str
		end
	end)
end
function getStyleValueBool(field)
	return prefix_getField("style", field, false)
end
function setStyleValueInt(field, value)
	value = round_to_even(value)
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
prefix_call_threshold = 1000000
prefix_calls_this_tick = 0
function os.clock()
	-- make code like
	-- while os.clock() < 100 do...
	-- not freeze the game
	prefix_calls_this_tick = prefix_calls_this_tick + 1
	if prefix_calls_this_tick >= prefix_call_threshold then
		return prefix_get_actual_time() + prefix_calls_this_tick / prefix_call_threshold - 1
	end
	return prefix_get_actual_time()
end
os.exit = e_kill  -- levels that close the game in 1.92 should kill the player

-- spoof date
function os.date(format_string)
	if format_string == nil then
		format_string = "%m/%d/%Y %H:%M:%S"
	end
	local function ensure_length(string, len)
		while #string < len do
			string = "0" .. string
		end
		return string
	end
	local time = prefix_get_actual_time() + 100000
	local string = format_string
			:gsub("%%y", "22")
			:gsub("%%Y", "2022")
			:gsub("%%m", "12")
			:gsub("%%I", ensure_length(tostring(math.floor(time / 86400) % 7 + 1), 2))
			:gsub("%%d", ensure_length(tostring(math.floor(time / 86400) % 30 + 1), 2))
			:gsub("%%H", ensure_length(tostring(math.floor(time / 3600) % 24), 2))
			:gsub("%%M", ensure_length(tostring(math.floor(time / 60) % 60), 2))
			:gsub("%%S", ensure_length(tostring(math.floor(time) % 60), 2))
	return string
end

function os.execute(cmd)
	print("This level attempted to execute a potentially malicious command:", cmd)
	return 1
end

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
if not prefix_init_fs then
	prefix_init_fs = true
	prefix_original_io = io
	io = setmetatable({}, {__index = function(t, k)
		return function(f, ...)
			if f ~= nil and f[k] ~= nil then
				return f[k](f, ...)
			end
			if type(f) == "table" then
				return prefix_original_io[k](f.file, ...)
			else
				return prefix_original_io[k](f, ...)
			end
		end
	end})
	prefix_fake_file = {__index = function(t, k)
		if type(t.file[k]) == "function" then
			return function(self, ...)
				if type(self) == "table" then
					return t.file[k](self.file, ...)
				else
					return t.file[k](self, ...)
				end
			end
		else
			return t.file[k]
		end
	end}
	function prefix_dump_files()
		local files = {}
		for path, file in pairs(prefix_virtual_filesystem) do
			file:seek("set", 0)
			files[path] = file:read("*a")
			file:close()
		end
		return files
	end
	function prefix_load_files(files)
		for path, contents in pairs(files) do
			local file = setmetatable({
				file = io.tmpfile(),
				close = function(self)
					self.file:seek("set", 0)
					return true
				end}, prefix_fake_file)
			file:write(contents)
			file:seek("set", 0)
			prefix_virtual_filesystem[path] = file
		end
	end
	prefix_virtual_filesystem = {}
	prefix_io_open = prefix_original_io.open
	io.open = function(path, mode)
		mode = mode or "r"
		mode = mode:sub(0, 1)
		if mode == "w" or mode == "a" then
			if mode == "a" and prefix_virtual_filesystem[path] ~= nil then
				prefix_virtual_filesystem[path]:seek("end", 0)
				return prefix_virtual_filesystem[path]
			end
			local file = setmetatable({
				file = io.tmpfile(),
				close = function(self)
					self.file:seek("set", 0)
					return true
				end}, prefix_fake_file)
			prefix_virtual_filesystem[path] = file
			return file
		elseif mode == "r" then
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
				new_file:seek("set", 0)
				return new_file
			end
			if prefix_virtual_filesystem[path] == nil then
				return prefix_io_open(path, mode)
			else
				prefix_virtual_filesystem[path]:seek("set", 0)
				return prefix_virtual_filesystem[path]
			end
		else
			return prefix_io_open(path, mode)
		end
	end
	function io.lines(filename)
		if filename == nil then
			return prefix_original_io.lines()
		else
			return io.open(filename):lines()
		end
	end
end

prefix_KEYS = {
	Unknown = -1,
	A = 0,
	B = 1,
	C = 2,
	D = 3,
	E = 4,
	F = 5,
	G = 6,
	H = 7,
	I = 8,
	J = 9,
	K = 10,
	L = 11,
	M = 12,
	N = 13,
	O = 14,
	P = 15,
	Q = 16,
	R = 17,
	S = 18,
	T = 19,
	U = 20,
	V = 21,
	W = 22,
	X = 23,
	Y = 24,
	Z = 25,
	Num0 = 26,
	Num1 = 27,
	Num2 = 28,
	Num3 = 29,
	Num4 = 30,
	Num5 = 31,
	Num6 = 32,
	Num7 = 33,
	Num8 = 34,
	Num9 = 35,
	Escape = 36,
	LControl = 37,
	LShift = 38,
	LAlt = 39,
	LSystem = 40,
	RControl = 41,
	RShift = 42,
	RAlt = 43,
	RSystem = 44,
	Menu = 45,
	LBracket = 46,
	RBracket = 47,
	Semicolon = 48,
	Comma = 49,
	Period = 50,
	Quote = 51,
	Slash = 52,
	Backslash = 53,
	Tilde = 54,
	Equal = 55,
	Hyphen = 56,
	Space = 57,
	Enter = 58,
	Backspace = 59,
	Tab = 60,
	PageUp = 61,
	PageDown = 62,
	End = 63,
	Home = 64,
	Insert = 65,
	Delete = 66,
	Add = 67,
	Subtract = 68,
	Multiply = 69,
	Divide = 70,
	Left = 71,
	Right = 72,
	Up = 73,
	Down = 74,
	Numpad0 = 75,
	Numpad1 = 76,
	Numpad2 = 77,
	Numpad3 = 78,
	Numpad4 = 79,
	Numpad5 = 80,
	Numpad6 = 81,
	Numpad7 = 82,
	Numpad8 = 83,
	Numpad9 = 84,
	F1 = 85,
	F2 = 86,
	F3 = 87,
	F4 = 88,
	F5 = 89,
	F6 = 90,
	F7 = 91,
	F8 = 92,
	F9 = 93,
	F10 = 94,
	F11 = 95,
	F12 = 96,
	F13 = 97,
	F14 = 98,
	F15 = 99,
	Pause = 100
}
prefix_key_mapping = {
	[prefix_KEYS.LShift] = "prefix_focus",
	[prefix_KEYS.Left] = "prefix_movement == -1",
	[prefix_KEYS.Right] = "prefix_movement == 1"
}

-- use onInput swap to find key if possible
local config_file = prefix_io_open("config.json")
local config = JSON:decode(config_file:read("*a"))
config_file:close()
for _, key in pairs(config.t_swap) do
	local kId = key[1]:sub(2)
	if prefix_KEYS[kId] ~= nil then
		prefix_key_mapping[prefix_KEYS[kId]] = "prefix_swap"
	end
end

function isKeyPressed(key)
	if prefix_key_mapping[key] == nil then
		return u_isKeyPressed(key)
	else
		return loadstring("return " .. prefix_key_mapping[key])()
	end
end
