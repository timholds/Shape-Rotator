from manim import *
import numpy as np

class LossLandscapeSharpness(Scene):
    def construct(self):
        # Create axes for both sharp and flat minima
        axes_sharp = Axes(
            x_range=[-4, 4, 1],
            y_range=[0, 8, 1],
            axis_config={"color": BLUE},
            x_length=6,
            y_length=4
        ).shift(LEFT * 3)

        axes_flat = Axes(
            x_range=[-4, 4, 1],
            y_range=[0, 8, 1],
            axis_config={"color": BLUE},
            x_length=6,
            y_length=4
        ).shift(RIGHT * 3)

        # Labels
        sharp_label = Text("Sharp Minimum\n(Large eigenvalue)", font_size=24).next_to(axes_sharp, UP)
        flat_label = Text("Flat Minimum\n(Small eigenvalue)", font_size=24).next_to(axes_flat, UP)

        # Create functions for sharp and flat minima
        def sharp_loss(x):
            return 2 * (x ** 2) + 1

        def flat_loss(x):
            return 0.5 * (x ** 2) + 1

        # Create graphs
        sharp_graph = axes_sharp.plot(sharp_loss, color=RED)
        flat_graph = axes_flat.plot(flat_loss, color=GREEN)

        # Add arrows to show eigenvalues/curvature
        sharp_arrows = VGroup()
        flat_arrows = VGroup()

        # Add arrows for sharp minimum
        for x in [-1, 1]:
            arrow = Arrow(
                start=axes_sharp.c2p(x, sharp_loss(x)),
                end=axes_sharp.c2p(x, sharp_loss(x) + 1),
                color=YELLOW,
                buff=0
            )
            sharp_arrows.add(arrow)

        # Add arrows for flat minimum
        for x in [-2, 2]:
            arrow = Arrow(
                start=axes_flat.c2p(x, flat_loss(x)),
                end=axes_flat.c2p(x, flat_loss(x) + 0.5),
                color=YELLOW,
                buff=0
            )
            flat_arrows.add(arrow)

        # Create tangent lines at minima
        sharp_tangent = Line(
            start=axes_sharp.c2p(-0.5, 1),
            end=axes_sharp.c2p(0.5, 1),
            color=BLUE_A
        )
        flat_tangent = Line(
            start=axes_flat.c2p(-0.5, 1),
            end=axes_flat.c2p(0.5, 1),
            color=BLUE_A
        )

        # Animation sequence
        self.play(Create(axes_sharp), Create(axes_flat))
        self.play(Write(sharp_label), Write(flat_label))
        self.play(Create(sharp_graph), Create(flat_graph))
        self.wait()

        # Show tangent lines
        self.play(Create(sharp_tangent), Create(flat_tangent))
        self.wait()

        # Show curvature arrows
        self.play(Create(sharp_arrows), Create(flat_arrows))
        self.wait()

        # Add explanation text
        explanation = Text(
            "The sharpness (top eigenvalue) indicates\nhow quickly the loss changes\nnear the minimum",
            font_size=24
        ).to_edge(DOWN)
        self.play(Write(explanation))
        self.wait(2)

if __name__ == "__main__":
    with tempconfig({"quality": "medium_quality", "preview": True}):
        scene = LossLandscapeSharpness()
        scene.render()