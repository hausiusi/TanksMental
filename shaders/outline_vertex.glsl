#version 330 core

// Vertex attributes
layout(location = 0) in vec3 vertex_position;
layout(location = 1) in vec2 uv_coords;

// Outputs to the fragment shader
out vec2 tex_coords;

uniform mat4 p3d_ModelViewProjectionMatrix;  // Projection matrix (Ursina passes this)

void main() {
    tex_coords = uv_coords;
    gl_Position = p3d_ModelViewProjectionMatrix * vec4(vertex_position, 1.0);
}
