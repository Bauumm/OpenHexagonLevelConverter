u_execScript("prefix_increment.lua")
u_execScript("prefix_message_timeline.lua")
prefix_timeline = {}
prefix_actual_time = -50
prefix_wait_delay = nil
prefix_wait_first_call = true
prefix_timeline_ready = true

function prefix_get_actual_time()
	return (prefix_actual_time + 50) / 60
end

function prefix_update_timeline(frametime)
	prefix_actual_time = prefix_actual_time + frametime
	prefix_update_increment(frametime)
	prefix_update_messages()
	if prefix_actual_time < 0 then
		l_resetTime()
		u_haltTime(-6)
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

function prefix_timeline_clear()
	prefix_timeline = {}
	prefix_wait_first_call = true
end

function prefix_timeline_insert_do(index, func, args)
	if index > #prefix_timeline then
		index = #prefix_timeline
	end
	table.insert(prefix_timeline, index, function()
		if args == nil then
			func()
		else
			func(unpack(args))
		end
		return true
	end)
end

function prefix_timeline_append_do(func, args)
	table.insert(prefix_timeline, function()
		if args == nil then
			func()
		else
			func(unpack(args))
		end
		return true
	end)
end

function prefix_get_wait_function(delay)
	return function(frametime)
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
	end
end

function prefix_timeline_insert_wait(index, delay)
	if index > #prefix_timeline then
		index = #prefix_timeline
	end
	table.insert(prefix_timeline, index, prefix_get_wait_function(delay))
end

function wait(delay)
	table.insert(prefix_timeline, prefix_get_wait_function(delay))
end

function wall(side, thickness)
	prefix_timeline_append_do(prefix_wall_module.wall, {nil, side, thickness})
end

function wallAdj(side, thickness, speedAdj)
	prefix_timeline_append_do(prefix_wall_module.wallAdj, {nil, side, thickness, speedAdj})
end

function wallAcc(side, thickness, speedAdj, acceleration, minSpeed, maxSpeed)
	prefix_timeline_append_do(prefix_wall_module.wallAcc, {nil, side, thickness, speedAdj, acceleration, minSpeed, maxSpeed})
	
end
