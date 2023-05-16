u_execScript("timeline.lua")
u_execScript("increment.lua")

prefix_timeline, prefix_t_wait, prefix_t_do = prefix_get_timeline_module()
u_execScript("message_timeline.lua")
prefix_actual_time = -50
prefix_main_timeline = prefix_timeline:new()

function prefix_get_actual_time()
	return (prefix_actual_time + 50) / 60
end

function prefix_update_initial_timestop(frametime)
	prefix_actual_time = prefix_actual_time + frametime
	prefix_update_increment(frametime)
	if prefix_actual_time < 0 then
		u_haltTime(frametime)
	end
end

function prefix_update_timeline(frametime)
	prefix_main_timeline:update(frametime)
	if prefix_main_timeline.finished then
		prefix_main_timeline:clear()
		prefix_function_wrapper(prefix_onStep)
		prefix_main_timeline:reset()
	end
end

function prefix_clear_and_reset_timeline()
	prefix_main_timeline:clear()
	prefix_main_timeline:reset()
end

function wait(delay)
	prefix_main_timeline:append(prefix_t_wait:new(prefix_main_timeline, delay))
end

function wall(side, thickness)
	prefix_main_timeline:append(prefix_t_do:new(prefix_main_timeline, function()
		prefix_wall_module:wall(side, thickness)
	end))
end

function wallAdj(side, thickness, speedAdj)
	prefix_main_timeline:append(prefix_t_do:new(prefix_main_timeline, function()
		prefix_wall_module:wallAdj(side, thickness, speedAdj)
	end))
end

function wallAcc(side, thickness, speedAdj, acceleration, minSpeed, maxSpeed)
	prefix_main_timeline:append(prefix_t_do:new(prefix_main_timeline, function()
		prefix_wall_module:wallAcc(side, thickness, speedAdj, acceleration, minSpeed, maxSpeed)
	end))
end
