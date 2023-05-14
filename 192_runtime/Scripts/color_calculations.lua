function prefix_get_calculation_methods(style)
	return {
		-- dynamic = false
		function(color, result)
			result = result or {}
			for i = 1, 4 do
				result[i] = style:component_clamp(color.value[i] + color.pulse[i] * style.pulse_factor)
			end
			return result
		end,

		-- dynamic = true
		-- main = true
		function(color, result)
			result = result or {}
			local dynamic_color = style.hue_colors[(style.hue + color.hue_shift) / 360]
			for i = 1, 4 do
				result[i] = style:component_clamp(dynamic_color[i] + color.pulse[i] * style.pulse_factor)
			end
			return result
		end,

		-- dynamic = true
		-- main = false
		-- dynamic_offset = true
		-- offset = 0
		function(color, result)
			result = result or {}
			for i = 1, 3 do
				result[i] = style:component_clamp(color.pulse[i] * style.pulse_factor)
			end
			result[4] = style:component_clamp((color.value[4] + 255) % 256 + color.pulse[4] * style.pulse_factor)
			return result
		end,

		-- dynamic = true
		-- main = false
		-- dynamic_offset = true
		function(color, result)
			result = result or {}
			local dynamic_color = style.hue_colors[(style.hue + color.hue_shift) / 360]
			for i = 1, 3 do
				result[i] = style:component_clamp(
					(color.value[i] + dynamic_color[i] / color.offset) % 256 + color.pulse[i] * style.pulse_factor
				)
			end
			result[4] = style:component_clamp((color.value[4] + 255) % 256 + color.pulse[4] * style.pulse_factor)
			return result
		end,

		-- dynamic = true
		-- main = false
		-- dynamic_offset = false
		-- dynamic_darkness = 0
		function(color, result)
			result = result or {}
			local dynamic_color = style.hue_colors[(style.hue + color.hue_shift) / 360]
			for i = 1, 3 do
				result[i] = style:component_clamp(color.pulse[i] * style.pulse_factor)
			end
			result[4] = style:component_clamp(255 + color.pulse[4] * style.pulse_factor)
			return result
		end,

		-- dynamic = true
		-- main = false
		-- dynamic_offset = false
		function(color, result)
			result = result or {}
			local dynamic_color = style.hue_colors[(style.hue + color.hue_shift) / 360]
			for i = 1, 3 do
				result[i] = style:component_clamp(
					(dynamic_color[i] / color.dynamic_darkness) % 256 + color.pulse[i] * style.pulse_factor
				)
			end
			result[4] = style:component_clamp(255 + color.pulse[4] * style.pulse_factor)
			return result
		end,
	}
end
