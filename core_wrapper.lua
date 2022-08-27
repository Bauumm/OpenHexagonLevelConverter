if prefix_was_defined == nil then
	prefix_was_defined = true
	prefix_time_stop = 0
	if prefix_limit_fps ~= nil then
		prefix_target_tickrate = prefix_limit_fps / 240
		prefix_remainder = 0
	end
	u_execScript("prefix_styles.lua")
	u_execScript("prefix_timeline.lua")
	u_execScript("prefix_lua_functions.lua")
	u_execScript("prefix_events.lua")
	u_execScript("prefix_walls.lua")

	-- wrap core functions to ignore errors and call custom event/timeline/style handlers
	function prefix_function_wrapper(func, arg)
		if func ~= nil then
			xpcall(func, print, arg)
		end
	end

	-- onStep should not be called by the game but by the custom timeline, so it isn't included here
	function onUpdate(frametime)
		if prefix_limit_fps ~= nil then
			local calls = prefix_target_tickrate + prefix_remainder
			local actual_calls = math.floor(calls)
			prefix_remainder = calls - actual_calls
			for i=1,actual_calls do
				prefix_call_onUpdate(frametime / prefix_target_tickrate)
			end
		else
			prefix_call_onUpdate(frametime)
		end
		if prefix_time_stop > 0 then
			prefix_time_stop = prefix_time_stop - frametime
			u_haltTime(frametime)
		end
	end

	function prefix_call_onUpdate(frametime)
		prefix_update_events(frametime)
		prefix_updateStyle()
		prefix_function_wrapper(prefix_onUpdate, frametime)
		prefix_update_timeline(frametime)
		prefix_wall_module:update_walls(frametime)
	end

	function onUnload()
		prefix_function_wrapper(prefix_onUnload)
	end

	function onLoad()
		u_haltTime(-6)  -- undo timehalt the steam version adds by default
		prefix_initStyle()
		prefix_function_wrapper(prefix_onLoad)
	end

	function onIncrement()
		prefix_function_wrapper(prefix_onIncrement)
	end
end
