if prefix_was_defined == nil then
	onInit()
	prefix_was_defined = true
	prefix_time_stop = 0
	prefix_died = false
	prefix_next_calls = 0
	prefix_next_time = 0
	prefix_remainder = 0
	u_execScript("prefix_styles.lua")
	u_execScript("prefix_main_timeline.lua")
	u_execScript("prefix_lua_functions.lua")
	u_execScript("prefix_events.lua")
	u_execScript("prefix_walls.lua")
	u_execScript("prefix_pulse.lua")
	u_execScript("prefix_rotation.lua")
	u_execScript("prefix_random.lua")

	-- wrap core functions to ignore errors and call custom event/timeline/style handlers
	function prefix_function_wrapper(func, arg)
		if func ~= nil then
			xpcall(func, print, arg)
		end
	end

	function onDeath()
		prefix_died = true
		l_setRotationSpeed(getLevelValueFloat("rotation_speed"))
		setLevelValueFloat("rotation_speed", 0)
	end

	function prefix_get_fps()
		-- estimate for standardised fps
		local walls = prefix_wall_module:size()
		local fps
		if walls < 1000 then
			fps = prefix_limit_fps
		else
			fps = prefix_limit_fps / (walls / 1000)
		end
		if fps < 60 then
			fps = 60
		end
		return fps
	end

	function onRenderStage(render_stage, frametime)
		if render_stage == 0 and prefix_next_calls > 0 then
			prefix_remainder = prefix_remainder + frametime
			local calls = math.floor(prefix_remainder / prefix_next_time)
			prefix_remainder = prefix_remainder - calls * prefix_next_time
			for i=1,calls do
				prefix_next_calls = prefix_next_calls - 1
				prefix_call_onUpdate(prefix_next_time)
			end
		end
	end

	function onInput(frametime, movement, focus)
		prefix_movement = movement
		prefix_focus = focus
		while prefix_next_calls >= 1 do
			prefix_call_onUpdate(prefix_next_time)
			prefix_next_calls = prefix_next_calls - 1
		end
		prefix_remainder = 0
		prefix_next_calls = prefix_next_calls + prefix_get_fps() / 240
		prefix_next_time = frametime / prefix_next_calls
		if movement ~= 0 then
			return true
		end
	end

	-- onStep should not be called by the game but by the custom timeline, so it isn't included here
	function prefix_call_onUpdate(frametime)
		if not prefix_died then
			prefix_wall_module:check_collisions(frametime, prefix_movement, prefix_focus)
			prefix_wall_module:update_walls(frametime)
			prefix_update_events(frametime)
			prefix_update_timeline(frametime)
			prefix_function_wrapper(prefix_onUpdate, frametime)
			prefix_pulse_module:update_beatpulse(frametime)
			prefix_pulse_module:update_pulse(frametime)
			prefix_style_module:update(frametime)
		end
		prefix_style_module:update3D(frametime)
		prefix_update_rotation(frametime)
		prefix_style_module:compute_colors()
	end

	function onUpdate(frametime)
		if prefix_time_stop > 0 then
			prefix_time_stop = prefix_time_stop - frametime
			u_haltTime(frametime)
		end
		prefix_update_initial_timestop(frametime)
	end

	function onPreUnload()
		prefix_is_unloading = true
		prefix_executingEvents = {}
		prefix_queuedEvents = {}
		prefix_clear_and_reset_timeline()
		prefix_function_wrapper(prefix_onUnload)
		prefix_update_events(0)
		if not u_inMenu() and prefix_level_changed then
			e_eval("prefix_seed = " .. prefix_seed)
			e_eval("prefix_change_level(\"" .. prefix_level_id .. "\", true)")
		end
	end

	function onUnload()
		prefix_is_retry = true
	end

	function onLoad()
		if not u_inMenu() then
			u_haltTime(-6)  -- undo timehalt the steam version adds by default
			setLevelValueFloat("rotation_speed", getLevelValueFloat("rotation_speed") * (math.random(0, 1) * 2 - 1))

			-- make font the same as 1.92
			u_setMessageFont("imagine.ttf")
			u_setMessageFontSize(40)

			prefix_style_module = prefix_get_style_module()
			prefix_style_module:init()
			prefix_pulse_module = prefix_get_pulse_module()
			prefix_pulse_module:init()
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
			a_playSound("go.ogg")
			a_setMusic(level_json.musicId)
			l_resetTime()
			onLoad()
		end
	end
end
