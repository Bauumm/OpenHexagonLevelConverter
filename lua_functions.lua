prefix_RAD = {
	wall_angle_left=true,
	wall_angle_right=true,
	wall_skew_left=true,
	wall_skew_right=true
}


function prefix_setField(file, field, value)
	local functions
	if file == "level" then
		functions = prefix_LEVEL_PROPERTY_MAPPING[field]
	elseif file == "style" then
		functions = prefix_STYLE_PROPERTY_MAPPING[field]
	end
	if functions == nil then
		u_log("Could not set " .. field .. "!!!")
	else
		if prefix_RAD[field] then
			_G[functions[2]](math.rad(value))
		else
			_G[functions[2]](value)
		end
	end
end

function prefix_getField(file, field)
	local functions
	if file == "level" then
		functions = prefix_LEVEL_PROPERTY_MAPPING[field]
	elseif file == "style" then
		functions = prefix_STYLE_PROPERTY_MAPPING[field]
	end
	if functions == nil then
		u_log("Could not get " .. field .. "!!!")
	else
		if prefix_RAD[field] then
			return math.deg(_G[functions[1]]())
		else
			return _G[functions[1]]()
		end
	end
end

function getLevelValueInt(field)
	return prefix_getField("level", field)
end
function getLevelValueFloat(field)
	return prefix_getField("level", field)
end
function getLevelValueString(field)
	return prefix_getField("level", field)
end
function getLevelValueBool(field)
	return prefix_getField("level", field)
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
	return prefix_getField("style", field)
end
function getStyleValueFloat(field)
	return prefix_getField("style", field)
end
function getStyleValueString(field)
	return prefix_getField("style", field)
end
function getStyleValueBool(field)
	return prefix_getField("style", field)
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
