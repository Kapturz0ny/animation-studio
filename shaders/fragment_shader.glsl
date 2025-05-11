#version 330 core

out vec4 FragColor;

in vec3 FragPos;                           // Position of fragment in world space
in vec3 Normal;                            // Normal at the fragment position
// in vec2 TexCoord;                          // Texture coordinate (if used)

uniform vec3 light_position;               // Position of the light source
uniform vec3 viewPos;                      // Camera position
uniform vec3 objectColor;                  // Object color
uniform vec3 lightColor;                   // Light color

uniform vec3 material_ambient;             // Material ambient property
uniform vec3 material_diffuse;             // Material diffuse property
uniform float material_shininess;          // Material shininess

void main()
{
    // Ambient component
    vec3 ambient = material_ambient * lightColor;

    // Diffuse component (Lambertian reflectance)
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(light_position - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = material_diffuse * diff * lightColor;

    // Specular component (Phong model)
    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), material_shininess);
    vec3 specular = lightColor * spec;

    // Final color result
    vec3 result = ambient + diffuse + specular;
    FragColor = vec4(result * objectColor, 1.0);
}
