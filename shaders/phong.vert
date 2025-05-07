#version 330

in vec3 position;
in vec3 normal;

uniform mat4 projection;
uniform mat4 view;
uniform mat4 M;

out vec3 v_position;
out vec3 v_normal;

void main()
{

	v_position = (M * vec4(position, 1.0)).xyz;
	v_normal = (M * vec4(normal, 0.0)).xyz;
	

    gl_Position = projection * view * M * vec4(position, 1.0);
}