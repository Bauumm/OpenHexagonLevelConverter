function prefix_get_pulse_module()
	local Pulse = {}

	l_setManualPulseControl(true)
	l_setManualBeatPulseControl(true)

	function Pulse:init()
		-- pulse
		self.pulse = 75
		self.pulse_direction = 1
		self.pulse_delay = 0
		self.pulse_delay_half = 0
		l_setPulse(self.pulse)

		-- beatpulse
		self.beatpulse = 0
		self.beatpulse_delay = 0
		l_setBeatPulse(self.beatpulse)
	end

	function Pulse:update_pulse(frametime)
		if self.pulse_delay <= 0 and self.pulse_delay_half <= 0 then
			local pulse_add
			local pulse_limit
			if self.pulse_direction > 0 then
				pulse_add = l_getPulseSpeed()
				pulse_limit = l_getPulseMax()
			else
				pulse_add = -l_getPulseSpeedR()
				pulse_limit = l_getPulseMin()
			end
			self.pulse = self.pulse + pulse_add * frametime
			if (self.pulse_direction > 0 and self.pulse >= pulse_limit) or (self.pulse_direction < 0 and self.pulse <= pulse_limit) then
				self.pulse = pulse_limit
				self.pulse_direction = -self.pulse_direction
				self.pulse_delay_half = getLevelValueFloat("pulse_delay_half_max")
				if self.pulse_direction < 0 then
					self.pulse_delay = l_getPulseDelayMax()
				end
			end
			l_forceSetPulse(self.pulse)
		end
		self.pulse_delay = self.pulse_delay - frametime
		self.pulse_delay_half = self.pulse_delay_half - frametime
	end

	function Pulse:update_beatpulse(frametime)
		if self.beatpulse_delay <= 0 then
			self.beatpulse = l_getBeatPulseMax()
			self.beatpulse_delay = l_getBeatPulseDelayMax()
		else
			self.beatpulse_delay = self.beatpulse_delay - frametime
		end
		if self.beatpulse > 0 then
			self.beatpulse = self.beatpulse - 2 * frametime
		end
		l_forceSetBeatPulse(self.beatpulse)
	end

	return Pulse
end
