-- small utility class to automatically round numbers like exactly like floats in c++
prefix_float = {}
prefix_float.round = function(num)
	local speedMult = l_getSpeedMult()
	l_setSpeedMult(num)
	local num = l_getSpeedMult()
	l_setSpeedMult(speedMult)
	return num
end
prefix_float.make_float = function(num)
	if type(num) == "number" then
		return prefix_float:new(num)
	end
	return num
end
prefix_float.__add = function(a, b)
	return prefix_float:new(prefix_float.make_float(a).value + prefix_float.make_float(b).value)
end
prefix_float.__sub = function(a, b)
	return prefix_float:new(prefix_float.make_float(a).value - prefix_float.make_float(b).value)
end
prefix_float.__mul = function(a, b)
	return prefix_float:new(prefix_float.make_float(a).value * prefix_float.make_float(b).value)
end
prefix_float.__div = function(a, b)
	return prefix_float:new(prefix_float.make_float(a).value / prefix_float.make_float(b).value)
end
prefix_float.__tostring = function(o)
	return o.value
end
function prefix_float:new(value)
	return setmetatable({value=prefix_float.round(value or 0)}, prefix_float)
end

function round_to_even(num)
	if num == nil then
		return 0
	end
	local decimal = num % 1
	if decimal ~= 0.5 then
		return math.floor(num + 0.5)
	else
		if num % 2 == 0.5 then
			return num - 0.5
		else
			return num + 0.5
		end
	end
end

-- insert a path into a recursive table structure
function prefix_insert_path(t, keys, value)
	local directory = t
	for i=1,#keys do
		local key = keys[i]
		if directory[key] == nil then
			if i == #keys then
				directory[key] = value
				return
			end
			directory[key] = {}
		end
		directory = directory[key]
	end
end

-- lookup the item at the end of a path inside a recursive table structure
function prefix_lookup_path(t, keys)
	local directory = t
	for _, key in pairs(keys) do
		if directory[key] == nil then
			return
		end
		directory = directory[key]
	end
	return directory
end
