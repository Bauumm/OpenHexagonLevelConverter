#version 130
uniform float hue;
uniform float pulse_factor;
uniform int swap;
uniform int sides;
const float color_mod = 256.f / 255.f;


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
	float s=1.f;
	float v=1.f;
	float r=0.f;
	float g=0.f;
	float b=0.f;
	int i=int(floor(mHue * 6.f));
	float f=mHue * 6.f - float(i);
	float p=v * (1.f - s);
	float q=v * (1.f - f * s);
	float t=v * (1.f - (1.f - f) * s);

	switch(int(i > 0.f ? mod(i, 6.f) : -mod(i, 6.f)))
	{
		case 0: r = v, g = t, b = p; break;
		case 1: r = q, g = v, b = p; break;
		case 2: r = p, g = v, b = t; break;
		case 3: r = p, g = q, b = v; break;
		case 4: r = t, g = p, b = v; break;
		case 5: r = v, g = p, b = q; break;
	}

	return vec4(r, g, b, 1.f);
}


vec4 calculateColor(ColorData color_data) {
	vec4 color = color_data.value;
	if(color_data.dynamic) {
		vec4 dynamic_color = getColorFromHue((hue + color_data.hue_shift) / 360.f);
		if(color_data.main) {
			color = dynamic_color;
		} else {
			if(color_data.dynamic_offset) {
				if(color_data.offset != 0.f) {
					color.rgb += dynamic_color.rgb / color_data.offset;
				}
				color.a += dynamic_color.a;
			} else {
				if(color_data.dynamic_darkness == 0.f) {
					dynamic_color.rgb = vec3(0.f, 0.f, 0.f);
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


int getIndex(vec4 color) {
	const float mults[] = float[4](255.f, 255.f * 256.f, 255.f * pow(256.f, 2.f), 255.f * pow(256.f, 3.f));
	return int(color.a * mults[0] + color.b * mults[1] + color.g * mults[2] + color.r * mults[3]);
}


void main() {
	int index = (getIndex(gl_Color) + swap) % colors.length();
	vec4 color = calculateColor(colors[index]) / (index % 2 == 0 && index == sides - 1 ? 1.4 : 1);
	gl_FragColor = color;
}
