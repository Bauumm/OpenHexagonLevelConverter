if prefix_was_defined == nil then
	prefix_was_defined = true
	u_execScript("prefix_styles.lua")
	u_execScript("prefix_timeline.lua")
	u_execScript("prefix_lua_reimplementations.lua")
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
		prefix_is_incrementing = false
		prefix_function_wrapper(prefix_onIncrement)
	end
end
