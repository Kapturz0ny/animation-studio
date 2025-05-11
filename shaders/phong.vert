#version 330

layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;

uniform mat4 projection;
uniform mat4 view;
uniform mat4 M;

out vec3 FragPos;
out vec3 Normal;

void main()
{

	FragPos = (M * vec4(aPos, 1.0)).xyz;
	Normal = (M * vec4(aNormal, 0.0)).xyz;
	

    gl_Position = projection * view * M * vec4(aPos, 1.0);
}