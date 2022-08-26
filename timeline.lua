u_execScript("prefix_increment.lua")
u_execScript("prefix_message_timeline.lua")
prefix_timeline = {}
prefix_actual_time = -50
prefix_initial_time = nil
prefix_wait_delay = nil
prefix_wait_first_call = true
prefix_timeline_ready = true

function prefix_get_actual_time()
	return (prefix_actual_time + 50) / 60
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
