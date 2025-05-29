#!/usr/bin/env python3.12
"""
A visualization of learning rate warmup using manim.
This script creates an animation to illustrate how learning rate warmup
helps in navigating the loss landscape during neural network training.
"""

from typing import Callable
import argparse
import numpy as np
from numpy.typing import NDArray
from manim import (
    ThreeDScene, ThreeDAxes, Surface, Text, VMobject, VGroup,
    DEGREES, BLUE_D, GREEN, YELLOW, RED, BLUE, UP, UR, DOWN, LEFT,
    Create, Write, config
)

class WarmupVisualization(ThreeDScene):
    """A manim scene that visualizes learning rate warmup concept."""
    
    def construct(self) -> None:
        """Construct and animate the scene."""
        # Set up the camera
        self.set_camera_orientation(phi=70 * DEGREES, theta=30 * DEGREES)
        
        def loss_surface(x: float, y: float, t: float = 0) -> float:
            """Generate the loss surface value at a point."""
            # Base quadratic bowl
            bowl = (x**2 + y**2) / 2
            # Add some non-convexity that reduces over time
            ridges = np.exp(-t) * (np.sin(2*x) * np.cos(2*y)) / 4
            return bowl + ridges

        # Create axes
        axes = ThreeDAxes(
            x_range=[-4, 4, 1],
            y_range=[-4, 4, 1],
            z_range=[0, 8, 1],
            x_length=8,
            y_length=8,
            z_length=4
        )

        # Create surface
        surface = Surface(
            lambda u, v: np.array([
                u,
                v,
                loss_surface(u, v, t=0)
            ]),
            u_range=[-4, 4],
            v_range=[-4, 4],
            resolution=(30, 30),
        )
        surface.set_opacity(0.7)
        surface.set_color_by_gradient(BLUE_D, GREEN, YELLOW)

        # Create title
        title = Text("Learning Rate Warmup Visualization", font_size=36)
        title.to_edge(UP)

        # Generate trajectories
        steps = 40
        lr_base = 0.3
        start_point = np.array([-3, -3, loss_surface(-3, -3, 0)])

        def generate_trajectory(use_warmup: bool) -> list[np.ndarray]:
            """Generate optimization trajectory with or without warmup."""
            trajectory = [start_point.copy()]
            current_point = start_point.copy()
            
            for i in range(steps):
                lr = lr_base * (i / steps) if use_warmup else lr_base
                grad_x = 2 * current_point[0] + 2 * np.cos(2*current_point[0]) * np.cos(2*current_point[1])
                grad_y = 2 * current_point[1] - 2 * np.sin(2*current_point[0]) * np.sin(2*current_point[1])
                
                current_point[0] -= lr * grad_x
                current_point[1] -= lr * grad_y
                current_point[2] = loss_surface(current_point[0], current_point[1])
                trajectory.append(current_point.copy())
            
            return trajectory

        # Generate both trajectories
        trajectory_no_warmup = generate_trajectory(use_warmup=False)
        trajectory_warmup = generate_trajectory(use_warmup=True)

        # Create path objects
        def create_path(trajectory: list[np.ndarray], color) -> VMobject:
            """Create a smooth path from trajectory points."""
            path = VMobject()
            path.set_points_smoothly([axes.coords_to_point(*point) for point in trajectory])
            path.set_color(color)
            return path

        path_no_warmup = create_path(trajectory_no_warmup, RED)
        path_warmup = create_path(trajectory_warmup, BLUE)

        # Create legend
        warmup_label = Text("With Warmup", color=BLUE, font_size=24)
        no_warmup_label = Text("No Warmup", color=RED, font_size=24)
        legend = VGroup(warmup_label, no_warmup_label).arrange(DOWN, aligned_edge=LEFT)
        legend.to_corner(UR)

        # Animation sequence
        self.add_fixed_in_frame_mobjects(title, legend)
        self.play(Create(axes))
        self.play(Create(surface))
        self.wait()
        
        self.play(
            Create(path_no_warmup),
            Create(path_warmup),
            run_time=3
        )
        self.wait()

        # Camera movement
        self.begin_ambient_camera_rotation(rate=0.2)
        self.wait(10)
        self.stop_ambient_camera_rotation()
        self.wait()

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate a visualization of learning rate warmup using manim"
    )
    parser.add_argument(
        "--quality", 
        type=str, 
        choices=["medium_quality", "high_quality", "production_quality", "fourk_quality"], 
        default="medium_quality",
        help="Rendering quality"
    )
    parser.add_argument(
        "--fps", 
        type=int, 
        default=30,
        help="Frames per second for the animation"
    )
    parser.add_argument(
        "--resolution", 
        type=str, 
        choices=["480p", "720p", "1080p", "2160p"], 
        default="720p",
        help="Output video resolution"
    )
    
    return parser.parse_args()

def get_resolution(res: str) -> tuple[int, int]:
    """Convert resolution string to width and height."""
    match res:
        case "480p":
            return 854, 480
        case "720p":
            return 1280, 720
        case "1080p":
            return 1920, 1080
        case "2160p":
            return 3840, 2160
        case _:
            raise ValueError(f"Unsupported resolution: {res}")

def main() -> None:
    """Main entry point for the visualization."""
    args = parse_args()
    
    # Configure manim settings
    width, height = get_resolution(args.resolution)
    
    # Update config individually as config.update doesn't accept kwargs
    config.quality = args.quality
    config.frame_rate = args.fps
    config.pixel_width = width
    config.pixel_height = height
    config.preview = True
    
    # Create and render the scene
    scene = WarmupVisualization()
    scene.render()

if __name__ == "__main__":
    main()