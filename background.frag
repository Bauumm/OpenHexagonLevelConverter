#version 130
uniform float hue;
uniform float pulse_factor;
uniform int swap;
const float color_mod = 256.0 / 255.0;


struct ColorData {
	bool dynamic;
	float dynamic_darkness;
	bool dynamic_offset;
	float offset;
	bool main;
	vec4 value;
	vec4 pulse;
	float hue_shift;
};


vec4 getColorFromHue(float mHue)
{
	float s=1.0;
	float v=1.0;
	float r=0.0;
	float g=0.0;
	float b=0.0;
	int i=int(floor(mHue * 6.0));
	float f=mHue * 6.0 - float(i);
	float p=v * (1.0 - s);
	float q=v * (1.0 - f * s);
	float t=v * (1.0 - (1.0 - f) * s);

	switch(int(i > 0.0 ? mod(i, 6.0) : -mod(i, 6.0)))
	{
		case 0: r = v, g = t, b = p; break;
		case 1: r = q, g = v, b = p; break;
		case 2: r = p, g = v, b = t; break;
		case 3: r = p, g = q, b = v; break;
		case 4: r = t, g = p, b = v; break;
		case 5: r = v, g = p, b = q; break;
	}

	return vec4(r, g, b, 1.0);
}


vec4 calculateColor(ColorData color_data) {
	vec4 color = color_data.value;
	if(color_data.dynamic) {
		vec4 dynamic_color = getColorFromHue((hue + color_data.hue_shift) / 360.0);
		if(color_data.main) {
			color = dynamic_color;
		} else {
			if(color_data.dynamic_offset) {
				if(color_data.offset != 0.0) {
					color.rgb += dynamic_color.rgb / color_data.offset;
				}
				color.a += dynamic_color.a;
			} else {
				if(color_data.dynamic_darkness == 0.0) {
					dynamic_color.rgb = vec3(0.0, 0.0, 0.0);
				} else {
					dynamic_color.rgb /= color_data.dynamic_darkness;
				}
				color = dynamic_color;
			}
			color = mod(color, color_mod);
		}
	}
	color.rgba += color_data.pulse.rgba * pulse_factor;
	return color;
}


int getIndex(vec4 color, float mult) {
	const float mults[] = float[3](255.0, 255.0 * 256.0, 255.0 * pow(256.0, 2.0));
	return int((color.a * mults[0] + color.b * mults[1] + color.g * mults[2]) * mult);
}


void main() {
	float mult = (gl_Color.r * 255.0 == 10.0 ? 1.4f : 1.0);
	int index = (getIndex(gl_Color, mult) + swap) % colors.length();
	vec4 color = calculateColor(colors[index]) / mult;
	gl_FragColor = color;
}
