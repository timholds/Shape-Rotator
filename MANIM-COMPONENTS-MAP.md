MANIM-COMPONENTS-MAP
SCENE-HIERARCHY

Scene (base): class MyScene(Scene): def construct(self): ...
GraphScene: class MyGraph(GraphScene): setup_axes(self); plot_function(self, func, color=RED, x_min=-5, x_max=5)
ThreeDScene: self.set_camera_orientation(phi=75*DEGREES, theta=30*DEGREES)
VectorScene: self.play(ShowCreation(vector))
ZoomedScene: setup(); activate_zooming(); self.play(self.zoomable_mobjects[0].scale, 2)

MOBJECT-TYPES

Mobject (base): Mobject()
VMobject (vector): VMobject().set_points_as_corners([LEFT, RIGHT, UP])
Text: Text("Hello", font="Consolas").scale(0.5).to_edge(UP)
Tex/MathTex: MathTex(r"\int_{a}^{b} f(x) dx").set_color_by_tex("f", YELLOW)
ImageMobject: ImageMobject("image.png").scale_to_fit_width(5)
Group: VGroup(mob1, mob2).arrange(RIGHT, buff=0.2)
ValueTracker: tracker = ValueTracker(0); mob.add_updater(lambda m: m.next_to(tracker.get_value()*RIGHT, UP))

GEOMETRIC-MOBJECTS

Circle: Circle(radius=1.0, color=RED, fill_opacity=0.5)
Square: Square(side_length=2, fill_color=BLUE, fill_opacity=0.7)
Rectangle: Rectangle(height=2, width=4, color=GREEN)
Polygon: Polygon(ORIGIN, RIGHT, UP, color=PURPLE)
Triangle: Triangle().scale(2).shift(LEFT)
Line: Line(LEFT, RIGHT, color=WHITE)
Arrow: Arrow(ORIGIN, 2*UP+RIGHT)
DoubleArrow: DoubleArrow(LEFT, RIGHT, buff=0.1, tip_length=0.2)
Arc: Arc(radius=1, start_angle=0, angle=PI/2)
AnnularSector: AnnularSector(inner_radius=1, outer_radius=2, angle=TAU/4)
Dot: Dot(point=ORIGIN, radius=0.1, color=WHITE)
TangentLine: TangentLine(circle, alpha=0.5)
Elbow: Elbow()
CubicBezier: CubicBezier(a, b, c, d)

COORDINATE-SYSTEMS

Axes: Axes(x_range=[-5,5,1], y_range=[-3,3,1], axis_config={"include_tip": True})
NumberPlane: NumberPlane(x_range=[-10,10,1], y_range=[-5,5,1], background_line_style={"stroke_opacity": 0.6})
ThreeDAxes: ThreeDAxes(z_range=[-5,5,1])
ComplexPlane: ComplexPlane().add_coordinates()
NumberLine: NumberLine(x_range=[-5,5,1], include_numbers=True, unit_size=0.5)

ANIMATION-TYPES

Create/ShowCreation: self.play(Create(circle))
FadeIn/FadeOut: self.play(FadeIn(text, shift=UP))
Transform: self.play(Transform(mob1, mob2))
ReplacementTransform: self.play(ReplacementTransform(circle, square))
TransformMatchingShapes: self.play(TransformMatchingShapes(tex1, tex2))
Write: self.play(Write(text))
DrawBorderThenFill: self.play(DrawBorderThenFill(square))
Indicate: self.play(Indicate(dot))
Flash: self.play(Flash(point))
GrowFromCenter: self.play(GrowFromCenter(circle))
SpinInFromNothing: self.play(SpinInFromNothing(square))
FadeToColor: self.play(mob.animate.set_color(RED))
ScaleInPlace: self.play(mob.animate.scale(2))
MoveTo/Shift: self.play(mob.animate.move_to(ORIGIN)); self.play(mob.animate.shift(RIGHT*2))
TransformFromCopy: self.play(TransformFromCopy(source_mob, target_mob))
ApplyMethod: self.play(ApplyMethod(mob.set_width, 2))
CyclicReplace: self.play(CyclicReplace(mob1, mob2, mob3))
Rotate: self.play(Rotate(mob, angle=PI/2))
MoveToTarget: mob.generate_target(); mob.target.shift(RIGHT); self.play(MoveToTarget(mob))

UPDATER-PATTERNS

add_updater: mob.add_updater(lambda m, dt: m.rotate(dt))
ValueTracker+updater: alpha = ValueTracker(0); mob.add_updater(lambda m: m.move_to(path.point_from_proportion(alpha.get_value())))
remove_updater: mob.clear_updaters()
UpdateFromFunc: self.play(UpdateFromFunc(mob, lambda m: m.set_color(random_color())))
UpdateFromAlphaFunc: self.play(UpdateFromAlphaFunc(mob, lambda m, a: m.set_opacity(a)))

3D-OBJECTS

Sphere: Sphere(radius=1, resolution=(20,20))
Cube: Cube(side_length=2, fill_opacity=0.7)
Prism: Prism(dimensions=[1,2,3])
Cylinder: Cylinder(height=2, radius=1, resolution=(20,20))
Cone: Cone(base_radius=1, height=2, resolution=(20,20))
Line3D: Line3D(start=ORIGIN, end=RIGHT+UP+OUT)
Arrow3D: Arrow3D(ORIGIN, 2*RIGHT+UP)
ParametricSurface: ParametricSurface(lambda u,v: np.array([u,v,u*v]), u_range=[-1,1], v_range=[-1,1])
TexturedSurface: TexturedSurface(surface, texture_path="earth.jpg")

TEXT-STYLING

set_color: text.set_color(RED)
set_opacity: text.set_opacity(0.5)
add_background_rectangle: tex.add_background_rectangle(opacity=0.8, buff=0.1)
set_width/height: text.set_width(5); text.set_height(2)
SurroundingRectangle: SurroundingRectangle(text, buff=0.1, color=YELLOW)
Underline: Underline(text)
Brace: brace = Brace(text, direction=DOWN); brace_label = brace.get_text("label")
DecimalNumber: DecimalNumber(number=3.14159).set_color(YELLOW)
Integer: Integer(42)

CORE-METHODS

rotate: mob.rotate(angle=PI/2, axis=OUT)
flip: mob.flip(axis=RIGHT)
move_to: mob.move_to(ORIGIN+2*RIGHT)
shift: mob.shift(DOWN+RIGHT)
next_to: mob2.next_to(mob1, direction=RIGHT, buff=0.5)
align_to: mob2.align_to(mob1, UP)
get_center: point = mob.get_center()
get_corner: corner = mob.get_corner(UL)
set_z_index: mob.set_z_index(2)
add_to_back: self.add_to_back(background)
get_part_by_tex: term = tex.get_part_by_tex("x^2")
get_bounding_box: corners = mob.get_bounding_box()
become: mob1.become(mob2)

COMMON-CONSTANTS

Directions: UP, DOWN, LEFT, RIGHT, UR, UL, DR, DL, IN, OUT, ORIGIN
Colors: RED, GREEN, BLUE, WHITE, BLACK, YELLOW, ORANGE, PURPLE, PINK, GREY
Math: PI, TAU, DEGREES, RADIANS

LAYOUT-METHODS

arrange: VGroup(mob1, mob2, mob3).arrange(DOWN, center=False, aligned_edge=LEFT)
arrange_in_grid: VGroup(*[Circle() for _ in range(9)]).arrange_in_grid(3, 3, buff=0.2)
to_edge: mob.to_edge(UP, buff=0.5)
to_corner: mob.to_corner(UR, buff=0.5)
center: mob.center()
scale_to_fit_width: mob.scale_to_fit_width(5)
scale_to_fit_height: mob.scale_to_fit_height(3)
stretch: mob.stretch(factor=1.5, dim=0)

-----------------------------------------------

MANIM-COMPONENT-MAP-V2
CORE-CLASS-HIERARCHY
CopyScene
├─ GraphScene(x_min=-10,x_max=10,y_min=-5,y_max=5,axes_color=WHITE)
├─ ThreeDScene → self.set_camera_orientation(phi=75*DEGREES,theta=30*DEGREES)
├─ MovingCameraScene → self.camera_frame.scale(1.5).move_to(point)
└─ ZoomedScene → self.activate_zooming(animate=True)
ANIMATION-SEQUENCES
Copy# REVEAL_EQUATION
eq1 = MathTex(r"E = mc^2")
eq2 = MathTex(r"E", r"=", r"mc^2")
eq3 = MathTex(r"E", r"=", r"m", r"c^2")
self.play(Write(eq1))
self.wait(0.5)
self.play(TransformMatchingTex(eq1, eq2))
self.play(eq3[2].animate.set_color(BLUE), eq3[3].animate.set_color(RED))

# COORDINATE_TRANSFORMATION
axes = Axes(x_range=[-2,2], y_range=[-2,2])
graph = axes.plot(lambda x: x**2, x_range=[-2,2], color=BLUE)
point = Dot(axes.c2p(1, 1))
self.play(Create(axes), run_time=1)
self.play(Create(graph), run_time=2)
self.play(FadeIn(point))
self.play(point.animate.move_to(axes.c2p(2, 4)))

# ZOOMING_SEQUENCE
self.camera.frame.save_state()
self.play(self.camera.frame.animate.scale(0.5).move_to(target_point))
self.wait()
self.play(Restore(self.camera.frame))
MOBJECT-RELATIONSHIPS
Copy# HIERARCHY
parent = VGroup()
child1 = Square()
child2 = Circle().next_to(child1, RIGHT)
parent.add(child1, child2)
parent.move_to(ORIGIN) # moves entire group

# ALIGNMENT  
text = Text("Label")
box = Square()
text.next_to(box, UP, buff=0.1)
text.align_to(box, LEFT) # only aligns in x-direction
text.align_to(box, RIGHT) # only aligns in x-direction

# UPDATERS
dot = Dot()
line = Line(ORIGIN, RIGHT)
dot.add_updater(lambda d: d.move_to(line.get_end()))
self.add(line, dot)
self.play(line.animate.put_start_and_end_on(ORIGIN, 2*UP+RIGHT))
ERROR-PREVENTION-PATTERNS
Copy# PREVENT: Using undefined variable
try:
    mob = Circle()
    self.play(Create(mob))  # CORRECT
    # self.play(Create(undefined_mob))  # ERROR
except: pass

# PREVENT: Wrong animation target
try:
    square = Square()
    self.add(square)  # Object must exist in scene
    self.play(square.animate.shift(RIGHT))  # CORRECT
    # self.play(square.shift(RIGHT))  # ERROR: direct method call
except: pass

# PREVENT: Animation collision
try:
    dot = Dot()
    self.play(Create(dot))
    # Below simultaneously animates same object (collision):
    # self.play(dot.animate.shift(RIGHT), dot.animate.scale(2))  # ERROR
    # Correct approach:
    self.play(dot.animate.shift(RIGHT).scale(2))  # CORRECT
except: pass
PARAMETER-VALUE-RANGES
Copy# COLORS: RED,BLUE,GREEN,YELLOW,PURPLE,ORANGE,WHITE,BLACK,GREY,PINK
# COLOR_MAPS: "viridis","plasma","inferno","magma","cividis"

# OPACITIES
fill_opacity=0-1  # 0=transparent, 1=solid
stroke_opacity=0-1  # 0=invisible border, 1=visible border

# SIZES
radius=0.5-3  # for Circle, Dot
side_length=0.5-4  # for Square
height=0.5-5, width=0.5-7  # for Rectangle
stroke_width=1-8  # line thickness

# COORDINATES
ORIGIN=[0,0,0], LEFT=[-1,0,0], RIGHT=[1,0,0], UP=[0,1,0], DOWN=[0,-1,0]
UR=[1,1,0], UL=[-1,1,0], DR=[1,-1,0], DL=[-1,-1,0], OUT=[0,0,1], IN=[0,0,-1]

# ANGLES
PI=3.14159, TAU=2*PI, DEGREES=0.01745 # 1° in radians
# Usage: 45*DEGREES, PI/4, TAU/8 (all same angle)
ANIMATION-TIMING-CONTROL
Copy# RUN_TIME
self.play(Create(mob), run_time=2)  # default=1

# RATE_FUNCTIONS:
# linear = constant speed
# smooth = gentle easing in and out (DEFAULT)
# rush_from = start fast, end slow  
# rush_into = start slow, end fast
# there_and_back = goes to target and back
self.play(Create(mob), rate_func=smooth, run_time=2)

# MULTIPLE_ANIMATIONS_TIMING
self.play(
    Create(circle, run_time=2, rate_func=linear),
    FadeIn(square, run_time=1, rate_func=rush_from),
)
COORDINATE-SYSTEM-MANIPULATION
Copy# CONVERT_BETWEEN_COORDINATE_SYSTEMS
axes = Axes(x_range=[-5,5], y_range=[-3,3])
graph_point = axes.c2p(2, 4)  # coords to point: converts (2,4) to pixel position
coords = axes.p2c(graph_point)  # point to coords: converts pixel position to (2,4)

# ATTACH_OBJECTS_TO_GRAPH
axes = Axes(x_range=[-2,2], y_range=[0,4])
graph = axes.plot(lambda x: x**2)
dot = Dot().move_to(axes.c2p(1, 1))
dot.add_updater(lambda d: d.move_to(axes.c2p(
    t.get_value(), 
    t.get_value()**2
)))

# GET_GRAPH_POINTS
points = [axes.c2p(x, x**2) for x in np.linspace(-2, 2, 10)]
dots = VGroup(*[Dot(point, radius=0.05) for point in points])
MANIM-MATH-OBJECTS
Copy# COMMON_FUNCTIONS
graph1 = axes.plot(lambda x: np.sin(x), color=RED)
graph2 = axes.plot(lambda x: np.exp(x), color=BLUE)
graph3 = axes.plot(lambda x: np.log(x), x_range=[0.1, 5], color=GREEN)
graph4 = axes.plot(lambda x: np.sqrt(x), x_range=[0, 5], color=YELLOW)
parametric = ParametricFunction(
    lambda t: np.array([np.cos(t), np.sin(t), 0]),
    t_range=[0, TAU]
)

# INEQUALITIES
x_region = axes.get_area(graph, x_range=[0, 2])  # area under curve

# VECTOR_FIELDS
def func(p):
    x, y = p[:2]
    return np.array([y, -x, 0])
vector_field = VectorField(func, x_range=[-2, 2], y_range=[-2, 2])
COMPLEX-ANIMATION-PATTERNS
Copy# FADING_BETWEEN_SCENES
self.play(FadeOut(*self.mobjects))  # Clear everything

# HIGHLIGHT_THEN_REPLACE
self.play(Indicate(term))
self.play(ReplacementTransform(term, new_term))

# MOVING_FRAMES
self.camera_frame.save_state()
self.play(
    self.camera_frame.animate.scale(0.5).move_to(target)
)
self.wait()
self.play(Restore(self.camera_frame))


-----------------------------------------------
MANIMv3-COMPREHENSIVE-REFERENCE
SCENE-TYPES-HIERARCHY
CopyScene → self.play(Animation), self.wait(seconds), self.add(mobject), self.remove(mobject)
├─ GraphScene → self.setup_axes(), self.get_graph(func), self.coords_to_point(x,y)
│  └─ parameters: x_min=-10, x_max=10, y_min=-5, y_max=5, graph_origin=ORIGIN
├─ ThreeDScene → self.set_camera_orientation(phi=75*DEGREES, theta=30*DEGREES, zoom=0.5)
│  └─ self.begin_ambient_camera_rotation(rate=0.1), self.move_camera(phi=45*DEGREES)
├─ MovingCameraScene → self.camera.frame.scale(1.5).move_to(point)
│  └─ self.camera.frame.save_state(), self.play(Restore(self.camera.frame))
├─ ZoomedScene → self.activate_zooming(animate=True, zoom_factor=0.3)
│  └─ self.zoom_camera(new_zoom_factor, run_time=2)
├─ LinearTransformationScene → self.apply_matrix([[1,2],[3,4]], run_time=3)
└─ SampleSpace/PiCreatureScene → specialized animation scenes
MOBJECT-COMPOSITION-PATTERNS
Copy# NESTED_HIERARCHIES
outer_group = VGroup()
middle_group = VGroup()
inner_elements = VGroup(*[Square() for _ in range(3)]).arrange(RIGHT, buff=0.2)
middle_group.add(Text("Title"), inner_elements.next_to(Text("Title"), DOWN))
outer_group.add(middle_group, Circle().next_to(middle_group, RIGHT))
outer_group.move_to(ORIGIN)  # Moves entire nested structure

# COMPLEX_LAYOUTS
grid = VGroup()
for i in range(3):
    row = VGroup()
    for j in range(4):
        cell = Square(side_length=0.5).set_fill(opacity=0.5)
        label = Text(f"{i},{j}", font_size=24).scale(0.5)
        cell.add(label.move_to(cell.get_center()))
        row.add(cell)
    row.arrange(RIGHT, buff=0.1)
    grid.add(row)
grid.arrange(DOWN, buff=0.1)

# DYNAMIC_REFERENCES
circle = Circle()
dot = Dot()
line = always_redraw(lambda: Line(circle.get_center(), dot.get_center()))
self.add(circle, dot, line)
self.play(circle.animate.shift(RIGHT), dot.animate.shift(2*UP))
ANIMATION-SEQUENCES-TEMPLATES
Copy# EQUATION_DERIVATION
eq1 = MathTex(r"f(x) = x^2")
eq2 = MathTex(r"f'(x) = \lim_{h \to 0} \frac{f(x+h) - f(x)}{h}")
eq3 = MathTex(r"f'(x) = \lim_{h \to 0} \frac{(x+h)^2 - x^2}{h}")
eq4 = MathTex(r"f'(x) = \lim_{h \to 0} \frac{x^2 + 2xh + h^2 - x^2}{h}")
eq5 = MathTex(r"f'(x) = \lim_{h \to 0} \frac{2xh + h^2}{h}")
eq6 = MathTex(r"f'(x) = \lim_{h \to 0} (2x + h)")
eq7 = MathTex(r"f'(x) = 2x")
equations = [eq1, eq2, eq3, eq4, eq5, eq6, eq7]
for i in range(len(equations)-1):
    self.play(TransformMatchingTex(equations[i], equations[i+1]), run_time=2)
    self.wait(1)

# ZOOMING_SEQUENCE
def get_zoom_sequence(scene, target_point, zoom_factor=0.3):
    scene.camera.frame.save_state()
    scene.play(
        scene.camera.frame.animate.scale(zoom_factor).move_to(target_point),
        run_time=2
    )
    scene.wait()
    scene.play(Restore(scene.camera.frame), run_time=2)

# PARAMETRIC_JOURNEY
def parametric_journey(scene, curve, t_range=[0, 1], run_time=3):
    path = ParametricFunction(curve, t_range=t_range)
    dot = Dot().move_to(path.point_from_proportion(0))
    scene.add(path, dot)
    scene.play(MoveAlongPath(dot, path), run_time=run_time)
TEXT-MATHEMATICS-FORMATTING
Copy# TEX_TRANSFORMATIONS
tex1 = MathTex(r"e^{i\pi} + 1 = 0")
tex2 = MathTex(r"e^{i\pi}", r"+", r"1", r"=", r"0")
tex2[0].set_color(RED)
tex2[2].set_color(BLUE)
tex2[4].set_color(GREEN)
self.play(TransformMatchingTex(tex1, tex2), run_time=2)

# HIGHLIGHTING_PARTS
# Method 1: Set color by substring
equation = MathTex(r"E=mc^2", substrings_to_isolate=["E", "m", "c^2"])
equation.set_color_by_tex("E", RED)
equation.set_color_by_tex("m", GREEN)
equation.set_color_by_tex("c^2", BLUE)

# Method 2: Access by index
equation = MathTex(r"E=mc^2")
equation[0][0].set_color(RED)  # E
equation[0][2].set_color(GREEN)  # m
equation[0][3:5].set_color(BLUE)  # c^2

# LATEX_ENVIRONMENTS
aligned = MathTex(r"\begin{aligned} a &= b + c \\ &= d + e + f \\ &= g + h \end{aligned}")
cases = MathTex(r"f(x) = \begin{cases} x^2 & \text{if } x > 0 \\ x^3 & \text{if } x \leq 0 \end{cases}")
matrix = MathTex(r"A = \begin{bmatrix} a & b \\ c & d \end{bmatrix}")
GEOMETRY-CONSTRUCTION-TECHNIQUES
Copy# COMPLEX_SHAPES
star = RegularPolygon(5, start_angle=90*DEGREES).scale(2)
annular = AnnularSector(inner_radius=1, outer_radius=2, angle=270*DEGREES)
arrow = Arrow(start=ORIGIN, end=2*RIGHT+UP, buff=0, stroke_width=4)
doublearrow = DoubleArrow(start=LEFT, end=RIGHT, tip_length=0.2, stroke_width=5)
arc = Arc(radius=2, angle=PI/1.5, stroke_width=3)
elbow = Elbow(width=2, angle=PI/4)

# CUSTOM_SHAPES
custom_shape = VMobject()
custom_shape.set_points_as_corners([
    ORIGIN, RIGHT, RIGHT+UP, UP, ORIGIN
])
custom_curve = VMobject()
custom_curve.set_points([
    ORIGIN, 
    UP+RIGHT, UP+2*RIGHT, 2*UP+2*RIGHT,  # Control points for Bezier curve
    2*UP+3*RIGHT
])

# SHAPE_OPERATIONS
square = Square(side_length=2)
circle = Circle(radius=1)
# Cut circle from square
difference = Difference(square, circle, color=BLUE)
# Combine shapes
union = Union(square, circle.shift(RIGHT), color=GREEN)
# Intersection
intersection = Intersection(square, circle.move_to(square.get_corner(UR)/2), color=RED)
COORDINATE-SYSTEMS-GRAPHING
Copy# AXES_CONFIGURATION
axes = Axes(
    x_range=[-3, 3, 1],  # [min, max, step]
    y_range=[-2, 2, 0.5],
    x_length=6,  # width in screen units
    y_length=4,  # height in screen units
    axis_config={
        "color": BLUE,
        "include_tip": True,
        "numbers_to_exclude": [0],
    },
    x_axis_config={
        "numbers_to_include": range(-3, 4),
        "decimal_number_config": {"num_decimal_places": 0}
    },
    y_axis_config={
        "numbers_to_include": np.arange(-2, 2.5, 0.5),
        "decimal_number_config": {"num_decimal_places": 1}
    }
)

# PLOTTING_FUNCTIONS
# Single function
parabola = axes.plot(lambda x: x**2, x_range=[-2, 2], color=RED)
# Parametric function
circle_graph = axes.plot_parametric_curve(
    lambda t: np.array([np.cos(t), np.sin(t)]),
    t_range=[0, TAU],
    color=YELLOW
)
# Implicit curve (circle)
implicit_circle = axes.plot_implicit_curve(
    lambda x, y: x**2 + y**2 - 1,
    color=GREEN
)

# LABELING_GRAPHS
x_label = axes.get_x_axis_label("x")
y_label = axes.get_y_axis_label("f(x)")
graph_label = axes.get_graph_label(
    parabola, "f(x)=x^2", 
    x=2, direction=UR
)
point = Dot(axes.c2p(1, 1))
coordinates = MathTex("(1,1)").next_to(point, UR, buff=0.1)
3D-OBJECT-CREATION
Copy# 3D_PRIMITIVES
sphere = Sphere(radius=1, resolution=(20, 20))
cube = Cube(side_length=2, fill_opacity=0.8)
prism = Prism(dimensions=[2, 1, 3])
cylinder = Cylinder(height=3, radius=1)
cone = Cone(height=2, base_radius=1)

# 3D_SURFACES
def param_gauss(u, v):
    x = u
    y = v
    z = np.exp(-(x**2 + y**2)/2)
    return np.array([x, y, z])

gauss_surface = ParametricSurface(
    param_gauss,
    u_range=[-2, 2],
    v_range=[-2, 2],
    resolution=(30, 30),
    checkerboard_colors=[BLUE_D, BLUE_E]
)

# 3D_CAMERA_CONTROL
def setup_3d_scene(scene):
    scene.set_camera_orientation(phi=70*DEGREES, theta=30*DEGREES)
    scene.begin_ambient_camera_rotation(rate=0.1)
ANIMATION-MODIFIERS-TIMING
Copy# RATE_FUNCTIONS
rate_funcs = {
    "linear": lambda t: t,  # Constant speed
    "smooth": lambda t: 3*t**2 - 2*t**3,  # Ease in and out (default)
    "rush_from": lambda t: 2*t - t**2,  # Start fast, end slow
    "rush_into": lambda t: t**2,  # Start slow, end fast
    "slow_into": lambda t: np.sqrt(t),  # Very slow start
    "double_smooth": lambda t: smooth(t) if t < 0.5 else 1 - smooth(1 - t),  # Ease in, pause, ease out
    "there_and_back": lambda t: 1 - (2*t - 1)**2 if t < 0.5 else (2*t - 1)**2,  # Go and return
    "wiggle": lambda t: np.sin(8*t),  # Oscillating
}

# ANIMATION_TIMING
multi_anim = [
    FadeIn(obj1, rate_func=rate_funcs["rush_from"], run_time=1.5),
    GrowFromCenter(obj2, rate_func=rate_funcs["slow_into"], run_time=2),
    obj3.animate.shift(RIGHT*2), run_time=3, rate_func=rate_funcs["there_and_back"])
]
self.play(*multi_anim)

# STAGGERED_ANIMATIONS
dots = VGroup(*[Dot() for _ in range(5)]).arrange(RIGHT)
self.play(LaggedStart(
    *[dot.animate.shift(UP) for dot in dots],
    lag_ratio=0.2,  # Time gap between animations (0 to 1)
    run_time=3
))
UPDATERS-DYNAMIC-ELEMENTS
Copy# CUSTOM_CONTINUOUS_UPDATERS
dot = Dot()
line = Line(ORIGIN, RIGHT)
# Attach dot to end of line
dot.add_updater(lambda d: d.move_to(line.get_end()))
self.add(line, dot)
self.play(line.animate.put_start_and_end_on(ORIGIN, 2*UP+2*RIGHT))
# Remove updater
dot.clear_updaters()

# VALUE_TRACKER_CONTROL
alpha = ValueTracker(0)
dot = Dot().move_to(LEFT*3)
curve = ParametricFunction(
    lambda t: np.array([3*np.cos(t), 2*np.sin(t), 0]),
    t_range=[0, TAU]
)
# Position dot on curve based on alpha value
dot.add_updater(lambda d: d.move_to(curve.point_from_proportion(alpha.get_value())))
self.add(curve, dot)
self.play(alpha.animate.set_value(1), run_time=3)

# COMPLEX_UPDATER_EXAMPLE
# Value trackers
t = ValueTracker(0)
zoom = ValueTracker(1)
# Objects
axes = Axes(x_range=[-2, 2], y_range=[-1, 1])
graph = axes.plot(lambda x: np.sin(3*x), color=BLUE)
dot = Dot(color=RED)
# Connect dot to curve
dot.add_updater(lambda d: d.move_to(axes.c2p(t.get_value(), np.sin(3*t.get_value()))))
# Zoom camera based on value
self.camera.frame.add_updater(lambda f: f.set_scale(zoom.get_value()))
# Animate both values
self.add(axes, graph, dot)
self.play(t.animate.set_value(2), zoom.animate.set_value(0.5), run_time=5)
INTERACTIVE-OBJECTS-PATTERNS
Copy# DRAGGABLE_POINTS
def add_draggable_point(scene, position=ORIGIN, color=YELLOW):
    dot = Dot(position, color=color)
    # Here would be touch/mouse detection code for real interaction
    return dot

# SLIDERS
def create_slider(min_val=0, max_val=10, initial=5, width=4):
    line = Line(LEFT*width/2, RIGHT*width/2)
    tick_marks = VGroup(*[
        Line(UP*0.1, DOWN*0.1).move_to(line.point_from_proportion(i/10))
        for i in range(11)
    ])
    handle = Dot().scale(1.5)
    # Position handle based on initial value
    handle.move_to(line.point_from_proportion((initial-min_val)/(max_val-min_val)))
    return VGroup(line, tick_marks, handle)

# BUTTONS
def create_button(text="Click Me", width=2, height=0.75, color=BLUE, text_color=WHITE):
    box = Rectangle(width=width, height=height, fill_color=color, 
                   fill_opacity=0.8, stroke_color=WHITE)
    label = Text(text, color=text_color).scale(0.5).move_to(box.get_center())
    return VGroup(box, label)
ERROR-PREVENTION-TECHNIQUES
Copy# COMMON_ERROR_FIXES
# ERROR: AnimationGroup with conflicting animations on same object
# FIX: Combine animations for same object
circle = Circle()
# WRONG: self.play(circle.animate.shift(RIGHT), circle.animate.scale(2))
# CORRECT:
self.play(circle.animate.shift(RIGHT).scale(2))

# ERROR: Method called directly instead of using .animate
# WRONG: self.play(circle.shift(RIGHT))
# CORRECT: 
self.play(circle.animate.shift(RIGHT))

# ERROR: Referencing object before adding it to scene
# FIX: Add all objects before animating them
square = Square()
# CORRECT ORDER:
self.add(square)
self.play(square.animate.shift(UP))

# ERROR: Using Transform between incompatible objects
# FIX: Use ReplacementTransform or match structure
text1 = Text("Hello")
text2 = Text("World")
# CORRECT:
self.play(ReplacementTransform(text1, text2))

# ERROR: Using incompatible coordinate systems
# FIX: Convert between coord systems
axes = Axes()
# WRONG: circle.move_to(2, 3)  # These are axis values, not screen coordinates
# CORRECT:
circle.move_to(axes.c2p(2, 3))
ADVANCED-ANIMATIONS-REGISTRY
Copy# CREATION_ANIMATIONS
Create(mob)  # General creation
DrawBorderThenFill(mob)  # First border, then fill
Write(text)  # Text writing effect
AddTextLetterByLetter(text, time_per_letter=0.1)  # Slower text reveal
ShowCreation(mob)  # Legacy name for Create
FadeIn(mob, shift=UP)  # Fade in, optional direction

# MOVEMENT_ANIMATIONS
mob.animate.shift(direction)  # Move in direction
mob.animate.move_to(point)  # Move to absolute position
MoveAlongPath(mob, path)  # Follow a path
ApplyMethod(mob.method, *args)  # Apply any method

# INDICATION_ANIMATIONS
Indicate(mob)  # Brief highlight pulse
Flash(point)  # Quick radial flash effect
CircleIndicate(mob)  # Highlight with surrounding circle
ShowPassingFlash(mob)  # Traveling highlight
Wiggle(mob)  # Shake effect
Circumscribe(mob)  # Draw circle around

# TRANSFORMATION_ANIMATIONS
Transform(mob1, mob2)  # Transform mob1 into mob2 (mob1 remains)
ReplacementTransform(mob1, mob2)  # Transform and replace mob1 with mob2
TransformMatchingShapes(mob1, mob2)  # Transform matching parts
TransformMatchingTex(tex1, tex2)  # Transform matching TeX elements
ClockwiseTransform(mob1, mob2)  # Rotate clockwise during transform
CounterclockwiseTransform(mob1, mob2)  # Rotate counterclockwise

# GROUP_ANIMATIONS
AnimationGroup(*animations, lag_ratio=0)  # Group with specified lag
LaggedStart(*animations, lag_ratio=0.2)  # Group with automatic lag
Succession(*animations)  # Play one after another

# SPECIALIZED_ANIMATIONS
GrowFromCenter(mob)  # Scale from center
GrowFromPoint(mob, point)  # Scale from specific point
SpinInFromNothing(mob)  # Spin and grow
FadeToColor(mob, color)  # Change color
ShowIncreasingSubsets(group)  # Reveal group members one by one