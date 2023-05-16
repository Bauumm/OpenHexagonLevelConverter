function prefix_get_timing_system()
	local timing_sys = {
		next_calls = 0,
		next_time = 0,
		remainder = 0,
		skipped_time = 0,
		skip_divider = 0,
		last_skip_divider = 1,
	}

	function timing_sys:random_update(frametime)
		if self.next_calls >= 1 then
			self.remainder = self.remainder + frametime
			local calls = math.floor(self.remainder / self.next_time)
			self.remainder = self.remainder - calls * self.next_time
			for i = 1, calls do
				if self.next_calls >= 1 then
					self.next_calls = self.next_calls - 1
					prefix_call_onUpdate(self.next_time)
				end
			end
		end
	end

	function timing_sys:run_missing()
		while self.next_calls >= 1 do
			self.next_calls = self.next_calls - 1
			prefix_call_onUpdate(self.next_time)
		end
	end

	function timing_sys:fixed_update(frametime)
		self.remainder = 0
		self.next_calls = self.next_calls + frametime / prefix_perfsim:get_target()
		if self.skip_divider ~= 0 then
			self.skipped_time = 0
		end
		if math.floor(self.next_calls) == 0 then
			self.skipped_time = self.skipped_time + frametime
			self.next_time = 0
			self.last_skip_divider = self.skip_divider
			if self.last_skip_divider < 1 then
				self.last_skip_divider = 1
			end
			self.skip_divider = 0
		else
			self.next_time = self.skipped_time / self.last_skip_divider + frametime / math.floor(self.next_calls)
			self.skip_divider = self.skip_divider + 1
		end
		if self.next_calls >= 1 then
			self.next_calls = self.next_calls - 1
			prefix_call_onUpdate(self.next_time)
		end
	end

	return timing_sys
end
