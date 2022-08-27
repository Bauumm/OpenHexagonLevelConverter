prefix_message_clear_timeline = ct_create()
prefix_message_timeline = {}
prefix_message_remove_time = nil

function prefix_update_messages()
	if prefix_message_timeline[1] ~= nil then
		if prefix_message_remove_time == nil then
			prefix_message_remove_time = prefix_get_actual_time() + prefix_message_timeline[1]() / 60
		elseif prefix_message_remove_time <= prefix_get_actual_time() then
			e_messageAddImportantSilent("", 0)
			prefix_message_remove_time = nil
			table.remove(prefix_message_timeline, 1)
			prefix_update_messages()
		end
	end
end

function messageAdd(message, duration)
	table.insert(prefix_message_timeline, function()
		setMessage(message)
		return duration
	end)
end

function messageImportantAdd(message, duration)
	table.insert(prefix_message_timeline, function()
		setMessageImportant(message)
		return duration
	end)
end

function setMessage(str)
	if prefix_first_play then
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
