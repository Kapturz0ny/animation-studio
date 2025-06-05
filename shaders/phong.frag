#version 330

in vec3 FragPos;
in vec3 Normal;

struct Light {
    vec3 position;
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};

const int MAX_LIGHTS = 8;

uniform int numLights;
uniform Light lights[MAX_LIGHTS];

uniform vec3 material_ambient;
uniform vec3 material_diffuse;
uniform vec3 material_specular;
uniform float material_shininess;

uniform vec3 viewPos;
uniform vec3 objectColor;

out vec4 FragColor;

void main()
{
	vec3 N = normalize(Normal);
	vec3 V = normalize(viewPos - FragPos);

	vec3 result = vec3(0.0);

	for (int i = 0; i < numLights; ++i){

		vec3 ambient = lights[i].ambient * material_ambient;
		
		vec3 L = normalize(lights[i].position - FragPos);
		float cosNL = clamp(dot(N, L), 0.0, 1.0);
		
		vec3 diffuse = lights[i].diffuse * (cosNL * material_diffuse);

		
		// vec3 R = reflect(FragPos - light_position, Normal);
		vec3 R = reflect(-L, N);
		// float cosVR = clamp(dot(V, R), 0.0, 1.0);
		float spec = pow(max(dot(V, R), 0.0), material_shininess);

		//vec3 specular = light_shininess * material_shininess * cosVR; 
		vec3 specular = lights[i].specular * (spec * material_specular);

		result += ambient + diffuse + specular;
	
	}
	FragColor = vec4(clamp(result, 0.0, 1.0), 1.0);
}
