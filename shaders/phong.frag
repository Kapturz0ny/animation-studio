#version 330

in vec3 v_position;
in vec3 v_normal;

out vec4 fragColor;

uniform vec3 light_position;
uniform vec3 light_ambient;
uniform vec3 light_diffuse;
uniform vec3 light_specular;

uniform vec3 material_ambient;
uniform vec3 material_diffuse;
uniform float material_shininess;
uniform vec3 color;

uniform vec3 camera_position;

void main()
{
	vec3 ambient = light_ambient * material_ambient;
	
	vec3 N = normalize(v_normal);
	vec3 L = normalize(light_position - v_position);
	float cosNL = clamp(dot(N, L), 0.0, 1.0);
	
	vec3 diffuse = light_diffuse * material_diffuse * cosNL;

	vec3 V = normalize(camera_position - v_position);
	vec3 R = reflect(v_position - light_position, v_normal);
	float cosVR = clamp(dot(V, R), 0.0, 1.0);
	
	vec3 specular = light_specular * material_shininess * cosVR; 
	
	vec3 phong_color = clamp(ambient + diffuse + specular, 0.0, 1.0);
	
	fragColor = vec4(phong_color*color, 1.0);
}
