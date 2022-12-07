function prefix_get_persistent_storage()
	local storage = {}

	function storage:allocate(size)
		cw_clear()
		local current_size = 0
		local count = 0
		while current_size < size do
			while cw_create() ~= current_size do
				count = count + 1
			end
			current_size = count
		end
	end

	function storage:store(str)
		local space = math.ceil(#str / 8) + 1
		self:allocate(space)
		cw_setVertexPos4(0, #str, space, 0, 0, 0, 0, 0, 0)
		local nums = self:encode_str(str)
		for i=1,#nums % 8 do
			table.insert(nums, 0)
		end
		for i=1,space - 1 do
			local pos = i - 1
			cw_setVertexPos4(i, unpack(nums, pos * 8 + 1, pos * 8 + 8))
		end
	end

	function storage:pop()
		local test = cw_create()
		if test == 31 then
			cw_destroy(test)
			return "{level_values: {}, files: {}}"
		end
		local len, space = cw_getVertexPos(0, 0)
		local nums = {}
		for i=1,space - 1 do
			for _, num in pairs({cw_getVertexPos4(i)}) do
				table.insert(nums, num)
				if #nums == len then
					break
				end
			end
		end
		local str = self:decode_str(nums)
		cw_clear()
		return str
	end

	function storage:encode_str(str)
		local result = {}
		for char in str:gmatch"." do
			table.insert(result, string.byte(char))
		end
		return result
	end

	function storage:decode_str(bytes)
		local result = ""
		for _, byte in pairs(bytes) do
			result = result .. string.char(byte)
		end
		return result
	end

	return storage
end
