#version 330 core

in vec2 tex_coords;
out vec4 frag_color;

// Uniforms
uniform sampler2D tex;      
uniform vec4 outline_color; 
uniform float outline_width;

void main() {
    vec4 color = texture(tex, tex_coords);
    
    if (color.a == 0.0) {
        vec2 offsets[4] = vec2[](
            vec2(-outline_width, 0.0),  // Left
            vec2(outline_width, 0.0),   // Right
            vec2(0.0, -outline_width),  // Down
            vec2(0.0, outline_width)    // Up
        );

        for (int i = 0; i < 4; ++i) {
            vec4 neighbor_color = texture(tex, tex_coords + offsets[i]);
            if (neighbor_color.a > 0.0) {
                frag_color = vec4(1.0, 0.0, 0.0, 1.0);  // Debug: Render everything red

                //frag_color = outline_color;
                return;
            }
        }
    }
    
    frag_color = color; // Draw the original color if no outline is needed
}
