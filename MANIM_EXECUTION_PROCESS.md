self.document_store = document_store
self.context_selector = ContextSelector(document_store)
class DocumentStore:
    def __init__(self, docs_dir: str):
    def _load_documents(self):
    def get_document(self, filename: str) -> str:
class ContextSelector:
    def __init__(self, document_store: DocumentStore):
    def get_relevant_context(self, query: str, max_sections: int = 3) -> str:
context = self.context_selector.get_relevant_context(user_request)
- add this to the async def generate_manim_code_with_llm()

------

`python manim.py code.py Scene --opt` propagates through the system:

Processing begins in manimlib/config.py which handles command options and reads configuration from custom_default.yml.
manimlib/extract_scene.py main() extracts scene configurations (window_config, camera_config) and identifies scenes to render, with fallbacks for missing inputs (BlankScene) or unspecified scenes (user prompt).
Scene initialization in manimlib/scene/scene.py __init__() creates essential components (Camera, SceneFileWriter) and sets up the environment, including random seeds for reproducibility.
Scene generation creates an instance of the target scene class.
Execution flows through manimlib/__init__.py main() which calls run() on the scene instance.
manimlib/scene/scene.py run() executes the animation pipeline:

setup() prepares the environment
construct() contains the user-defined animation sequence
tear_down() handles cleanup


During rendering:

Camera continuously captures frames
play() and wait() methods realize animations
SceneFileWriter writes frames to partial movie files
Preview mode keeps window open until manually closed
Final rendering merges partial files into complete video

-----
Manim Technical Control Flow and Structure Reference
Execution Pipeline and Control Flow
Entry Point

Command: python manim.py code.py Scene --opt
Triggers loading of configuration and scene extraction

Configuration Processing (manimlib/config.py)

Function call: process_input_options(args, opts)

Processes CLI arguments including quality, preview mode, output formats


Function call: process_config(config_file)

Reads from custom_default.yml to load defaults
Parameters parsed: module, scene_names, window_config, camera_config, file_writer_config, preview


Config aggregation: combines CLI arguments with file-based configuration

Scene Extraction (manimlib/extract_scene.py:main())

Function call: extract_scene_configs(config_data)

Extracts: window_config, camera_config, and other scene-specific settings


BRANCH: File input validation

IF no file input → instantiate BlankScene
IF file exists but no Scene specified → prompt user for choice from available scenes


Function call: get_scenes_to_render(scene_classes, config_data)

Returns list of scene classes requiring rendering



Scene Initialization (manimlib/scene/scene.py:__init__())

Constructor arguments: camera_class=Camera, always_update_mobjects=True, random_seed=None, skip_animations=False
BRANCH: Preview mode

IF preview → create Window instance with scene dimensions


Instance creation:

camera = camera_class(**camera_config)
file_writer = SceneFileWriter(self, **file_writer_config)


Seed initialization:

random.seed(random_seed)
np.random.seed(random_seed)


Mouse event tracking setup (for interactive elements)

Scene Instance Generation

Function call: scene_class(**scene_kwargs)

Instantiates the targeted Scene subclass with configuration parameters
Prepares the scene for execution



Main Execution Entry (manimlib/__init__.py:main())

Function call: scene_instance.run()

Triggers the animation execution pipeline



Scene Execution (manimlib/scene/scene.py:run())

Function call: self.setup()

Prepares environment, camera, and rendering pipeline


Function call: self.construct()

PRIMARY USER CODE EXECUTION POINT
Contains animation definitions and sequences created by user


Function call: self.tear_down()

BRANCH: Output mode determination

IF preview → keep window open until user closes
IF video output → call file_writer to merge partial movie files





Critical Internal Functions
Animation Generation (play()):

Function call: self.play(*args, **kwargs)

Arguments: animation objects/mobjects, run_time, rate_func, lag_ratio
Process: transforms objects according to animation type
Camera captures frame sequence during animation
SceneFileWriter records frames to partial files



Timing Control (wait()):

Function call: self.wait(duration=1, stop_condition=None)

Creates pause between animations
Camera continues capturing static frames
SceneFileWriter records frames during waiting period



Object Management:

Function call: self.add(*mobjects)

Adds objects to scene without animation


Function call: self.remove(*mobjects)

Removes objects from scene


Function call: self.bring_to_front(*mobjects)

Changes z-index for visibility control



Camera Operations:

Frame management: self.camera.frame.animate.scale(factor)
Viewport control: self.camera.frame.animate.move_to(point)
Perspective changes: self.camera.frame.animate.rotate(angle)

SceneFileWriter Operations

Frame capturing: occurs during play() and wait() calls
Partial file generation: creates segments for each animation sequence
File merging: tear_down() triggers merge of all partial movie files
Storage path: determined by configuration and output settings

Critical Control Flow for Animation Creation

Scene class definition extends Scene
construct() method contains user animation code
Object creation establishes initial state
add() places objects in scene
play() executes animation transformations
wait() controls timing between animations
Camera captures frames throughout process
SceneFileWriter records and assembles final output

Conditional Branches Affecting Execution

Preview mode changes output destination and window behavior
Animation skipping for faster rendering (when skip_animations=True)
Quality settings affect resolution and rendering detail
Scene selection depends on command arguments or user prompts
File existence validation determines execution path

Common Arguments and Parameters

Animation duration: run_time=seconds
Animation speed: rate_func=linear/smooth/there_and_back
Camera settings: frame_width, frame_height, background_color
Object styling: color=COLOR, fill_opacity=0-1, stroke_width=pixels
Positioning: to_edge(direction), next_to(mobject, direction), move_to(point)
Transformations: shift(vector), scale(factor), rotate(angle)

System Component Interdependencies

Scene controls Camera and SceneFileWriter
Camera captures each frame based on current scene state
MObjects maintain their state and transform according to animations
SceneFileWriter receives frames from Camera and writes to disk
Window (in preview mode) displays Camera output in real-time