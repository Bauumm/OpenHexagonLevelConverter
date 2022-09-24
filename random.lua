prefix_seed = u_getAttemptRandomSeed()

math.randomseed = function(seed)
	prefix_seed = seed
end

math.random = function(a, b)
	local function band(a, b)
		local result = 0
		local mult = 1
		local ba, bb
		repeat
			local ba = math.modf(a / mult)
			local bb = math.modf(b / mult)
			if ba % 2 == 1 and bb % 2 == 1 then
				result = result + mult
			end
			mult = mult * 2
		until ba == 0 or bb == 0
		return result
	end
	prefix_seed = band(prefix_seed * 1103515245 + 12345, 0x7fffffff)
	if a == nil then
		return prefix_seed / 2147483647
	end
	local size
	local start
	if b == nil then
		if a <= 0 then
			error("bad argument to 'random' (interval is empty)")
		end
		size = a
		start = 1
	else
		if a > b then
			error("bad argument to 'random' (interval is empty)")
		end
		size = b - a + 1
		start = a
	end
	return prefix_seed % size + start
end
