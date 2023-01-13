prefix_random_values = { a = 1103515245, c = 12345 }

function math.random(a, b)
	local t = prefix_random_values.a * prefix_random_values.x + prefix_random_values.c
	local y = t % 0x10000
	prefix_random_values.x = y
	prefix_random_values.c = math.floor(t / 0x10000)
	if not a then
		return y / 0x10000
	elseif not b then
		if a == 0 then
			return y
		else
			return 1 + (y % prefix_floor_with_negatives(a))
		end
	else
		a = prefix_floor_with_negatives(a)
		b = prefix_floor_with_negatives(b)
		return a + (y % (b - a + 1))
	end
end

function math.randomseed(s)
	prefix_random_values.c = 12345
	prefix_random_values.x = s % 0x80000000
end

math.randomseed(u_getAttemptRandomSeed())
