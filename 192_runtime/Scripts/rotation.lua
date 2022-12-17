function prefix_update_rotation(frametime)
	local next_rotation = math.abs(getLevelValueFloat("rotation_speed")) * 10 * frametime
	if prefix_fast_spin > 0 then
		next_rotation = next_rotation + math.abs((prefix_get_smoother_step(0, l_getFastSpin(), prefix_fast_spin) / 3.5) * frametime * 17)
		prefix_fast_spin = prefix_fast_spin - frametime
	end
	l_setRotation((l_getRotation() + next_rotation * prefix_sign(getLevelValueFloat("rotation_speed"))) % 360)
end
