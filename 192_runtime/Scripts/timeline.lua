function prefix_get_timeline_module()
	local Timeline = {}
	Timeline.__index = Timeline

	function Timeline:new()
		return setmetatable(
			{ ready = true, finished = false, commands = {}, current_command = nil, current_index = 1 },
			Timeline
		)
	end

	function Timeline:update(frametime)
		if self.finished then
			return
		end
		self.ready = true
		repeat
			if self.current_command == nil then
				self.finished = true
				self.ready = false
				break
			end
			self.current_command:update(frametime)
		until not self.ready
	end

	function Timeline:append(command)
		table.insert(self.commands, command)
		if self.current_command == nil then
			self.current_command = command
			self.current_index = #self.commands
		end
	end

	function Timeline:insert(index, command)
		table.insert(self.commands, index, command)
		if self.current_command == nil then
			self.current_command = command
			self.current_index = index
		end
	end

	function Timeline:reset()
		self:start()
		for _, command in pairs(self.commands) do
			command:reset()
		end
		if #self.commands ~= 0 then
			self.current_command = self.commands[1]
		else
			self.current_command = nil
		end
		self.current_index = 1
	end

	function Timeline:clear()
		self.current_command = nil
		self.current_index = 1
		self.commands = {}
		self.finished = true
	end

	function Timeline:start()
		self.finished = false
		self.ready = true
	end

	function Timeline:next()
		if self.current_command == nil then
			return
		end
		--self.current_index = self.current_index + 1
		table.remove(self.commands, self.current_index)
		self.current_command = self.commands[self.current_index]
	end

	function Timeline:get_current_index()
		if self.current_command == nil then
			return 1
		else
			if self.current_index > #self.commands then
				return -1
			end
			return self.current_index
		end
	end

	local Wait = {}
	Wait.__index = Wait

	function Wait:new(timeline, time)
		return setmetatable({ timeline = timeline, time = time or 0, current_time = time }, Wait)
	end

	function Wait:update(frametime)
		self.timeline.ready = false
		self.current_time = self.current_time - frametime
		if self.current_time - frametime > frametime then
			return
		end
		self.timeline:next()
		self:reset()
	end

	function Wait:reset()
		self.current_time = self.time
	end

	local Do = {}
	Do.__index = Do

	function Do:new(timeline, action)
		return setmetatable({ timeline = timeline, action = action }, Do)
	end

	function Do:update()
		self.action()
		self.timeline:next()
	end

	function Do:reset() end

	return Timeline, Wait, Do
end
