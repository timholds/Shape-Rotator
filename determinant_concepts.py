from manim import *
import numpy as np

class DeterminantConcepts(Scene):
    def construct(self):
        # Title
        title = Text("Determinants in Linear Algebra", font_size=48)
        self.play(Write(title))
        self.wait(2)
        self.play(FadeOut(title))
        
        # Part 1: 2D Determinant as Area Scaling
        self.show_2d_area_scaling()
        
        # Part 2: Specific Example (i-hat scaled by 3, j-hat by 2)
        self.show_specific_example()
        
        # Part 3: Zero Determinant
        self.show_zero_determinant()
        
        # Part 4: Negative Determinant (Orientation Flip)
        self.show_negative_determinant()
        
        # Part 5: Determinant Formula
        self.show_determinant_formula()
        
        # Part 6: 3D Determinant Preview
        self.show_3d_preview()

    def show_2d_area_scaling(self):
        # Create coordinate system
        plane = NumberPlane(
            x_range=[-4, 4, 1],
            y_range=[-4, 4, 1],
            background_line_style={
                "stroke_color": GREY,
                "stroke_width": 1,
                "stroke_opacity": 0.3
            }
        )
        
        # Unit square
        unit_square = Polygon(
            [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
            color=BLUE, fill_opacity=0.5, stroke_width=2
        )
        
        # Basis vectors
        i_hat = Arrow(ORIGIN, RIGHT, color=GREEN, buff=0)
        j_hat = Arrow(ORIGIN, UP, color=RED, buff=0)
        
        i_label = MathTex("\\hat{i}", color=GREEN).next_to(i_hat.get_end(), DOWN)
        j_label = MathTex("\\hat{j}", color=RED).next_to(j_hat.get_end(), LEFT)
        
        # Title for this section
        section_title = Text("Determinant = Area Scaling Factor", font_size=36).to_edge(UP)
        
        self.play(
            Create(plane),
            Write(section_title)
        )
        self.play(
            Create(unit_square),
            GrowArrow(i_hat),
            GrowArrow(j_hat),
            Write(i_label),
            Write(j_label)
        )
        self.wait(2)
        
        # Clear for next part
        self.play(
            FadeOut(plane), FadeOut(unit_square), 
            FadeOut(i_hat), FadeOut(j_hat),
            FadeOut(i_label), FadeOut(j_label),
            FadeOut(section_title)
        )

    def show_specific_example(self):
        # Create coordinate system
        plane = NumberPlane(
            x_range=[-1, 4, 1],
            y_range=[-1, 3, 1],
            background_line_style={
                "stroke_color": GREY,
                "stroke_width": 1,
                "stroke_opacity": 0.3
            }
        )
        
        # Original basis vectors and unit square
        i_hat_orig = Arrow(ORIGIN, RIGHT, color=GREEN, buff=0)
        j_hat_orig = Arrow(ORIGIN, UP, color=RED, buff=0)
        unit_square = Polygon(
            [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
            color=BLUE, fill_opacity=0.3, stroke_width=2
        )
        
        # Transformed vectors and parallelogram
        i_hat_new = Arrow(ORIGIN, 3*RIGHT, color=GREEN, buff=0)
        j_hat_new = Arrow(ORIGIN, 2*UP, color=RED, buff=0)
        parallelogram = Polygon(
            [0, 0, 0], [3, 0, 0], [3, 2, 0], [0, 2, 0],
            color=BLUE, fill_opacity=0.3, stroke_width=2
        )
        
        # Matrix representation
        matrix = MathTex(
            "\\begin{bmatrix} 3 & 0 \\\\ 0 & 2 \\end{bmatrix}",
            font_size=36
        ).to_corner(UL)
        
        det_text = MathTex("\\text{det} = 3 \\times 2 = 6", font_size=36).next_to(matrix, DOWN)
        
        # Title
        title = Text("Example: Scaling i-hat by 3, j-hat by 2", font_size=32).to_edge(UP)
        
        self.play(Create(plane), Write(title))
        self.play(
            Create(unit_square),
            GrowArrow(i_hat_orig),
            GrowArrow(j_hat_orig)
        )
        
        # Show area
        area_text = MathTex("\\text{Area} = 1", font_size=24).next_to(unit_square, RIGHT)
        self.play(Write(area_text))
        self.wait(1)
        
        # Transform
        self.play(Write(matrix))
        self.play(
            Transform(i_hat_orig, i_hat_new),
            Transform(j_hat_orig, j_hat_new),
            Transform(unit_square, parallelogram),
            area_text.animate.become(
                MathTex("\\text{Area} = 6", font_size=24).next_to(parallelogram, RIGHT)
            )
        )
        self.play(Write(det_text))
        self.wait(2)
        
        # Clear
        self.play(*[FadeOut(mob) for mob in self.mobjects])

    def show_zero_determinant(self):
        plane = NumberPlane(
            x_range=[-3, 3, 1],
            y_range=[-3, 3, 1],
            background_line_style={
                "stroke_color": GREY,
                "stroke_width": 1,
                "stroke_opacity": 0.3
            }
        )
        
        # Original vectors and square
        i_hat = Arrow(ORIGIN, RIGHT, color=GREEN, buff=0)
        j_hat = Arrow(ORIGIN, UP, color=RED, buff=0)
        unit_square = Polygon(
            [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
            color=BLUE, fill_opacity=0.3, stroke_width=2
        )
        
        # Transformation that squishes to a line
        matrix = MathTex(
            "\\begin{bmatrix} 2 & 1 \\\\ 4 & 2 \\end{bmatrix}",
            font_size=36
        ).to_corner(UL)
        
        det_text = MathTex("\\text{det} = 2(2) - 1(4) = 0", font_size=36).next_to(matrix, DOWN)
        
        title = Text("Zero Determinant: Squishing to Lower Dimension", font_size=32).to_edge(UP)
        
        self.play(Create(plane), Write(title))
        self.play(
            Create(unit_square),
            GrowArrow(i_hat),
            GrowArrow(j_hat)
        )
        self.play(Write(matrix))
        
        # Transform to line
        i_hat_new = Arrow(ORIGIN, 2*RIGHT + UP, color=GREEN, buff=0)
        j_hat_new = Arrow(ORIGIN, RIGHT + 0.5*UP, color=RED, buff=0)
        line = Line(ORIGIN, 3*RIGHT + 1.5*UP, color=BLUE, stroke_width=4)
        
        self.play(
            Transform(i_hat, i_hat_new),
            Transform(j_hat, j_hat_new),
            Transform(unit_square, line)
        )
        self.play(Write(det_text))
        
        warning_text = Text("All areas become 0!", color=YELLOW, font_size=24).next_to(line, DOWN)
        self.play(Write(warning_text))
        self.wait(2)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects])

    def show_negative_determinant(self):
        plane = NumberPlane(
            x_range=[-3, 3, 1],
            y_range=[-3, 3, 1],
            background_line_style={
                "stroke_color": GREY,
                "stroke_width": 1,
                "stroke_opacity": 0.3
            }
        )
        
        # Original configuration
        i_hat = Arrow(ORIGIN, RIGHT, color=GREEN, buff=0)
        j_hat = Arrow(ORIGIN, UP, color=RED, buff=0)
        
        # Labels that follow vectors
        i_label = MathTex("\\hat{i}", color=GREEN, font_size=24)
        j_label = MathTex("\\hat{j}", color=RED, font_size=24)
        i_label.add_updater(lambda m: m.next_to(i_hat.get_end(), DOWN, buff=0.1))
        j_label.add_updater(lambda m: m.next_to(j_hat.get_end(), LEFT, buff=0.1))
        
        # Orientation indicator (shows j is "left" of i initially)
        orientation_text = Text("j is LEFT of i", font_size=24, color=YELLOW).to_corner(UR)
        
        # Matrix that flips orientation
        matrix = MathTex(
            "\\begin{bmatrix} 0 & 1 \\\\ 2 & 0 \\end{bmatrix}",
            font_size=36
        ).to_corner(UL)
        
        det_text = MathTex("\\text{det} = 0(0) - 1(2) = -2", font_size=36).next_to(matrix, DOWN)
        
        title = Text("Negative Determinant: Orientation Flip", font_size=32).to_edge(UP)
        
        self.play(Create(plane), Write(title))
        self.play(
            GrowArrow(i_hat),
            GrowArrow(j_hat),
            Write(i_label),
            Write(j_label),
            Write(orientation_text)
        )
        self.play(Write(matrix))
        
        # Transform - i goes to j, j goes to 2i
        i_hat_new = Arrow(ORIGIN, UP, color=GREEN, buff=0)
        j_hat_new = Arrow(ORIGIN, 2*RIGHT, color=RED, buff=0)
        
        self.play(
            Transform(i_hat, i_hat_new),
            Transform(j_hat, j_hat_new),
            orientation_text.animate.become(
                Text("j is RIGHT of i (flipped!)", font_size=24, color=RED).to_corner(UR)
            )
        )
        self.play(Write(det_text))
        self.wait(2)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects if not isinstance(mob, VMobject) or mob not in [i_label, j_label]])

    def show_determinant_formula(self):
        title = Text("The 2×2 Determinant Formula", font_size=36).to_edge(UP)
        
        # General matrix
        matrix = MathTex(
            "\\begin{bmatrix} a & b \\\\ c & d \\end{bmatrix}",
            font_size=48
        ).shift(LEFT*3)
        
        # Formula
        formula = MathTex("\\text{det} = ad - bc", font_size=48).shift(RIGHT*2)
        
        self.play(Write(title))
        self.play(Write(matrix))
        self.play(Write(formula))
        self.wait(1)
        
        # Visual explanation for simple case (b=0)
        explanation = Text("When b=0: parallelogram becomes rectangle", font_size=24).shift(DOWN*2)
        area_calc = MathTex("\\text{Area} = a \\times d", font_size=36).shift(DOWN*3)
        
        self.play(Write(explanation))
        self.play(Write(area_calc))
        self.wait(2)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects])

    def show_3d_preview(self):
        title = Text("Extension to 3D: Volume Scaling", font_size=36).to_edge(UP)
        
        # 3D matrix example
        matrix_3d = MathTex(
            "\\begin{bmatrix} a & b & c \\\\ d & e & f \\\\ g & h & i \\end{bmatrix}",
            font_size=36
        ).shift(LEFT*3)
        
        # Note about 3D
        note = VGroup(
            Text("• Determinant measures volume scaling", font_size=24),
            Text("• Orientation determined by right-hand rule", font_size=24),
            Text("• det = 0 means squishing to plane/line/point", font_size=24)
        ).arrange(DOWN, aligned_edge=LEFT).shift(RIGHT*2)
        
        self.play(Write(title))
        self.play(Write(matrix_3d))
        self.play(Write(note))
        
        # Property: det(AB) = det(A)×det(B)
        property_text = MathTex(
            "\\text{Important: } \\det(AB) = \\det(A) \\times \\det(B)",
            font_size=32,
            color=YELLOW
        ).shift(DOWN*2.5)
        
        self.play(Write(property_text))
        self.wait(3)
        
        # End screen
        self.play(*[FadeOut(mob) for mob in self.mobjects])
        end_text = Text("Determinants: The scaling factor of space!", font_size=42)
        self.play(Write(end_text))
        self.wait(2)