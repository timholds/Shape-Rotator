from manim import *

class SquareToCircle(Scene):
    def construct(self):
        # Create a square
        square = Square()

        # Display the square
        self.play(Create(square))

        # Transform the square into a circle
        self.play(Transform(square, Circle()))

        # Fade out
        self.play(FadeOut(square))