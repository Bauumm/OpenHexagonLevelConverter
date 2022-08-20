function _setField(file, field, value)
	local functions
	if file == "level" then
		functions = LEVEL_PROPERTY_MAPPING[field]
		if functions == nil then
			u_log("Could not set " .. field .. "!!!")
		else
			_G[functions[2]](value)
		end
	end
end

function _getField(file, field)
	local functions
	if file == "level" then
		functions = LEVEL_PROPERTY_MAPPING[field]
	elseif file == "style" then
		functions = STYLE_PROPERTY_MAPPING[field]
	end
	if functions == nil then
		u_log("Could not get " .. field .. "!!!")
	else
		return _G[functions[1]]()
	end
end

function getLevelValueInt(field)
	return _getField("level", field)
end
function getLevelValueFloat(field)
	return _getField("level", field)
end
function getLevelValueString(field)
	return _getField("level", field)
end
function getLevelValueBool(field)
	return _getField("level", field)
end
function setLevelValueInt(field, value)
	return _setField("level", field, value)
end
function setLevelValueFloat(field, value)
	return _setField("level", field, value)
end
function setLevelValueString(field, value)
	return _setField("level", field, value)
end
function setLevelValueBool(field, value)
	return _setField("level", field, value)
end
function getStyleValueInt(field)
	return _getField("style", field)
end
function getStyleValueFloat(field)
	return _getField("style", field)
end
function getStyleValueString(field)
	return _getField("style", field)
end
function getStyleValueBool(field)
	return _getField("style", field)
end
function setStyleValueInt(field, value)
	return _setField("style", field, value)
end
function setStyleValueFloat(field, value)
	return _setField("style", field, value)
end
function setStyleValueString(field, value)
	return _setField("style", field, value)
end
function setStyleValueBool(field, value)
	return _setField("style", field, value)
end

function playSound(id)
	if SOUNDS[id] == nil then
		a_playSound(id)
	else
		a_playPackSound(id)
	end
end
