function prefix_get_style_module()
	local Style = {
		shdr_wall3D = shdr_getShaderId("prefix_wall3D.frag"),
		shdr_wall = shdr_getShaderId("prefix_solid.frag")
	}

	function Style:darken_color(r, g, b, a)
		local darken_mult = s_get3dDarkenMult()
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
		s,v,r,g,b=1,1,0,0,0
		i = math.floor(hue * 6)
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
		return r,g,b,255
	end

	function Style:shader_scaling(color)
		return color[1] / 255, color[2] / 255, color[3] / 255, color[4] / 255
	end

	function Style:init()
		u_execScript("prefix_Styles/" .. prefix_style_id .. ".lua")
		if self.depth == nil then
			self.depth = s_get3dDepth()
		else
			s_set3dDepth(self.depth)
		end
		-- 3D alpha fixes
		for i=1,3 do  -- 1,2,3 are the RenderStages for the 3D layers
			shdr_setActiveFragmentShader(i, self.shdr_wall3D)
		end
		if prefix_style["3D_override_color"] ~= nil then
			local override_color = self:darken_color(unpack(prefix_style["3D_override_color"]))
			shdr_setUniformFVec4(self.shdr_wall3D, "color", self:shader_scaling(override_color))
		end
		self:set_3d_alpha_mult(s_get3dAlphaMult())
		self:set_3d_alpha_falloff(s_get3dAlphaFalloff())
		s_set3dAlphaMult(1)
		s_set3dAlphaFalloff(1)

		-- set wall color without needing to call cw_setVertexColor for every wall
		shdr_setActiveFragmentShader(4, self.shdr_wall)
		shdr_setUniformFVec4(self.shdr_wall, "color", self:shader_scaling({s_getMainColor()}))

		-- DM adjust negations
		local mult = u_getDifficultyMult() ^ 0.8
		s_setMaxSwapTime(s_getMaxSwapTime() * mult)
		s_setHueInc(s_getHueInc() / mult)
	end

	function Style:update()
		if prefix_style["3D_override_color"] == nil then
			local override_color = self:darken_color(s_getMainColor())
			shdr_setUniformFVec4(self.shdr_wall3D, "color", self:shader_scaling(override_color))
		end
		shdr_setUniformFVec4(self.shdr_wall, "color", self:shader_scaling({s_getMainColor()}))
	end

	function Style:set_style(id)
		s_setStyle(id)
		self:init()
	end

	function Style:set_3d_depth(depth)
		self.depth = depth
		s_set3dDepth(depth)
	end

	function Style:get_3d_depth()
		return self.depth
	end

	function Style:set_3d_spacing(spacing)
		s_set3dSpacing(spacing / 1.4)
	end

	function Style:get_3d_spacing()
		return s_get3dSpacing() * 1.4
	end

	function Style:set_3d_alpha_mult(mult)
		self.alpha_mult = mult
		shdr_setUniformF(self.shdr_wall3D, "alpha_mult", mult)
	end

	function Style:get_3d_alpha_mult()
		return self.alpha_mult
	end

	function Style:set_3d_alpha_falloff(falloff)
		self.alpha_falloff = falloff
		shdr_setUniformF(self.shdr_wall3D, "alpha_falloff", falloff)
	end

	function Style:get_3d_alpha_falloff()
		return self.alpha_falloff
	end

	return Style
end
