prefix_executingEvents = {}
prefix_queuedEvents = {}

function execEvent(event_id)
	prefix_data_module:loadEvent(event_id)
	local event = prefix_EVENT_FILES[event_id]
	if event ~= nil then
		table.insert(prefix_executingEvents, {["events"] = event})
	else
		print("Trying to load non-existing event: " .. event_id)
	end
end

function enqueueEvent(event_id)
	prefix_data_module:loadEvent(event_id)
	local event = prefix_EVENT_FILES[event_id]
	if event ~= nil then
		table.insert(prefix_queuedEvents, {["events"] = event})
	else
		print("Trying to load non-existing event: " .. event_id)
	end
end

function prefix_execute_events(event_table, current_time)
	for time, events in pairs(event_table.events) do
		if type(time) == "number" then
			if ((event_table.done == nil) or not (time <= event_table.done)) and time <= current_time then
				event_table.done = current_time
				for i = 1, #events, 1 do
					loadstring(events[i])()
				end
			end
		end
	end
end

function prefix_update_event(event, frametime)
	if event.current_time == nil then
		event.current_time = 0
	end
	event.current_time = event.current_time + frametime / 60
	prefix_execute_events(event, event.current_time)
	for time, _ in pairs(event.events) do
		if type(time) == "number" then
			if time > event.current_time then
				return
			end
		end
	end
	return true
end

function prefix_update_events(frametime)
	local del_queue = {}
	for i=1, #prefix_executingEvents do
		local done = prefix_update_event(prefix_executingEvents[i], frametime)
		if #prefix_executingEvents == 0 then
			-- level changed
			return true
		end
		if done then
			table.insert(del_queue, 1, i)
		end
	end
	for _, i in pairs(del_queue) do
		table.remove(prefix_executingEvents, i)
	end
	if #prefix_queuedEvents ~= 0 then
		if prefix_update_event(prefix_queuedEvents[1], frametime) then
			table.remove(prefix_queuedEvents, 1)
		end
	end

	prefix_update_message_timeline(frametime)
	
	prefix_execute_events(prefix_MAIN_EVENTS, prefix_level_time)
end
