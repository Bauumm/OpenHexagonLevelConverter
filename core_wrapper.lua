if prefix_was_defined == nil then
	prefix_was_defined = true
	prefix_on_update_count = 0
	if prefix_limit_fps ~= nil then
		prefix_on_update_interval = 240 / prefix_limit_fps
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
			local wait_until = prefix_on_update_interval + prefix_remainder
			prefix_on_update_count = prefix_on_update_count + 1
			if prefix_on_update_count < math.floor(wait_until) then
				return
			end
			prefix_remainder = wait_until - math.floor(wait_until)
			frametime = frametime * prefix_on_update_count
			prefix_on_update_count = 0
		end
		xpcall(prefix_update_events, print)  -- in case some events do funny stuff
		prefix_updateStyle()
		prefix_update_timeline(frametime)
		prefix_function_wrapper(prefix_onUpdate, frametime)
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
