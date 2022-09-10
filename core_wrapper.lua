if prefix_was_defined == nil then
	prefix_was_defined = true
	prefix_time_stop = 0
	if prefix_limit_fps ~= nil then
		prefix_target_tickrate = prefix_limit_fps / 240
		prefix_remainder = 0
	end
	u_execScript("prefix_styles.lua")
	u_execScript("prefix_main_timeline.lua")
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

	function onPreUnload()
		prefix_is_unloading = true
		prefix_executingEvents = {}
		prefix_queuedEvents = {}
		prefix_clear_and_reset_timeline()
		prefix_function_wrapper(prefix_onUnload)
		prefix_update_events(0)
		if not u_inMenu() and prefix_level_changed then
			e_eval("prefix_change_level(\"" .. prefix_level_id .. "\", true)")
		end
	end

	function onUnload()
		prefix_is_retry = true
	end

	function onLoad()
		if not u_inMenu() then
			u_haltTime(-6)  -- undo timehalt the steam version adds by default

			-- make font the same as 1.92
			u_setMessageFont("imagine.ttf")
			u_setMessageFontSize(40)

			prefix_initStyle()
			prefix_function_wrapper(prefix_onLoad)
		end
	end

	function onIncrement()
		prefix_function_wrapper(prefix_onIncrement)
	end

	function prefix_change_level(id, from_retry)
		if from_retry and not prefix_is_retry then
			return
		end
		prefix_level_changed = true
		if prefix_is_unloading then
			prefix_level_id = id
		else
			prefix_is_retry = false
			prefix_was_defined = nil
			prefix_3D_depth = nil
			prefix_limit_fps = nil
			e_messageAddImportantSilent("", 0)
			prefix_function_wrapper(prefix_onUnload)
			prefix_wall_module:clear()
			prefix_message_timeline:clear()
			prefix_message_timeline:reset()
			local level_json = _G["prefix_level_json_" .. id]
			s_setStyle(level_json.styleId)
			u_execScript(level_json.luaFile)
			onInit()
			a_playSound("go.ogg")
			a_setMusic(level_json.musicId)
			l_resetTime()
			onLoad()
		end
	end
end
