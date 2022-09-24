#version 130
uniform sampler2D font;
uniform vec4 offset_color;
uniform vec4 text_color;

void main() {
	vec4 color = gl_Color.r + gl_Color.g + gl_Color.b + gl_Color.a == 0 ? text_color : offset_color;
	gl_FragColor = color * texture(font, gl_TexCoord[0].xy);
}
