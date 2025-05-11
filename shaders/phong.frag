#version 330

in vec3 FragPos;
in vec3 Normal;

out vec4 FragColor;

uniform vec3 light_position;
uniform vec3 viewPos;
uniform vec3 objectColor;
uniform vec3 lightColor;

uniform vec3 material_ambient;
uniform vec3 material_diffuse;
uniform float material_shininess;



void main()
{
	vec3 ambient = lightColor * material_ambient;
	
	vec3 N = normalize(Normal);
	vec3 L = normalize(light_position - FragPos);
	float cosNL = clamp(dot(N, L), 0.0, 1.0);
	
	vec3 diffuse = lightColor * material_diffuse * cosNL;

	vec3 V = normalize(viewPos - FragPos);
	vec3 R = reflect(FragPos - light_position, Normal);
	float cosVR = clamp(dot(V, R), 0.0, 1.0);
	
	vec3 specular = lightColor * material_shininess * cosVR; 
	
	vec3 phong_color = clamp(ambient + diffuse + specular, 0.0, 1.0);
	
	FragColor = vec4(phong_color*objectColor, 1.0);
}
