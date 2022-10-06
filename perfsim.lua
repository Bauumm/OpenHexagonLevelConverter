prefix_perfsim = {factor_3D = 1}
prefix_perf_const = 60 / prefix_limit_fps
prefix_current_fps = 0
l_addTracked("prefix_current_fps", "FPS")


function prefix_perfsim:update_3D()
	local depth_factor = prefix_style_module.depth * 0.005 + 0.015
	if depth_factor > 0.035 then
		depth_factor = 0.035
	end
	local pulse_interval = prefix_style["3D_pulse_max"] - prefix_style["3D_pulse_min"]
	local max_factor_3D = (depth_factor * ((pulse_interval - prefix_style["3D_pulse_max"]) * s_get3dSkew() * 3.6 * s_get3dSpacing() * 1.4)) ^ 2
	self.factor_3D = 1 + (depth_factor * ((pulse_interval - prefix_style_module.pulse3D) * s_get3dSkew() * 3.6 * s_get3dSpacing() * 1.4)) ^ 2 - max_factor_3D
	if self.factor_3D > 1.2 then
		self.factor3D = 1.2
	elseif self.factor_3D < 1 then
		self.factor_3D = 1
	end
end


function prefix_perfsim:get_target()
	local wc = prefix_wall_module:size()
	local ft = ((0.785 * prefix_style_module.depth + 1) * (0.000461074 * prefix_perf_const + 0.000155698) * wc + prefix_perf_const * (0.025 * prefix_style_module.depth + 1))
	if 60 / ft > prefix_limit_fps then
		ft = 60 / prefix_limit_fps
	end
	if 60 / ft < 60 then
		ft = 1
	end
	prefix_current_fps = 60 / ft
	return ft
end
