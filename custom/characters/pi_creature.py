from __future__ import annotations

import numpy as np

from manimlib.constants import *
from manimlib.mobject.mobject import Group, Mobject
from manimlib.mobject.geometry import Circle, Dot, Line
from manimlib.mobject.geometry import ArcBetweenPoints
from manimlib.mobject.svg.drawings import ThoughtBubble
from manimlib.mobject.svg.drawings import SpeechBubble
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.utils.space_ops import get_norm
from manimlib.utils.space_ops import normalize
from manimlib.animation.composition import AnimationGroup
from manimlib.animation.creation import ShowCreation
from manimlib.animation.transform import Transform
from manimlib.animation.fading import FadeIn

# The key insight: Don't try to inherit from complex classes like VMobject or VGroup
# Instead, wrap a container class (Group) and delegate methods

class PiCreature(Mobject):
    """
    A wrapper around a Group that behaves like a PiCreature.
    This avoids inheritance complexities in the Manim codebase.
    """
    def __init__(
        self,
        mode="plain",
        color=BLUE_E,
        stroke_width=0.0,
        stroke_color=BLACK,
        fill_opacity=1.0,
        height=3,
        flip_at_start=False,
        start_corner=None,
        **kwargs
    ):
        super().__init__(**kwargs)  # Simple initialization
        
        # First create the container that will hold all visual parts
        self.container = Group()
        
        # Store properties
        self.mode = mode
        self.bubble = None
        
        # Create body
        self.body = Circle(radius=1.0)
        self.body.set_fill(color, opacity=fill_opacity)
        self.body.set_stroke(width=stroke_width)
        
        # Create eyes
        self.eyes = self._create_eyes()
        
        # Create mouth based on mode
        self.mouth = self._create_mouth(mode)
        
        # Add all parts to the container
        self.container.add(self.body, self.eyes, self.mouth)
        
        # Scale to requested height
        self.container.set_height(height)
        
        if flip_at_start:
            self.container.flip()
        
        if start_corner is not None:
            self.container.to_corner(start_corner)
    
    def _create_eyes(self):
        """Create and return a VGroup of eyes"""
        eyes = VGroup()
        
        # Left eye
        left_eye_outer = Circle(radius=0.2)
        left_eye_outer.set_fill(WHITE, opacity=1)
        left_eye_outer.set_stroke(width=0)
        left_eye_outer.shift(UP * 0.3 + LEFT * 0.4)
        
        left_pupil = Circle(radius=0.08)
        left_pupil.set_fill(BLACK, opacity=1)
        left_pupil.set_stroke(width=0)
        left_pupil.shift(UP * 0.3 + LEFT * 0.35)
        
        left_pupil_shine = Dot(radius=0.02)
        left_pupil_shine.set_fill(WHITE, opacity=1)
        left_pupil_shine.set_stroke(width=0)
        left_pupil_shine.shift(UP * 0.31 + LEFT * 0.33)
        
        # Right eye
        right_eye_outer = Circle(radius=0.2)
        right_eye_outer.set_fill(WHITE, opacity=1)
        right_eye_outer.set_stroke(width=0)
        right_eye_outer.shift(UP * 0.3 + RIGHT * 0.4)
        
        right_pupil = Circle(radius=0.08)
        right_pupil.set_fill(BLACK, opacity=1)
        right_pupil.set_stroke(width=0)
        right_pupil.shift(UP * 0.3 + RIGHT * 0.35)
        
        right_pupil_shine = Dot(radius=0.02)
        right_pupil_shine.set_fill(WHITE, opacity=1)
        right_pupil_shine.set_stroke(width=0)
        right_pupil_shine.shift(UP * 0.31 + RIGHT * 0.33)
        
        # Group eyes
        left_eye = VGroup(left_eye_outer, left_pupil, left_pupil_shine)
        right_eye = VGroup(right_eye_outer, right_pupil, right_pupil_shine)
        eyes.add(left_eye, right_eye)
        
        return eyes
    
    def _create_mouth(self, mode):
        """Create and return a mouth based on the mode"""
        if mode == "plain":
            mouth = ArcBetweenPoints(
                LEFT * 0.3 + DOWN * 0.2,
                RIGHT * 0.3 + DOWN * 0.2,
            )
        elif mode == "happy":
            mouth = ArcBetweenPoints(
                LEFT * 0.3 + DOWN * 0.2,
                RIGHT * 0.3 + DOWN * 0.2,
                angle=-TAU/8,
            )
        elif mode == "sad":
            mouth = ArcBetweenPoints(
                LEFT * 0.3 + DOWN * 0.3,
                RIGHT * 0.3 + DOWN * 0.3,
                angle=TAU/8,
            )
        else:
            # Default to plain
            mouth = ArcBetweenPoints(
                LEFT * 0.3 + DOWN * 0.2,
                RIGHT * 0.3 + DOWN * 0.2,
            )
        
        mouth.set_stroke(BLACK, width=3)
        return mouth
    
    # Delegate all transform/position methods to container
    def scale(self, scale_factor, **kwargs):
        self.container.scale(scale_factor, **kwargs)
        return self
    
    def move_to(self, point_or_mobject, **kwargs):
        self.container.move_to(point_or_mobject, **kwargs)
        return self
    
    def shift(self, *vectors):
        self.container.shift(*vectors)
        return self
    
    def to_corner(self, corner=None, **kwargs):
        self.container.to_corner(corner, **kwargs)
        return self
    
    def get_center(self):
        return self.container.get_center()
    
    def get_height(self):
        return self.container.get_height()
    
    def get_width(self):
        return self.container.get_width()
    
    def flip(self, axis=UP):
        self.container.flip(axis)
        return self
    
    def set_height(self, height, **kwargs):
        self.container.set_height(height, **kwargs)
        return self
    
    # Add the special PiCreature methods
    def set_color(self, color, recurse=True):
        self.body.set_fill(color, opacity=self.body.get_fill_opacity())
        return self
    
    def get_color(self):
        return self.body.get_fill_color()
    
    def change_mode(self, mode):
        old_height = self.get_height()
        old_color = self.get_color()
        
        # Create a new mouth based on the mode
        new_mouth = self._create_mouth(mode)
        new_mouth.match_style(self.mouth)
        new_mouth.match_width(self.mouth)
        new_mouth.move_to(self.mouth)
        
        # Replace the old mouth
        self.container.remove(self.mouth)
        self.mouth = new_mouth
        self.container.add(self.mouth)
        
        # Update mode
        self.mode = mode
        return self
    
    def get_mode(self):
        return self.mode
    
    def look(self, direction):
        direction = normalize(direction)
        
        for eye in self.eyes:
            iris = eye[0]      # Outer eye
            pupil = eye[1]     # Pupil
            shine = eye[2]     # Shine
            
            iris_center = iris.get_center()
            right = iris.get_right() - iris_center
            up = iris.get_top() - iris_center
            
            # Calculate pupil movement
            vect = direction[0] * right + direction[1] * up
            v_norm = get_norm(vect)
            pupil_radius = pupil.get_width() / 2
            
            # Limit movement within the iris
            if v_norm > 0:
                vect = vect * (v_norm - 0.75 * pupil_radius) / v_norm
            
            # Move pupil and shine
            pupil.move_to(iris_center + vect)
            shine.move_to(pupil.get_center() + vect/3 + UP*0.02 + LEFT*0.02)
        
        return self
    
    def look_at(self, point_or_mobject):
        if isinstance(point_or_mobject, Mobject):
            point = point_or_mobject.get_center()
        else:
            point = point_or_mobject
        self.look(point - self.eyes.get_center())
        return self
    
    def get_looking_direction(self):
        return normalize(self.eyes[0][1].get_center() - self.eyes[0][0].get_center())
    
    def get_look_at_spot(self):
        return self.eyes.get_center() + self.get_looking_direction()
    
    def is_flipped(self):
        return self.eyes[0].get_center()[0] > self.eyes[1].get_center()[0]
    
    def blink(self):
        # Save eye positions
        eye_centers = [eye.get_center() for eye in self.eyes]
        
        # Create blink lines
        blink_lines = VGroup()
        for i, eye in enumerate(self.eyes):
            eye_center = eye_centers[i]
            blink_line = Line(
                eye_center + LEFT * 0.1,
                eye_center + RIGHT * 0.1,
            )
            blink_line.set_stroke(BLACK, width=3)
            blink_lines.add(blink_line)
        
        # Store original eyes
        self.original_eyes = self.eyes
        
        # Replace eyes with blink lines
        self.container.remove(self.eyes)
        self.eyes = blink_lines
        self.container.add(self.eyes)
        
        return self
    
    def get_bubble(self, content, bubble_type=ThoughtBubble, **bubble_config):
        bubble = bubble_type(content, **bubble_config)
        if hasattr(bubble, "pin_to"):
            bubble.pin_to(self)
        else:
            bubble.move_to(self.container.get_corner(UP + RIGHT) + UP + RIGHT)
        self.bubble = bubble
        return bubble
    
    def make_eye_contact(self, pi_creature):
        self.look_at(pi_creature.eyes)
        pi_creature.look_at(self.eyes)
        return self
    
    # Special method to access container submobjects
    def get_submobjects(self):
        return [self.container]
    
    # Animation methods
    def change(self, new_mode, look_at=None):
        animation = self.animate.change_mode(new_mode)
        if look_at is not None:
            animation = animation.look_at(look_at)
        return animation
    
    def says(self, content, **kwargs):
        bubble_type = kwargs.pop("bubble_type", SpeechBubble)
        target_mode = kwargs.pop("target_mode", "speaking")
        bubble_kwargs = kwargs.pop("bubble_kwargs", {})
        bubble = self.get_bubble(content, bubble_type=bubble_type, **bubble_kwargs)
        
        return [
            self.animate.change_mode(target_mode),
            FadeIn(bubble),
        ]
    
    def thinks(self, content, **kwargs):
        return self.says(content, bubble_type=ThoughtBubble, target_mode="thinking", **kwargs)


class Randolph(PiCreature):
    def __init__(self, **kwargs):
        super().__init__(color=BLUE_E, **kwargs)


class Mortimer(PiCreature):
    def __init__(
        self,
        mode="plain",
        color=GREY_BROWN,
        flip_at_start=True,
        **kwargs,
    ):
        super().__init__(mode, color, flip_at_start=flip_at_start, **kwargs)