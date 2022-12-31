u_execScript("color_calculations.lua")


function prefix_get_style_module()
	l_setManual3dPulseControl(true)
	s_setBGTileRadius(4500)

	local Style = {
		pulse3D = 1,
		pulse3DDirection = 1,
		wall_shader = shdr_getDependencyShaderId(prefix_DISAMBIGUATOR, "192_runtime", "Baum", "solid.frag"),
		hue_colors = setmetatable({}, {__index = function(self, k)
			local v = prefix_style_module:get_color_from_hue(k)
			self[k] = v
			return v
		end}),
		background_colors = {}
	}

	function Style:darken_color(color, darken_mult, copy)
		if copy then
			color = {unpack(color)}
		end
		darken_mult = darken_mult or (prefix_style["3D_darken_multiplier"] or 1.5)
		if darken_mult == 0 then
			color[1], color[2], color[3] = 0,0,0
		else
			for i=1,3 do
				color[i] = color[i] / darken_mult
			end
		end
		return color
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

		s_set3dDarkenMult(1)
		s_set3dAlphaMult(1)
		s_set3dAlphaFalloff(0)

		-- DM adjust negations
		local mult = u_getDifficultyMult() ^ 0.8
		s_setMaxSwapTime(s_getMaxSwapTime() * mult)
	end

	function Style:compute_colors()
		-- main
		self.main_color = self.calculation_methods[prefix_style.main.calculation_method](prefix_style.main, self.main_color)
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
		local limit = l_getSides() > #prefix_style.colors and #prefix_style.colors or l_getSides()
		for i=1, limit do
			local color = self.calculation_methods[prefix_style.colors[i].calculation_method](prefix_style.colors[i], self.background_colors[i])
			self.background_colors[i] = color
			if i % 2 == 0 and i == l_getSides() - 1 then
				self:darken_color(color, 1.4)
			end
			s_setOverrideColor((i - 1 + swap_offset) % #prefix_style.colors, unpack(color))
		end

		-- cap
		if #prefix_style.colors < 2 then
			cap_color = {0, 0, 0, 0}
		else
			local cap_index = (1 + swap_offset) % #prefix_style.colors + 1
			cap_color = self.background_colors[cap_index]
		end
		s_setCapOverrideColor(unpack(cap_color))

		-- 3d
		local override_color = prefix_style["3D_override_color"]
		if override_color == nil then
			override_color = self:darken_color(self.main_color, nil, true)
		else
			override_color = self:darken_color(override_color, nil, true)
		end
		local alpha_mult = prefix_style["3D_alpha_multiplier"] or 0.5
		if alpha_mult == 0 then
			override_color[4] = 0
		else
			override_color[4] = override_color[4] / alpha_mult
		end
		local alpha_falloff = prefix_style["3D_alpha_falloff"] or 3
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

	Style.calculation_methods = prefix_get_calculation_methods(Style)

	return Style
end
