from manim import *
import argparse

class HilbertProjection(Scene):
    def construct(self):
        # Create a title
        title = Text("Hilbert Projection Theorem").scale(0.8)
        title.to_edge(UP)
        self.play(Write(title))
        
        # Create the coordinate system
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-3, 3, 1],
            x_length=6,
            y_length=6,
            axis_config={"include_tip": False}
        )
        self.play(Create(axes))

        # Create a convex set (we'll use a line segment for simplicity)
        # Using y = x line from (0,0) to (2,2) for clear visualization
        line_start = axes.c2p(0, 0)
        line_end = axes.c2p(2, 2)
        convex_set = Line(line_start, line_end, color=BLUE)
        convex_set_label = Text("C (Convex Set)", font_size=24, color=BLUE)
        convex_set_label.next_to(line_end, UR, buff=0.2)
        
        self.play(
            Create(convex_set),
            Write(convex_set_label)
        )

        # Point x (chosen to clearly show projection)
        point_coords = [1, -1]  # This point will have a clear projection
        point = Dot(axes.c2p(*point_coords), color=RED)
        point_label = Text("x", font_size=24, color=RED)
        point_label.next_to(point, DR, buff=0.1)
        
        self.play(
            Create(point),
            Write(point_label)
        )

        # Calculate projection point (closest point on line)
        # For a line y=x, projection of point (a,b) is ((a+b)/2, (a+b)/2)
        proj_coords = [(point_coords[0] + point_coords[1])/2] * 2
        proj_point = Dot(axes.c2p(*proj_coords), color=GREEN)
        proj_label = Text("p (Projection)", font_size=24, color=GREEN)
        proj_label.next_to(proj_point, UR, buff=0.1)

        # Draw projection line
        proj_line = Line(
            point.get_center(),
            proj_point.get_center(),
            color=YELLOW
        )
        
        self.play(
            Create(proj_point),
            Write(proj_label)
        )
        
        # Show the projection line
        self.play(Create(proj_line))

        # Demonstrate uniqueness and minimality
        # Create a few other points on the line to compare distances
        comparison_points = [
            [0.5, 0.5],
            [1.5, 1.5]
        ]
        
        for comp_coords in comparison_points:
            comp_point = Dot(axes.c2p(*comp_coords), color=YELLOW)
            comp_line = Line(
                point.get_center(),
                comp_point.get_center(),
                color=YELLOW
            ).set_opacity(0.3)
            
            # Show comparison distance
            self.play(
                Create(comp_point),
                Create(comp_line)
            )
            
            # Add length comparison
            orig_dist = Text(
                f"d = {np.sqrt(sum((a-b)**2 for a,b in zip(point_coords, proj_coords))):.2f}",
                font_size=24
            )
            comp_dist = Text(
                f"d = {np.sqrt(sum((a-b)**2 for a,b in zip(point_coords, comp_coords))):.2f}",
                font_size=24
            )
            orig_dist.to_edge(RIGHT)
            comp_dist.next_to(orig_dist, DOWN)
            
            self.play(
                Write(orig_dist),
                Write(comp_dist)
            )
            
            # Clear comparison
            self.play(
                FadeOut(comp_point),
                FadeOut(comp_line),
                FadeOut(orig_dist),
                FadeOut(comp_dist)
            )

        # Add a final note about orthogonality
        ortho_line = DashedLine(
            proj_point.get_center(),
            axes.c2p(2, 0),
            color=WHITE
        )
        ortho_text = Text(
            "Projection is orthogonal to C",
            font_size=24
        ).to_edge(DOWN)
        
        self.play(
            Create(ortho_line),
            Write(ortho_text)
        )
        
        # Let everything sink in
        self.wait(2)

        # Clean up
        self.play(
            *[FadeOut(mob) for mob in self.mobjects]
        )

def get_quality_config(quality='medium'):
    """Get manim quality configuration based on quality setting."""
    qualities = {
        'low': {
            'resolution': '854x480',
            'frame_rate': 15,
        },
        'medium': {
            'resolution': '1280x720',
            'frame_rate': 30,
        },
        'high': {
            'resolution': '1920x1080',
            'frame_rate': 60,
        },
        'ultra': {
            'resolution': '3840x2160',
            'frame_rate': 60,
        }
    }
    return qualities.get(quality, qualities['medium'])

if __name__ == "__main__":
    import platform
    if platform.system() == 'Darwin':  # macOS
        config.renderer = 'cairo'
        
    parser = argparse.ArgumentParser(description='Render Hilbert Projection Theorem animation')
    parser.add_argument('--quality', choices=['low', 'medium', 'high', 'ultra'], 
                      default='medium', help='Rendering quality')
    parser.add_argument('--no-preview', action='store_true', 
                      help='Disable preview after rendering')
    args = parser.parse_args()

    # Get quality configuration
    quality_config = get_quality_config(args.quality)
    
    # Configure and render
    with tempconfig({
        "frame_rate": quality_config['frame_rate'],
        "pixel_height": int(quality_config['resolution'].split('x')[0]),
        "pixel_width": int(quality_config['resolution'].split('x')[1]),
        "preview": not args.no_preview
    }):
        scene = HilbertProjection()
        scene.render()