#version 330 core

layout (location = 0) in vec3 aPos;        // Position attribute
layout (location = 1) in vec3 aNormal;     // Normal attribute
// layout (location = 2) in vec2 aTexCoord;   // Texture coordinate attribute (if needed)

out vec3 FragPos;                          // Position of fragment (for lighting calculations)
out vec3 Normal;                           // Normal vector (for lighting calculations)
out vec2 TexCoord;                         // Pass texture coordinate to fragment shader (if used)

uniform mat4 M;                            // Model matrix
uniform mat4 view;                         // View matrix
uniform mat4 projection;                   // Projection matrix

void main()
{
    // Calculate the final position of the vertex by applying model, view, and projection transformations
    gl_Position = projection * view * M * vec4(aPos, 1.0);

    // Pass the fragment position and normal to the fragment shader
    FragPos = vec3(M * vec4(aPos, 1.0));  // Transform position to world space
    Normal = mat3(transpose(inverse(M))) * aNormal;  // Transform normal to world space
    // TexCoord = aTexCoord;                  // Pass texture coordinate
}
