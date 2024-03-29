inf = 1 / 0
prefix_EVENT_FILES = {}
u_execDependencyScript(prefix_DISAMBIGUATOR, "192_runtime", "Baum", "core_wrapper.lua")


-- small module to load events and styles which is invoked by the converter lib
function prefix_get_data_module()
	local data = {}

	function data:loadEvent(event_id)
		if prefix_EVENT_FILES[event_id] == nil then
			u_execScript("prefix_Events/" .. prefix_EVENT_ID_FILE_MAPPING[event_id] .. ".lua")
		end
	end

	function data:loadStyle(style_id)
		u_execScript("prefix_Styles/" .. prefix_STYLE_ID_FILE_MAPPING[style_id] .. ".lua")
	end

	return data
end
