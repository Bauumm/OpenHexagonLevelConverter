prefix_executingEvents = {}
prefix_queuedEvents = {}

function execEvent(event_id)
	if _G["prefix_" .. event_id .. "_EVENTS"] == nil then
		u_execScript("prefix_Events/" .. event_id .. ".lua")
	end
	table.insert(prefix_executingEvents, _G["prefix_" .. event_id .. "_EVENTS"])
end

function enqueueEvent(event_id)
	if _G["prefix_" .. event_id .. "_EVENTS"] == nil then
		u_execScript("prefix_Events/" .. event_id .. ".lua")
	end
	table.insert(prefix_queuedEvents, _G["prefix_" .. event_id .. "_EVENTS"])
end

function prefix_execute_events(event_table, current_time)
	for time, events in pairs(event_table) do
		if type(time) == "number" then
			for i = 1, #events, 1 do
				local event = events[i]
				if event ~= nil and time <= current_time then
					e_eval(event)
					events[i] = nil
				end
			end
		end
	end
end

function prefix_update_event(event)
	if event.current_time == nil then
		event.current_time = 0
		event.start_time = prefix_get_actual_time()
	end
	event.current_time = prefix_get_actual_time() - event.start_time
	prefix_execute_events(event, event.current_time)
	for time, _ in pairs(event) do
		if type(time) == "number" then
			if time > event.current_time then
				return
			end
		end
	end
	event.done = true
end

function prefix_update_events()
	for _, event in pairs(prefix_executingEvents) do
		prefix_update_event(event)
	end
	if #prefix_queuedEvents ~= 0 then
		prefix_update_event(prefix_queuedEvents[1])
		if prefix_queuedEvents[1].done then
			table.remove(prefix_queuedEvents, 1)
		end
	end
	prefix_execute_events(prefix_MAIN_EVENTS, prefix_get_actual_time())
end
