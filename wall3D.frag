uniform vec4 color;
uniform float alpha_mult;
uniform float alpha_falloff;


void main() {
	float layer = 255.0 - gl_Color.a * 255.0;
	float new_alpha = color.a;
	if(alpha_mult == 0.0) {
		new_alpha = 0.0;
	} else {
		new_alpha /= alpha_mult;
	}
	new_alpha -= alpha_falloff * layer / 255.0;
	while(new_alpha < 0.0) {
		new_alpha += 1.0;
	}
	while(new_alpha > 1.0) {
		new_alpha -= 1.0;
	}
	gl_FragColor = color;
	gl_FragColor.a = new_alpha;
}
