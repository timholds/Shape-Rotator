---
layout: page
title: "Creating a Custom Fine Tuning Dataset on 3Blue1Brown code"
permalink: /3b1b-dataset
menus: header

---
Our goal is to use the code from 3Blue1Brown to create a custom dataset for fine tuning a model. We will use the Youtube API to get transcripts for all the videos and match these up with code from the 3Blue1Brown repository. We use the transcript to get an understanding of intention


# Creating a Custom Fine Tuning Dataset

add a VLM in the loop to give layout and spacing feedback

## Problem: The Manim Library has changed
If we just try to render the old manim code with our current version of manimgl (1.7.2), we will certainly get an error. This link claims to have a way to do it, but I haven't tried it yet https://github.com/jeertmans/manim-tutorial/blob/main/examples/README.md

Our solution is to take the old code and pass it through an LLM to update it to be in line with how modern manim code is written. The nice thing is that this is totally verifiable by just rerendering the code and checking if it matches the video.

Here are some common updates:
- Replace `from manim_imports_ext import *` with `from manimlib import *`
- Replaced `OldTex` with `Tex` and `OldTexText` with `Text` 
- Before you could pass methods like next_to directly to `self.play()`, but in newer versions, you need to wrap them with `ApplyMethod`.
- Changed `formula.restore` to `Restore(formula)`
- Replaced ApplyMethod with .animate:

Important Notes:

You'll need the SVG files (like "steve.svg", "linda.svg", "book.svg", etc.) in your project directory. If you don't have these files, the code will fail when trying to load these assets.
Modern manimgl uses a different method for configuration. While I've preserved the CONFIG dictionaries which might still work, some animations may behave differently.
Certain SVG-related methods may have changed in manimgl. If you encounter issues with SVG rendering, you may need to update those specific parts.