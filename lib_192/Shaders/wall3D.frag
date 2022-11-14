uniform vec4 color;
uniform float alpha_mult;
uniform float alpha_falloff;
const float color_mod = 256.0 / 255.0;


void main() {
	float new_alpha = alpha_mult == 0.0 ? 0.0 : color.a / alpha_mult;
	new_alpha -= alpha_falloff * (1.0 - gl_Color.a);
	gl_FragColor = color;
	gl_FragColor.a = mod(new_alpha, color_mod);
}
