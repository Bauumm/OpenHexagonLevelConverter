prefix_message_clear_timeline = ct_create()
prefix_message_timeline = prefix_timeline:new()
prefix_shown_message = nil

function messageAdd(message, duration)
	prefix_message_timeline:append(prefix_t_do:new(prefix_message_timeline, function()
		if not prefix_is_retry then
			prefix_shown_message = message
		end
	end))
	prefix_message_timeline:append(prefix_t_wait:new(prefix_message_timeline, duration))
	prefix_message_timeline:append(prefix_t_do:new(prefix_message_timeline, function()
		prefix_shown_message = nil
	end))
end

function messageImportantAdd(message, duration)
	prefix_message_timeline:append(prefix_t_do:new(prefix_message_timeline, function()
		prefix_shown_message = message
	end))
	prefix_message_timeline:append(prefix_t_wait:new(prefix_message_timeline, duration))
	prefix_message_timeline:append(prefix_t_do:new(prefix_message_timeline, function()
		prefix_shown_message = nil
	end))
end

function prefix_set_message(str)
	e_messageAddImportant(str, 1)
	ct_eval(prefix_message_clear_timeline, "e_clearMessages()")
end

function prefix_update_message_timeline(frametime)
	prefix_message_timeline:update(frametime)
	if prefix_shown_message == nil then
		e_messageAddImportantSilent("", 0)
	else
		prefix_set_message(prefix_shown_message)
	end
	if prefix_message_timeline.finished then
		prefix_message_timeline:clear()
		prefix_message_timeline:reset()
	end
end
