function prefix_get_style_module()
	l_setManual3dPulseControl(true)
	s_setBGTileRadius(4500)

	local Style = {
		pulse3D = 1,
		pulse3DDirection = 1,
		wall_shader = shdr_getDependencyShaderId(prefix_DISAMBIGUATOR, "192_runtime", "Baum", "solid.frag")
	}

	function Style:darken_color(r, g, b, a)
		local darken_mult = s_get3dDarkenMult()
		if type(r) == "table" then
			darken_mult = g
			r,g,b,a = unpack(r)
		end
		if darken_mult == 0 then
			r,g,b = 0,0,0
		else
			r = r / darken_mult
			g = g / darken_mult
			b = b / darken_mult
		end
		return {r % 256, g % 256, b % 256, a % 256}
	end

	-- This is quite messy since it's copied from 1.92
	function Style:get_color_from_hue(hue)
		hue = prefix_float.round(hue)
		local s,v,r,g,b=1,1,0,0,0
		local i = math.floor(hue * 6)
		local f = hue * 6 - i
		local p,q,t=v * (1 - s), v * (1 - f * s), v * (1 - (1 - f) * s)
		local im
		if i >= 0 then
			im = i % 6
		else
			im = -(i % 6)
		end
		if im == 0 then r,g,b=v,t,p
		elseif im == 1 then r,g,b=q,v,p
		elseif im == 2 then r,g,b=p,v,t
		elseif im == 3 then r,g,b=p,q,v
		elseif im == 4 then r,g,b=t,p,v
		elseif im == 5 then r,g,b=v,p,q
		end
		r = math.modf(r * 255)
		g = math.modf(g * 255)
		b = math.modf(b * 255)
		return {r,g,b,255}
	end

	function Style:component_clamp(component)
		if component > 255 then
			return 255
		elseif component < 0 then
			return 0
		else
			return component
		end
	end

	function Style:calculate_color(color)
		local result = {unpack(color.value)}
		if color.dynamic then
			local dynamic_color = self:get_color_from_hue((self.hue + color.hue_shift) / 360)
			if color.main then
				result = dynamic_color
			else
				if color.dynamic_offset then
					if color.offset ~= 0 then
						for i=1,3 do
							result[i] = result[i] + dynamic_color[i] / color.offset
						end
					end
					result[4] = result[4] + dynamic_color[4]
				else
					result = self:darken_color(dynamic_color, color.dynamic_darkness)
				end
			end
		end
		for i=1,4 do
			result[i] = result[i] % 256
			result[i] = self:component_clamp(result[i] + color.pulse[i] * self.pulse_factor)
		end
		return result
	end

	function Style:init()
		shdr_resetActiveFragmentShader(4)
		shdr_setActiveFragmentShader(4, self.wall_shader)
		prefix_data_module:loadStyle(prefix_style_id)
		self.hue = prefix_style.hue_min
		self.pulse_factor = 0
		self.swap_time = 0
		if self.depth == nil then
			self.depth = s_get3dDepth()
		else
			s_set3dDepth(self.depth)
		end

		-- DM adjust negations
		local mult = u_getDifficultyMult() ^ 0.8
		s_setMaxSwapTime(s_getMaxSwapTime() * mult)
	end

	function Style:compute_colors()
		-- main
		self.main_color = self:calculate_color(prefix_style.main)
		shdr_setUniformFVec4(self.wall_shader, "color", unpack(self.main_color))
		s_setMainOverrideColor(unpack(self.main_color))
		s_setPlayerOverrideColor(unpack(self.main_color))
		s_setTextOverrideColor(unpack(self.main_color))

		-- background
		local swap_offset
		if prefix_style.max_swap_time == 0 then
			swap_offset = 0
		else
			swap_offset = math.modf(self.swap_time / (prefix_style.max_swap_time / 2))
		end
		local calculated_colors = {}
		for i=0,l_getSides() - 1 do
			local index = (i + swap_offset) % #prefix_style.colors + 1
			local color
			if calculated_colors[index] == nil then
				local color_obj = prefix_style.colors[index]
				color = self:calculate_color(color_obj)
				calculated_colors[index] = color
			else
				color = calculated_colors[index]
			end
			if i % 2 == 0 and i == l_getSides() - 1 then
				color = self:darken_color(color, 1.4)
			end
			s_setOverrideColor(i % #prefix_style.colors, unpack(color))
		end

		-- cap
		if #prefix_style.colors < 2 then
			cap_color = {0, 0, 0, 0}
		else
			local cap_index = (1 + swap_offset) % #prefix_style.colors + 1
			cap_color = calculated_colors[cap_index]
		end
		s_setCapOverrideColor(unpack(cap_color))

		-- 3d
		local override_color = prefix_style["3D_override_color"]
		if override_color == nil then
			override_color = self:darken_color(unpack(self.main_color))
		else
			override_color = self:darken_color(unpack(override_color))
		end
		local alpha_mult = s_get3dAlphaMult()
		if alpha_mult == 0 then
			override_color[4] = 0
		else
			override_color[4] = override_color[4] / alpha_mult
		end
		local alpha_falloff = s_get3dAlphaFalloff()
		for i=0, s_get3dDepth() - 1 do
			s_set3dLayerOverrideColor(i, unpack(override_color))
			override_color[4] = (override_color[4] - alpha_falloff) % 256
		end
	end

	function Style:update(frametime)
		self.swap_time = self.swap_time + frametime
		if self.swap_time > prefix_style.max_swap_time then
			self.swap_time = 0
		end
		self.hue = self.hue + prefix_style.hue_increment * frametime
		if self.hue < prefix_style.hue_min then
			if prefix_style.hue_ping_pong then
				self.hue = prefix_style.hue_min
				prefix_style.hue_increment = -prefix_style.hue_increment
			else
				self.hue = prefix_style.hue_max
			end
		end
		if self.hue > prefix_style.hue_max then
			if prefix_style.hue_ping_pong then
				self.hue = prefix_style.hue_max
				prefix_style.hue_increment = -prefix_style.hue_increment
			else
				self.hue = prefix_style.hue_min
			end
		end
		self.pulse_factor = self.pulse_factor + prefix_style.pulse_increment * frametime
		if self.pulse_factor < prefix_style.pulse_min then
			prefix_style.pulse_increment = -prefix_style.pulse_increment
			self.pulse_factor = prefix_style.pulse_min
		end
		if self.pulse_factor > prefix_style.pulse_max then
			prefix_style.pulse_increment = -prefix_style.pulse_increment
			self.pulse_factor = prefix_style.pulse_max
		end
	end

	function Style:update3D(frametime)
		self.pulse3D = self.pulse3D + prefix_style["3D_pulse_speed"] * self.pulse3DDirection * frametime
		if self.pulse3D > prefix_style["3D_pulse_max"] then
			self.pulse3DDirection = -1
		elseif self.pulse3D < prefix_style["3D_pulse_min"] then
			self.pulse3DDirection = 1
		end
		l_set3dPulse(self.pulse3D)
		-- Unused for now, as it seems to cause more issues than it's good
		--prefix_perfsim:update_3D()
	end

	function Style:set_style(id)
		prefix_style_id = id
		s_setStyle(id)
		self:init()
	end

	function Style:set_3D_depth(depth)
		if not prefix_onLoad_done then
			s_set3dDepth(depth)
			self.depth = depth
		end
	end

	function Style:set_3D_spacing(spacing)
		spacing = spacing or 0
		s_set3dSpacing(spacing / 1.4)
	end

	function Style:get_3D_spacing()
		return s_get3dSpacing() * 1.4
	end

	return Style
end
