prefix_executingEvents = {}
prefix_queuedEvents = {}

function execEvent(event_id)
	u_execScript("prefix_Events/" .. event_id .. ".lua")
	table.insert(prefix_executingEvents, _G["prefix_" .. event_id .. "_EVENTS"])
end

function enqueueEvent(event_id)
	u_execScript("prefix_Events/" .. event_id .. ".lua")
	table.insert(prefix_queuedEvents, _G["prefix_" .. event_id .. "_EVENTS"])
end

function prefix_execute_events(event_table, current_time)
	for time, events in pairs(event_table) do
		if type(time) == "number" then
			for i = 1, #events, 1 do
				local event = events[i]
				if event ~= nil and time <= current_time then
					loadstring(event)()
					events[i] = nil
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
	for time, _ in pairs(event) do
		if type(time) == "number" then
			if time > event.current_time then
				return
			end
		end
	end
	event.done = true
end

function prefix_update_events(frametime)
	local del_queue = {}
	for i=1, #prefix_executingEvents do
		prefix_update_event(prefix_executingEvents[i], frametime)
		if prefix_executingEvents[i].done then
			table.insert(del_queue, 1, i)
		end
	end
	for _, i in pairs(del_queue) do
		table.remove(prefix_executingEvents, i)
	end
	if #prefix_queuedEvents ~= 0 then
		prefix_update_event(prefix_queuedEvents[1], frametime)
		if prefix_queuedEvents[1].done then
			table.remove(prefix_queuedEvents, 1)
		end
	end

	prefix_message_timeline:update(frametime)
	if prefix_message_timeline.finished then
		prefix_message_timeline:clear()
		prefix_message_timeline:reset()
	end
	
	prefix_execute_events(prefix_MAIN_EVENTS, prefix_level_time)
end
