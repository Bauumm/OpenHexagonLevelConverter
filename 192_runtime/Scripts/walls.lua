function prefix_get_wall_module()
	local wall_module = {
		-- wall spawn distance in 1.92 cannot be changed
		WALL_SPAWN_DIST = 1600,
		WALL_DESPAWN_DIST = 1600,
		walls = {},
		duplicate_walls = {},
		duplicate_wall_count = 0,
		tmp_wall_data = {},
		stopped_walls = {},
		imaginary_walls = 0,
		stopped_wall_radius = 1 / 0,

		_getOrbit = function(degrees, distance)
			if type(degrees) == "table" then
				degrees = degrees.value
			end
			return math.cos((degrees / 57.3)) * distance,
			       math.sin((degrees / 57.3)) * distance
		end,

		_is_overlapping = function(verts, point)
			local result = false
			local vert_count = #verts / 2
			local j = vert_count - 1
			for i = 0, vert_count - 1 do
				local vI = {verts[i * 2 + 1], verts[i * 2 + 2]}
				local vJ = {verts[j * 2 + 1], verts[j * 2 + 2]}
				if (vI[2] > point[2]) ~= (vJ[2] > point[2]) and point[1] < (vJ[1] - vI[1]) * (point[2] - vI[2]) / (vJ[2] - vI[2]) + vI[1] then
					result = not result
				end
				j = i
			end
			return result
		end
	}

	function wall_module:size()
		return #self.walls + #self.stopped_walls + self.imaginary_walls + self.duplicate_wall_count
	end

	function wall_module:find_self()
		if self == nil then
			return prefix_wall_module
		end
		return self
	end

	function wall_module:wallAcc(side, thickness, speedAdj, acceleration, minSpeed, maxSpeed)
		self = prefix_wall_module.find_self(self)
		self:_wall(side, thickness, speedAdj * u_getSpeedMultDM(), acceleration, minSpeed * u_getSpeedMultDM(), maxSpeed * u_getSpeedMultDM())
	end

	function wall_module:wallAdj(side, thickness, speedAdj)
		self = prefix_wall_module.find_self(self)
		self:_wall(side, thickness, speedAdj * u_getSpeedMultDM(), 0, 0, 0)
	end

	function wall_module:wall(side, thickness)
		self = prefix_wall_module.find_self(self)
		self:_wall(side, thickness, u_getSpeedMultDM(), 0, 0, 0)
	end

	function wall_module:_wall(side, thickness, speed, acceleration, minSpeed, maxSpeed)
		side = prefix_round_to_even(side)
		if thickness ~= thickness then
			print("Not spawning wall with NaN thickness!")
			return
		end
		local side_count = l_getSides()
		local wall_angle_left = l_getWallAngleLeft()
		local wall_angle_right = l_getWallAngleRight()
		local wall_skew_left = l_getWallSkewLeft()
		local wall_skew_right = l_getWallSkewRight()
		local cw_handle = prefix_lookup_path(self.tmp_wall_data, {side_count, wall_angle_left, wall_angle_right, wall_skew_left, wall_skew_right, side, thickness, speed, acceleration, minSpeed, maxSpeed})
		if cw_handle ~= nil then
			if self.duplicate_walls[cw_handle] == nil then
				self.duplicate_walls[cw_handle] = {}
			end
			local cw = cw_createNoCollision()
			cw_setVertexPos4(cw, cw_getVertexPos4(cw_handle))
			table.insert(self.duplicate_walls[cw_handle], cw)
			self.duplicate_wall_count = self.duplicate_wall_count + 1
		else
			local wall = {cw=cw_createNoCollision()}
			prefix_insert_path(self.tmp_wall_data, {side_count, wall_angle_left, wall_angle_right, wall_skew_left, wall_skew_right, side, thickness, speed, acceleration, minSpeed, maxSpeed}, wall.cw)
			local div = prefix_float:new(360 / side_count)
			local angle = div * side
			cw_setVertexPos(wall.cw, 3, self._getOrbit(angle - div * 0.5, self.WALL_SPAWN_DIST))
			cw_setVertexPos(wall.cw, 2, self._getOrbit(angle + div * 0.5, self.WALL_SPAWN_DIST))
			cw_setVertexPos(wall.cw, 1, self._getOrbit(angle + div * 0.5 + wall_angle_left, self.WALL_SPAWN_DIST + thickness + wall_skew_left))
			cw_setVertexPos(wall.cw, 0, self._getOrbit(angle - div * 0.5 + wall_angle_right, self.WALL_SPAWN_DIST + thickness + wall_skew_right))
			wall.speed = speed
			wall.accel = acceleration
			wall.minSpeed = minSpeed
			wall.maxSpeed = maxSpeed
			table.insert(self.walls, wall)
		end
	end

	function wall_module:remove_duplicates(cw)
		if self.duplicate_walls[cw] ~= nil then
			self.duplicate_wall_count = self.duplicate_wall_count - #self.duplicate_walls[cw]
			for _, dup in pairs(self.duplicate_walls[cw]) do
				cw_destroy(dup)
			end
			self.duplicate_walls[cw] = nil
		end
	end

	function wall_module:update_duplicates(cw, x0, y0, x1, y1, x2, y2, x3, y3)
		if self.duplicate_walls[cw] ~= nil then
			for _, dup in pairs(self.duplicate_walls[cw]) do
				cw_setVertexPos4(dup, x0, y0, x1, y1, x2, y2, x3, y3)
			end
		end
	end

	function wall_module:empty()
		return self:size() == 0
	end

	function wall_module:clear()
		local length = #self.walls
		for i=1,length do
			cw_destroy(self.walls[1].cw)
			table.remove(self.walls, 1)
		end
	end

	function wall_module:move_player(frametime, movement, focus)
		local speed = focus and 4.625 or 9.45
		local last_angle = math.deg(u_getPlayerAngle())
		self.new_angle = last_angle + speed * movement * frametime
		self.radius = l_getRadiusMin() * (l_getPulse() / l_getPulseMin()) + l_getBeatPulse()
		self.last_player_pos = {self._getOrbit(last_angle, self.radius)}
		self.new_player_pos = {self._getOrbit(self.new_angle, self.radius)}
	end

	function wall_module:check_collisions(movement)
		if movement == 0 then
			if self.collides then
				prefix_must_kill = true
			end
		else
			if self.collides then
				if self.last_pos_now_kill then
					prefix_must_kill = true
				end
			else
				u_setPlayerAngle(math.rad(self.new_angle))
			end
		end
	end

	function wall_module:update_walls(frametime)
		self.tmp_wall_data = {}
		local delete_queue = {}
		local radius = self.radius * 0.65
		self.last_pos_now_kill = false
		self.collides = false
		for i=1,#self.walls do
			local moved_to_stopped = false
			local wall = self.walls[i]
			if wall.accel ~= 0 then
				wall.speed = wall.speed + wall.accel * frametime
				if wall.speed > wall.maxSpeed then
					wall.speed = wall.maxSpeed
				end
				if wall.speed < wall.minSpeed then
					wall.speed = wall.minSpeed
					if wall.minSpeed == 0 and wall.accel <= 0 then
						moved_to_stopped = true
						table.insert(self.stopped_walls, wall)
						table.insert(delete_queue, 1, i)
					end
				end
			end
			local points_on_center = 0
			local points_out_of_bg = 0
			local moved = false
			local wall_verts = {cw_getVertexPos4(wall.cw)}
			for i=1,8,2 do
				local x, y = wall_verts[i], wall_verts[i + 1]
				local abs_x, abs_y = math.abs(x), math.abs(y)
				if moved_to_stopped then
					self.stopped_wall_radius = math.min(abs_x, abs_y, self.stopped_wall_radius)
				end
				if abs_x < radius and abs_y < radius then
					points_on_center = points_on_center + 1
				elseif abs_x > self.WALL_DESPAWN_DIST and abs_y > self.WALL_DESPAWN_DIST then
					points_out_of_bg = points_out_of_bg + 1
				else
					local magnitude = math.sqrt(x ^ 2 + y ^ 2)
					local move_dist = wall.speed * 5 * frametime
					local new_x, new_y = x - x / magnitude * move_dist, y - y / magnitude * move_dist
					if (prefix_sign(new_x) ~= prefix_sign(x) or prefix_sign(new_y) ~= prefix_sign(y)) and wall.accel == 0 then
						points_on_center = points_on_center + 1
					end
					wall_verts[i] = new_x
					wall_verts[i + 1] = new_y
					moved = true
				end
			end
			self:update_duplicates(wall.cw, unpack(wall_verts))
			if moved then
				cw_setVertexPos4(wall.cw, unpack(wall_verts))
			end
			if self._is_overlapping(wall_verts, self.new_player_pos) then
				self.collides = true
			end
			if self._is_overlapping(wall_verts, self.last_player_pos) then
				self.last_pos_now_kill = true
			end
			if points_on_center > 3 or points_out_of_bg > 3 then
				if points_out_of_bg > 3 then
					self.imaginary_walls = self.imaginary_walls + 1
				end
				cw_destroy(wall.cw)
				self:remove_duplicates(wall.cw)
				if not moved_to_stopped then
					table.insert(delete_queue, 1, i)
				end
			end
		end
		for _, i in pairs(delete_queue) do
			table.remove(self.walls, i)
		end
		if self.stopped_wall_radius <= math.abs(self.radius) then
			self.stopped_wall_radius = 1 / 0
			local delete_queue = {}
			for i=1,#self.stopped_walls do
				local wall = self.stopped_walls[i]
				local points_on_center = 0
				local points_out_of_bg = 0
				local wall_verts = {cw_getVertexPos4(wall.cw)}
				for i=1,8,2 do
					local x, y = wall_verts[i], wall_verts[i + 1]
					local abs_x, abs_y = math.abs(x), math.abs(y)
					if abs_x < radius and abs_y < radius then
						points_on_center = points_on_center + 1
					elseif abs_x > self.WALL_DESPAWN_DIST and abs_y > self.WALL_DESPAWN_DIST then
						points_out_of_bg = points_out_of_bg + 1
					end
					self.stopped_wall_radius = math.min(abs_x, abs_y, self.stopped_wall_radius)
				end
				self:update_duplicates(wall.cw, unpack(wall_verts))
				if self._is_overlapping(wall_verts, self.new_player_pos) then
					self.collides = true
				end
				if self._is_overlapping(wall_verts, self.last_player_pos) then
					self.last_pos_now_kill = true
				end
				if points_on_center > 3 or points_out_of_bg > 3 then
					if points_out_of_bg > 3 then
						self.imaginary_walls = self.imaginary_walls + 1
					end
					cw_destroy(wall.cw)
					self:remove_duplicates(wall.cw)
					table.insert(delete_queue, 1, i)
				end
			end
			for _, i in pairs(delete_queue) do
				table.remove(self.stopped_walls, i)
			end
		end

		-- delete walls that were deleted for performance optimization when radius exceeds BGTileRadius
		-- may cause issues if far distant walls are not supposed to be deleted
		if self.radius > self.WALL_DESPAWN_DIST then
			self.imaginary_walls = 0
		end
	end

	return wall_module
end
