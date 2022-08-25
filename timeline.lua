prefix_timeline = {}
prefix_actual_time = -50
prefix_initial_time = nil
prefix_wait_delay = nil
prefix_wait_first_call = true
prefix_timeline_ready = true
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

function prefix_get_actual_time()
	return (prefix_actual_time + 50) / 60
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
	end
	if prefix_fast_spin > 0 then
		l_setRotation(l_getRotation() + math.abs((prefix_get_smoother_step(0, l_getFastSpin(), prefix_fast_spin) / 3.5) * frametime * 17))
		prefix_fast_spin = prefix_fast_spin - frametime
	end
	if prefix_is_incrementing and prefix_wall_module:empty() then
		onIncrement()
		prefix_is_incrementing = false
		l_setSpeedMult(l_getSpeedMult() + l_getSpeedInc())
		l_setDelayMult(l_getDelayMult() + l_getDelayInc())
		if prefix_enable_rnd_side_changes then
			a_playSound("beep.ogg")
			l_setSides(math.random(l_getSidesMin(), l_getSidesMax()))
		end
	end
end

function prefix_update_timeline(frametime)
	prefix_update_increment(frametime)
	prefix_update_messages()
	if prefix_actual_time < 0 then
		prefix_actual_time = prefix_actual_time + frametime
		l_resetTime()
		u_haltTime(-6)
	else
		if prefix_initial_time == nil then
			prefix_initial_time = prefix_actual_time
		end
		prefix_actual_time = prefix_initial_time + l_getLevelTime() * 60
	end
	prefix_timeline_ready = true
	repeat
		if prefix_timeline[1] == nil then
			if not prefix_is_incrementing then
				xpcall(prefix_onStep, print)
			end
			prefix_timeline_ready = false
		elseif prefix_timeline[1](frametime) then
			table.remove(prefix_timeline, 1)
		end
	until not prefix_timeline_ready
end

function wait(delay)
	table.insert(prefix_timeline, function(frametime)
		prefix_timeline_ready = false
		if prefix_wait_first_call then
			prefix_wait_first_call = false
			prefix_wait_delay = delay
		end
		prefix_wait_delay = prefix_wait_delay - frametime
		local done = not (prefix_wait_delay - frametime > frametime)
		if done then
			prefix_wait_first_call = true
		end
		return done
	end)
end

function wall(side, thickness)
	table.insert(prefix_timeline, function()
		prefix_wall_module:wall(side, thickness)
		return true
	end)
end

function wallAdj(side, thickness, speedAdj)
	table.insert(prefix_timeline, function()
		prefix_wall_module:wallAdj(side, thickness, speedAdj)
		return true
	end)
end

function wallAcc(side, thickness, speedAdj, acceleration, minSpeed, maxSpeed)
	table.insert(prefix_timeline, function()
		prefix_wall_module:wallAcc(side, thickness, speedAdj, acceleration, minSpeed, maxSpeed)
		return true
	end)
end

prefix_message_clear_timeline = ct_create()
prefix_message_timeline = {}
prefix_message_remove_time = nil
function prefix_update_messages()
	if prefix_message_timeline[1] ~= nil then
		if prefix_message_remove_time == nil then
			prefix_message_remove_time = prefix_get_actual_time() + prefix_message_timeline[1]() / 60
		elseif prefix_message_remove_time <= prefix_get_actual_time() then
			e_messageAddImportantSilent("", 0)
			prefix_message_remove_time = nil
			table.remove(prefix_message_timeline, 1)
			prefix_update_messages()
		end
	end
end

function messageAdd(message, duration)
	table.insert(prefix_message_timeline, function()
		setMessage(message)
		return duration
	end)
end

function messageImportantAdd(message, duration)
	table.insert(prefix_message_timeline, function()
		setMessageImportant(message)
		return duration
	end)
end

function setMessage(str)
	e_messageAdd(str, 1)
	ct_wait(prefix_message_clear_timeline, 1)
	ct_eval(prefix_message_clear_timeline, "e_clearMessages()")
end

function setMessageImportant(str)
	e_messageAddImportant(str, 1)
	ct_wait(prefix_message_clear_timeline, 1)
	ct_eval(prefix_message_clear_timeline, "e_clearMessages()")
end
