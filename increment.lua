prefix_last_increment = 0
prefix_is_incrementing = false
prefix_fast_spin = -1
prefix_enable_rnd_side_changes = true
prefix_increment_enabled = true

function prefix_sign(number)
    return number > 0 and 1 or (number == 0 and 0 or -1)
end

-- don't ask what this does, i just copied it from 1.92 code
function prefix_get_smoother_step(edge0, edge1, x)
	local x = math.max(0, math.min(1, (x - edge0) / (edge1 - edge0)))
	return x * x * x * (x * (x * 6 - 15) + 10)
end

function isFastSpinning()
	return prefix_fast_spin > 0
end

function prefix_update_increment(frametime)
	if not prefix_increment_enabled then
		return
	end
	local incTime = l_getLevelTime() - prefix_last_increment
	if incTime >= l_getIncTime() then
		prefix_last_increment = l_getLevelTime()
		prefix_is_incrementing = true
		
		a_playSound("levelUp.ogg")
		l_setRotationSpeed(l_getRotationSpeed() + l_getRotationSpeedInc() * prefix_sign(l_getRotationSpeed()))
		l_setRotationSpeed(l_getRotationSpeed() * -1)
		if prefix_fast_spin < 0 and math.abs(l_getRotationSpeed()) > l_getRotationSpeedMax() then
			l_setRotationSpeed(l_getRotationSpeedMax() * prefix_sign(l_getRotationSpeed()))
		end
		prefix_fast_spin = l_getFastSpin()
		prefix_main_timeline:insert(prefix_main_timeline:get_current_index() + 1, prefix_t_do:new(prefix_main_timeline, function()
			prefix_side_change(math.random(l_getSidesMin(), l_getSidesMax()))
		end))
	end
	if prefix_fast_spin > 0 then
		l_setRotation(l_getRotation() + (math.abs((prefix_get_smoother_step(0, l_getFastSpin(), prefix_fast_spin) / 3.5) * frametime * 17)) * prefix_sign(l_getRotationSpeed()))
		prefix_fast_spin = prefix_fast_spin - frametime
	end
end

function prefix_side_change(sides)
	if not prefix_wall_module:empty() then
		prefix_main_timeline:insert(prefix_main_timeline:get_current_index() + 1, prefix_t_do:new(prefix_main_timeline, function()
			prefix_clear_and_reset_timeline()
		end))
		prefix_main_timeline:insert(prefix_main_timeline:get_current_index() + 1, prefix_t_do:new(prefix_main_timeline, function()
			prefix_side_change(sides)
		end))
		prefix_main_timeline:insert(prefix_main_timeline:get_current_index() + 1, prefix_t_wait:new(prefix_main_timeline, 1))
		return
	end
	onIncrement()
	prefix_is_incrementing = false
	l_setSpeedMult(l_getSpeedMult() + l_getSpeedInc())
	l_setDelayMult(l_getDelayMult() + l_getDelayInc())
	if prefix_enable_rnd_side_changes then
		a_playSound("beep.ogg")
		l_setSides(sides)
	end
end
