
Things to try:
Fine tuning a llama


[X] frontend to accept user input
[ ] frontend to query an API
[ ] API to succesfully manim videos 
[ ] frontend to display the video
[ ] fine tune an open source model - how do i create an SFT dataset
[ ]



[ ] TODO transfer over manim wishlist from other repo
[ ] TODO start yt channel?

# Prompt purgatory
What are some simple but nontrivial and intuitive examples of vector spaces


Want a visualization of how the parameter for weight decay (lambda) shrinks the weights towards zero. relationship between this and l2 regularization and the visualization of how and why l1 gives sparse solutions while l2 does not (or do I have that backwards? See, it's because I don't have good intuition)

[ ] Add LLM call to update/convert any given 3blue1brown piece of manim code to work with the open source version of manim instead of the private one?
-> otherwise will be helping it generate the wrong code!

# Setup
For using manimgl (3b1b's private manim) rather than the open source version of manim:
pip install manimgl
pip install setuptools
add manim_imports_ext.py to root
Add custom folder with the required files

On linux instructions here https://manim.readthedocs.io/en/latest/installation/linux.htmlhttps://manim.readthedocs.io/en/latest/installation/linux.html:
- `sudo apt install libpango1.0-dev pkg-config python3-dev`  
- `sudo apt install sox ffmpeg libcairo2 libcairo2-dev`  
- `sudo apt install texlive-full`  
    - install was getting stuck so had to hold down enter until it unstuck per the advice here https://askubuntu.com/questions/956006/pregenerating-context-markiv-format-this-may-take-some-time-takes-forever
- getting error about "OSError: libGL.so: cannot open shared object file: No such file or directory
", fixed by running `sudo apt-get install freeglut3-dev`  

[ ] TODO add a custom_config.yml to control font, add custom images

# Daily
Running into all sorts of errors trying to run the manim demo scene without any changes 
- "Exception: cannot create OpenGL context"

# Fine Tuning

# In-context Learning

# RAG system
This might be interesting information to add - basically high level structure information https://3b1b.github.io/manim/getting_started/example_scenes.html


# Background
One common meditation practice in Vajrayana Buddhism involves picturing complex, geometrically detailed, fractal-like deity figures. The practicioner sits for minutes or even hours, holding the image in full 3d dimensions in their head, examining and relaxing into perfect concentrative witnessing, effortless examination that lets one see all the angles simultaneously. 

Being a subset of Mahāyāna Buddhism,

As the complexity of the figure grows with the skill of the meditator, a certain type of mental relaxation becomes a prerequisite for actually picturing the thing. To perceive all the subtle facets of the shape as it slowly rotates before you, you need have a familiarity with the territory. 

However, you *also* need to relax a bit to perceive the gestalt and finally hold all of its complexities in a way that isn't so mentally taxing. Think phase collapse with DMT or hyperbolic geometry packing in onto itself. TODO link to QRI

At the end of the meditation, they dissolve the complex shape in their head back to dust and open their eyes. My understanding is that the point of the exercise is not to worship the figure, but rather to practice letting your mind bend into whatever shape you ask it to.

Building geometric intuition for how machine learning architectures transform space is much the same

A Tulku is a teacher. 

Often, the meditation involves a mantra to be repeated and internalized, reified by the image.

Maybe I sound like a Guy With a Hammer here, but this sounds a lot like understanding linear algebra! Let's say  


From Wikipedia: "The special tantric vows vary depending on the specific mandala practice for which the initiation is received and also depending on the level of initiation". In other words, meditating on a specific image trying to internalize a specific idea. The thing you meditate on should be based off your current abilities. 

Thinking of this thread on Twitter about visualizing higher dimensions: https://x.com/spikedoanz/status/1877944710284668955 when the data is Tensors (easy mode, this kinda only makes sense for stacking boxes of numbers more than visualizing 4d spac)
and this one for the process of developing a deeper sense of the symmetries of a higher dim space https://x.com/Morphenius/status/1639439602841944066 

# Deployment
Need to run both simultaneously:
`python backend.py` 
cd `frontend` and run `npm run dev` to get the frontend at http://localhost:3000

# Workflow
Current Setup:
- User enters text in frontend
- Frontend sends POST to http://localhost:8000/generate
- Backend receives prompt in the AnimationRequest Pydantic model
- Currently using placeholder generate_manim_code() function

# Concerns
validate/sanitize the generated Manim code?
Options for handling potentially unsafe code

# Challenges and considerations
Knowing the name of the file that just got generated! A couple approaches:
- the output_file flag from the manimgl call
- add something to the LLM call that insists upon the file name / final class to be consistent - something like DisplayScene and `display_scene` as the class name and file name. 
- grab the most recent video