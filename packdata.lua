u_execDependencyScript(prefix_DISAMBIGUATOR, "192_runtime", "Baum", "core_wrapper.lua")


-- small module to load events and styles which is invoked by the converter lib
function prefix_get_data_module()
	local data = {}

	function data:loadEvent(event_id)
		u_execScript("prefix_Events/" .. event_id .. ".lua")
	end

	function data:loadStyle(style_id)
		u_execScript("prefix_Styles/" .. style_id .. ".lua")
	end

	return data
end
