log = u_log
getSides = l_getSides
getSpeedMult = u_getSpeedMultDM
getDelayMult = u_getDelayMultDM
getDifficultyMult = u_getDifficultyMult
execScript = u_execScript
forceIncrement = u_forceIncrement
isKeyPressed = u_isKeyPressed


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
	if functions == nil then
		if file == "level" then
			prefix_custom_keys[field] = value
		else
			u_log("Could not set " .. field .. "!!!")
		end
	else
		if file == "style" then
			prefix_style[field] = value
		end
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
