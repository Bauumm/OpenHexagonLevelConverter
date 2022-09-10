prefix_message_clear_timeline = ct_create()
prefix_message_timeline = prefix_timeline:new()
prefix_message_remove_time = nil

function messageAdd(message, duration)
	prefix_message_timeline:append(prefix_t_do:new(prefix_message_timeline, function()
		setMessage(message)
	end))
	prefix_message_timeline:append(prefix_t_wait:new(prefix_message_timeline, duration))
	prefix_message_timeline:append(prefix_t_do:new(prefix_message_timeline, function()
		e_messageAddImportantSilent("", 0)
	end))
end

function messageImportantAdd(message, duration)
	prefix_message_timeline:append(prefix_t_do:new(prefix_message_timeline, function()
		setMessageImportant(message)
	end))
	prefix_message_timeline:append(prefix_t_wait:new(prefix_message_timeline, duration))
	prefix_message_timeline:append(prefix_t_do:new(prefix_message_timeline, function()
		e_messageAddImportantSilent("", 0)
	end))
end

function setMessage(str)
	if not prefix_is_retry then
		setMessageImportant(str)
		return
	end
	e_messageAdd(str, 1)
	ct_wait(prefix_message_clear_timeline, 1)
	ct_eval(prefix_message_clear_timeline, "e_clearMessages()")
end

function setMessageImportant(str)
	e_messageAddImportant(str, 1)
	ct_wait(prefix_message_clear_timeline, 1)
	ct_eval(prefix_message_clear_timeline, "e_clearMessages()")
end
