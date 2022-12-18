u_execScript("lua_functions.lua")
if prefix_was_defined == nil or u_inMenu() then
	prefix_LEVEL_PROPERTY_DEFAULTS = {
		pulse_min = 75,
		pulse_max = 80,
		pulse_speed = 0,
		pulse_speed_r = 0,
		pulse_delay_max = 0,
		beatpulse_max = 0,
		beatpulse_delay_max = 0,
		radius_min = 72
	}
	prefix_NOT_SET_IN_ONINIT = {
		id = true,
		name = true,
		description = true,
		author = true,
		menu_priority = true,
		selectable = true,
		difficulty_multipliers = true,
		style_id = true,
		music_id = true,
		lua_file = true
	}
	l_setShowPlayerTrail(false)
	l_setShadersRequired(true)
	prefix_was_defined = true
	prefix_level_time = 0
	prefix_died = false
	prefix_call_depth = 0
	prefix_finished_timehalt = false  -- artifical timehalt when stack overflow happens
	prefix_game_stopped = false
	prefix_stopped_time = 0
	prefix_block_offset = 0
	u_execScript("utils.lua")
	u_execScript("styles.lua")
	u_execScript("main_timeline.lua")
	u_execScript("events.lua")
	u_execScript("walls.lua")
	u_execScript("pulse.lua")
	u_execScript("rotation.lua")
	u_execScript("perfsim.lua")
	u_execScript("random.lua")
	u_execScript("timing_system.lua")
	u_execScript("persistent_storage.lua")
	prefix_persistent_storage = prefix_get_persistent_storage()
	prefix_timing_system = prefix_get_timing_system()

	-- wrap core functions to ignore errors and call custom event/timeline/style handlers
	function prefix_function_wrapper(func, arg)
		if func ~= nil then
			if prefix_quiet then
				pcall(func, arg)
			else
				xpcall(func, print, arg)
			end
		end
	end

	function onInit(skip_storage)
		if not prefix_persistent_storage.popped or u_inMenu() then
			local level_json = _G["prefix_level_json_" .. prefix_level_id]
			prefix_style_id = level_json.style_id
			a_syncMusicToDM(false)
			l_setIncEnabled(false)
			prefix_custom_keys = {}
			local ignore_defaults = {}
			for key, value in pairs(level_json) do
				if prefix_LEVEL_PROPERTY_DEFAULTS[key] ~= nil then
					ignore_defaults[key] = true
				end
				if not prefix_NOT_SET_IN_ONINIT[key] then
					prefix_setField("level", key, value)
				end
			end
			for key, value in pairs(prefix_LEVEL_PROPERTY_DEFAULTS) do
				if not ignore_defaults[key] then
					prefix_setField("level", key, value)
				end
			end
			if not skip_storage and not u_inMenu() then
				-- load the last attempts custom keys if they exist
				local keys = prefix_persistent_storage.pop(prefix_persistent_storage)
				local data = JSON:decode(keys)
				prefix_load_files(data.files)
				for k, v in pairs(data.level_values) do
					prefix_custom_keys[k] = v
				end
			end
			prefix_onInit()
		end
	end

	onInit(prefix_skip_storage)

	function onDeath()
		prefix_died = true
		l_setRotationSpeed(getLevelValueFloat("rotation_speed"))
		setLevelValueFloat("rotation_speed", 0)
	end

	function onRenderStage(render_stage, frametime)
		if prefix_kill_wall ~= nil then
			cw_destroy(prefix_kill_wall)
			prefix_kill_wall = nil
		end
		if render_stage == 0 and not prefix_game_stopped then
			prefix_timing_system:random_update(frametime)
		end
	end

	function prefix_stop_game(condition_func)
		prefix_block_condition = condition_func
		prefix_game_stopped = true
	end

	function onInput(frametime, movement, focus, swap)
		if prefix_finished_timehalt and not prefix_game_stopped then
			prefix_update_initial_timestop(frametime)
			prefix_timing_system:run_missing()
			prefix_movement = movement
			prefix_focus = focus
			prefix_swap = swap
			prefix_level_time = l_getLevelTime()
			prefix_timing_system:fixed_update(frametime)
		elseif prefix_game_stopped then
			prefix_movement = movement
			prefix_focus = focus
			prefix_swap = swap
			if not prefix_block_condition() then
				prefix_game_stopped = false
			else
				prefix_stopped_time = prefix_stopped_time + frametime
				prefix_block_offset = prefix_block_offset + frametime
				u_haltTime(frametime)
			end
		end
		if prefix_must_kill and prefix_kill_wall == nil then
			prefix_must_kill = false
			prefix_kill_wall = cw_create()
			cw_setDeadly(prefix_kill_wall, true)
			cw_setVertexPos4(prefix_kill_wall, -1600, 1600, -1600, -1600, 1600, -1600, 1600, 1600)
		end
		if movement ~= 0 then
			return true
		end
	end

	-- onStep should not be called by the game but by the custom timeline, so it isn't included here
	function prefix_call_onUpdate(frametime)
		if prefix_stopped_time > 0 then
			frametime = frametime + prefix_stopped_time
			prefix_stopped_time = 0
		end
		if frametime > 4 then
			frametime = 4
		end
		if not prefix_died then
			prefix_wall_module:move_player(frametime, prefix_movement, prefix_focus)
			prefix_wall_module:update_walls(frametime)
			prefix_wall_module:check_collisions(prefix_movement)
			if prefix_update_events(frametime) then
				-- level changed
				return
			end
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
		if not prefix_finished_timehalt then
			prefix_finished_timehalt = true
			l_resetTime()
			u_haltTime(-6)
		end
	end

	function onPreUnload()
		prefix_message_clear_timeline = ct_create()
		prefix_is_unloading = true
		prefix_executingEvents = {}
		prefix_queuedEvents = {}
		prefix_clear_and_reset_timeline()
		prefix_custom_keys = nil
		prefix_persistent_storage.popped = false
		onInit(true)
		local old_keys = {}
		for k, v in pairs(prefix_custom_keys) do
			old_keys[k] = v
		end
		prefix_function_wrapper(prefix_onUnload)
		prefix_update_events(0)
		if not u_inMenu() and prefix_level_changed then
			e_eval("prefix_change_level(\"" .. prefix_level_id .. "\", true)")
		end
		local data = {level_values = {}, files = prefix_dump_files()}
		for k, v in pairs(prefix_custom_keys) do
			if old_keys[k] ~= v then
				data.level_values[k] = v
			end
		end
		prefix_persistent_storage:store(JSON:encode(data))
	end

	function onUnload()
		prefix_is_retry = true
	end

	function onLoad()
		if not u_inMenu() then
			u_haltTime(-6)  -- undo timehalt the steam version adds by default
			setLevelValueFloat("rotation_speed", getLevelValueFloat("rotation_speed") * (math.random(0, 1) * 2 - 1))

			-- make font the same as 1.92
			u_setDependencyMessageFont(prefix_DISAMBIGUATOR, "192_runtime", "Baum", "imagine.ttf")
			u_setMessageFontSize(40)

			prefix_wall_module = prefix_get_wall_module()
			prefix_data_module = prefix_get_data_module()
			prefix_style_module = prefix_get_style_module()
			prefix_style_module:set_style(prefix_style_id)
			prefix_pulse_module = prefix_get_pulse_module()
			prefix_pulse_module:init()
			prefix_function_wrapper(prefix_onLoad)
			prefix_onLoad_done = true
		else
			l_setRotationSpeed(prefix_custom_keys.rotation_speed)
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
			e_messageAddImportantSilent("", 0)
			if prefix_is_retry then
				prefix_function_wrapper(prefix_onUnload)
			end
			prefix_wall_module:clear()
			prefix_message_timeline:clear()
			prefix_message_timeline:reset()
			prefix_shown_message = nil
			local level_json = _G["prefix_level_json_" .. id]
			s_setStyle(level_json.style_id)
			prefix_skip_storage = true
			prefix_level_id = nil
			u_execScript(level_json.prefix_lua_file)
			a_playSound("go.ogg")
			a_setMusic(level_json.music_id)
			l_resetTime()
			onLoad()
		end
	end
end
