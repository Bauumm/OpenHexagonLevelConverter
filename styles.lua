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
	return r / 255, g / 255, b / 255, a / 255  -- pass the color into the shader properly
end


function prefix_initStyle()
	for i=1,3 do  -- 1,2,3 are the RenderStages for the 3D layers
		shdr_setActiveFragmentShader(i, prefix_shdr_wall3D)
	end
	if prefix_3D_colors[prefix_current_style] ~= nil then
		local color = prefix_3D_colors[prefix_current_style]
		shdr_setUniformFVec4(prefix_shdr_wall3D, "color", prefix_darken_color(color[1], color[2], color[3], color[4]))
	end
	shdr_setUniformF(prefix_shdr_wall3D, "alpha_mult", s_get3dAlphaMult())
	shdr_setUniformF(prefix_shdr_wall3D, "alpha_falloff", s_get3dAlphaFalloff())
	s_set3dAlphaMult(1)
	s_set3dAlphaFalloff(1)
end


function prefix_updateStyle()
	if prefix_3D_colors[prefix_current_style] == nil then
		shdr_setUniformFVec4(prefix_shdr_wall3D, "color", prefix_darken_color(s_getMainColor()))
	end
end


function prefix_setStyle(id)
	prefix_current_style = id
	s_setStyle(id)
	prefix_initStyle()
end
