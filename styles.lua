prefix_shdr_wall3D = shdr_getShaderId("prefix_wall3D.frag")

function prefix_darken_color(r, g, b, a)
	local darken_mult = s_get3dDarkenMult()
	if darken_mult == 0 then
		r,g,b = 0,0,0
	else
		r = r / darken_mult
		g = g / darken_mult
		b = b / darken_mult
	end
	return {r, g, b, a}
end

function prefix_shader_scaling(r, g, b, a)
	return r / 255, g / 255, b / 255, a / 255
end

function prefix_get_3d_adjusted_main_color()
	if prefix_3D_depth >= 1 then
		-- the first layer exists which in 1.92 is blending directly with the main color
		local main_color = {s_getMainColor()}
		local alpha_sum = prefix_3d_override_color[4] + main_color[4]
		local new_color = {}
		for i=1,4 do
			new_color[i] = main_color[i] * main_color[4] / alpha_sum + prefix_3d_override_color[i] * prefix_3d_override_color[4] / alpha_sum
		end
		return unpack(new_color)
	else
		return s_getMainColor()
	end
end

function prefix_set_3d_depth(depth)
	prefix_3D_depth = depth
	s_set3dDepth(depth - 1)
end

function prefix_get_3d_depth()
	return prefix_3D_depth
end

function prefix_set_3d_spacing(spacing)
	s_set3dSpacing(spacing / 1.4)
end

function prefix_get_3d_spacing()
	return s_get3dSpacing() * 1.4
end

function prefix_initStyle()
	if prefix_3D_depth == nil then
		prefix_3D_depth = s_get3dDepth()
	else
		s_set3dDepth(prefix_3D_depth - 1)
	end
	-- 3D alpha fixes
	for i=1,3 do  -- 1,2,3 are the RenderStages for the 3D layers
		shdr_setActiveFragmentShader(i, prefix_shdr_wall3D)
	end
	if prefix_3D_colors[prefix_current_style] ~= nil then
		local color = prefix_3D_colors[prefix_current_style]
		prefix_3d_override_color = prefix_darken_color(unpack(color))
		shdr_setUniformFVec4(prefix_shdr_wall3D, "color", prefix_shader_scaling(unpack(prefix_3d_override_color)))
	end
	shdr_setUniformF(prefix_shdr_wall3D, "alpha_mult", s_get3dAlphaMult())
	shdr_setUniformF(prefix_shdr_wall3D, "alpha_falloff", s_get3dAlphaFalloff())
	s_set3dAlphaMult(1)
	s_set3dAlphaFalloff(1)

	-- DM adjust negations
	local mult = u_getDifficultyMult() ^ 0.8
	s_setMaxSwapTime(s_getMaxSwapTime() * mult)
	s_setHueInc(s_getHueInc() / mult)
end

function prefix_updateStyle()
	if prefix_3D_colors[prefix_current_style] == nil then
		prefix_3d_override_color = prefix_darken_color(s_getMainColor())
		shdr_setUniformFVec4(prefix_shdr_wall3D, "color", prefix_shader_scaling(unpack(prefix_3d_override_color)))
	end
end

function prefix_setStyle(id)
	prefix_current_style = id
	s_setStyle(id)
	prefix_initStyle()
end
