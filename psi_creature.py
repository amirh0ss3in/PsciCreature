from manim import *
import numpy as np
import os

# ====================================================================
#  Unaltered Helper Classes (Sclera, Eye, Eyes)
#  (These classes are correct and do not need changes)
# ====================================================================
class Become(Transform):
    """
    An animation that transforms one mobject into another, then replaces the
    internal state of the original mobject with that of the target.

    After the animation, the starting mobject will be visually and internally
    indistinguishable from the target mobject. This allows for complex state
    changes (like re-initializing with new parameters) without needing to
    manually reassign the variable in your scene's `construct` method.
    """
    def __init__(self, mobject, target_mobject, **kwargs):
        """
        Args:
            mobject: The Mobject to be transformed.
            target_mobject: The Mobject to become. Its state will be copied
                            into `mobject` at the end of the animation.
        """
        self.target_copy = target_mobject.copy()
        super().__init__(mobject, target_mobject, **kwargs)

    def finish(self) -> None:
        """Called when the animation is finished."""
        super().finish()
        # The magic happens here:
        # We replace the dictionary of the original mobject with the
        # dictionary of the target mobject's copy. This effectively
        # makes the original mobject "become" the target.
        self.mobject.__dict__.update(self.target_copy.__dict__)

class Sclera(VMobject):
    def __init__(self, width: float = 1.0, height: float = 1.0, **kwargs):
        super().__init__(**kwargs)
        self.width = width
        self.height = height
        ellipse_template = Circle(radius=1.0).scale(np.array([width / 2, height / 2, 1]))
        self.set_points(ellipse_template.get_points())
        self.original_points = self.get_points().copy()
        self.set_fill(WHITE, opacity=1)
        self.set_stroke(BLACK, width=2)

    def _get_bend_target(self, direction_vector: np.ndarray, intensity: float) -> 'Sclera':
        target_points = self.original_points.copy()
        main_displacement_vector = normalize(-direction_vector)
        displacement_magnitude = self.height * intensity
        for i, point in enumerate(self.original_points):
            if np.linalg.norm(point) < 1e-6: continue
            point_direction = normalize(point)
            dot_p = np.clip(np.dot(normalize(direction_vector), point_direction), -1.0, 1.0)
            angle_diff = np.arccos(dot_p)
            if angle_diff > PI / 2: falloff_weight = 0.0
            else:
                falloff_weight = (np.cos(angle_diff) + 1) / 2 * np.cos(angle_diff)
                falloff_weight = falloff_weight ** 1.5
            displacement_for_point = main_displacement_vector * displacement_magnitude * falloff_weight
            target_points[i] += displacement_for_point
        target_sclera = self.copy()
        target_sclera.set_points(target_points)
        target_sclera.move_to(self)
        return target_sclera

    def get_bend_animation(self, direction_vector: np.ndarray, intensity: float = 0.4) -> Animation:
        return Transform(self, self._get_bend_target(direction_vector, intensity))

    def _get_squint_target(self, theta: float) -> 'Sclera':
        target_points = self.original_points.copy()
        theta = np.clip(theta, 0, PI / 2)
        max_y = self.height / 2
        squint_factor = np.sin(theta)
        for i, point in enumerate(self.original_points):
            if max_y == 0: continue
            norm_y = np.abs(point[1]) / max_y
            falloff_weight = norm_y ** 2
            displacement_y = -point[1] * falloff_weight * squint_factor
            target_points[i, 1] += displacement_y
        target_sclera = self.copy()
        target_sclera.set_points(target_points)
        target_sclera.move_to(self)
        return target_sclera

    def get_squint_animation(self, theta: float) -> Animation:
        return Transform(self, self._get_squint_target(theta))

    def get_reset_animation(self) -> Animation:
        target_mobject = self.copy()
        target_mobject.set_points(self.original_points)
        target_mobject.move_to(self)
        return Transform(self, target_mobject)

class Eye(VGroup):
    def __init__(self, width: float = 1.0, height: float = 1.0, iris_color: ManimColor = BLUE_C, iris_radius_ratio: float = 0.5, pupil_radius_ratio: float = 0.4, **kwargs):
        super().__init__(**kwargs)
        self.eye_width, self.eye_height = width, height
        self.sclera = Sclera(width=self.eye_width, height=self.eye_height)
        iris_radius = (self.eye_height / 2) * iris_radius_ratio
        self.iris = Circle(radius=iris_radius, color=iris_color, fill_opacity=1, stroke_width=0)
        pupil_radius = iris_radius * pupil_radius_ratio
        self.pupil = Circle(radius=pupil_radius, color=BLACK, fill_opacity=1, stroke_width=0)
        highlight_radius = pupil_radius * 0.5
        self.highlight = Circle(radius=highlight_radius, color=WHITE, fill_opacity=1, stroke_width=0)
        self.highlight.move_to(self.iris.get_center() + (UP + LEFT) * iris_radius * 0.4)
        self.iris_pupil_group = VGroup(self.iris, self.pupil, self.highlight)
        self.sclera.set_z_index(0)
        self.iris_pupil_group.set_z_index(1)
        self.add(self.sclera, self.iris_pupil_group)

    def blink(self, **kwargs) -> Animation: return self.animate(**kwargs, rate_func=there_and_back).scale((1, 0.1, 1))
    def look_at(self, point_or_mobject, **kwargs) -> Animation:
        target_point = point_or_mobject.get_center() if isinstance(point_or_mobject, Mobject) else point_or_mobject
        direction = target_point - self.sclera.get_center()
        if np.linalg.norm(direction) == 0: return self.iris_pupil_group.animate.move_to(self.sclera.get_center())
        unit_direction = normalize(direction)
        max_offset = (self.sclera.height / 2) - self.iris.radius
        new_position = self.sclera.get_center() + unit_direction * max_offset
        return self.iris_pupil_group.animate(**kwargs).move_to(new_position)

    def bend_sclera(self, direction_vector: np.ndarray, intensity: float = 0.4) -> Animation: return self.sclera.get_bend_animation(direction_vector, intensity)
    def reset_sclera(self) -> Animation: return self.sclera.get_reset_animation()
    def squint(self, theta: float, **kwargs) -> Animation: return self.sclera.get_squint_animation(theta)
    def reset_squint(self, **kwargs) -> Animation: return self.sclera.get_reset_animation()

class Eyes(VGroup):
    def __init__(self, separation: float=1.5, eye_width: float=1.0, eye_height: float=1.0, **eye_kwargs):
        super().__init__()
        self.left_eye = Eye(width=eye_width, height=eye_height, **eye_kwargs)
        self.right_eye = Eye(width=eye_width, height=eye_height, **eye_kwargs)
        self.left_eye.move_to(LEFT * separation / 2)
        self.right_eye.move_to(RIGHT * separation / 2)
        self.add(self.left_eye, self.right_eye)
    
    def blink(self, **kwargs) -> AnimationGroup: return AnimationGroup(self.left_eye.blink(**kwargs), self.right_eye.blink(**kwargs))
    def look_at(self, target, **kwargs) -> AnimationGroup: return AnimationGroup(self.left_eye.look_at(target, **kwargs), self.right_eye.look_at(target, **kwargs))
    def look_straight(self, **kwargs) -> AnimationGroup: return AnimationGroup(self.left_eye.look_at(self.left_eye.get_center(), **kwargs), self.right_eye.look_at(self.right_eye.get_center(), **kwargs))
    def bend_sclera(self, direction_vector: np.ndarray, intensity: float = 0.4) -> AnimationGroup:
        mirrored_direction = direction_vector * np.array([-1, 1, 1])
        return AnimationGroup(self.left_eye.bend_sclera(direction_vector, intensity=intensity), self.right_eye.bend_sclera(mirrored_direction, intensity=intensity))
    def reset_sclera(self) -> AnimationGroup: return AnimationGroup(self.left_eye.reset_sclera(), self.right_eye.reset_sclera())
    def squint(self, theta: float, **kwargs) -> AnimationGroup: return AnimationGroup(self.left_eye.squint(theta, **kwargs), self.right_eye.squint(theta, **kwargs))
    def reset_squint(self, **kwargs) -> AnimationGroup: return AnimationGroup(self.left_eye.reset_squint(**kwargs), self.right_eye.reset_squint(**kwargs))

# ====================================================================
#  PsiCreature CLASS WITH NEW `resize` METHOD
# ====================================================================

class PsiCreature(VGroup):
    def __init__(
        self,
        initial_anchor_pos: np.ndarray = ORIGIN,
        initial_state: str = "default",
        body_color: ManimColor = BLUE_E,
        eye_color: ManimColor = BLUE_C,
        body_scale: float = 2.0,
        eyes_separation: float = 0.48,
        eye_width: float = 0.3,
        eye_height: float = 0.3,
        **kwargs
    ):
        super().__init__(**kwargs)
        # Store key creation parameters for resizing
        self.body_scale = body_scale
        self.eye_color = eye_color

        self.templates = {
            "default": SVGMobject("Psi.svg").set_color(body_color),
            "pondering": SVGMobject("Psi_hand_on_mouth_pondering.svg").set_color(body_color),
            "hand_up": SVGMobject("Psi_hand_up.svg").set_color(body_color),
        }
        for template in self.templates.values():
            template.set_height(self.body_scale)

        self.anchor_vectors = {
            state: template.submobjects[-1].get_center()
            for state, template in self.templates.items()
        }

        default_body_scale = 2.0
        scale_factor = self.body_scale / default_body_scale
        scaled_eye_width = eye_width * scale_factor
        scaled_eye_height = eye_height * scale_factor
        scaled_eyes_separation = eyes_separation * scale_factor

        self.eyes = Eyes(
            separation=scaled_eyes_separation,
            eye_width=scaled_eye_width,
            eye_height=scaled_eye_height,
            iris_color=self.eye_color
        )
        
        self.eyes_offsets = {}
        for state, template in self.templates.items():
            stable_x = self.anchor_vectors[state][0]
            target_y = template.get_top()[1] - (self.eyes.get_height() * 0.9)
            eyes_center_in_template = np.array([stable_x, target_y, 0])
            self.eyes_offsets[state] = eyes_center_in_template - self.anchor_vectors[state]

        if initial_state not in self.templates:
            raise ValueError(f"Initial state '{initial_state}' is not valid.")
        self.current_state_name = initial_state
        self.anchor_pos = initial_anchor_pos

        self.body = self._create_body_at_anchor(self.current_state_name, self.anchor_pos)
        self.eyes.move_to(self.anchor_pos + self.eyes_offsets[self.current_state_name])
        self.add(self.body, self.eyes)

    def _create_body_at_anchor(self, state_name, anchor_target_pos):
        template = self.templates[state_name]
        anchor_vector = self.anchor_vectors[state_name]
        mobj = template.copy()
        mobj.move_to(anchor_target_pos - anchor_vector)
        return mobj

    def change_state(self, new_state_name: str) -> AnimationGroup:
        # This can also be improved with the Become pattern, but we'll leave it for now
        # for simplicity, as it doesn't suffer from the same internal state issue.
        if new_state_name not in self.templates:
            raise ValueError(f"Cannot change to '{new_state_name}'; not a valid state.")
        target_body = self._create_body_at_anchor(new_state_name, self.anchor_pos)
        body_transform = Transform(self.body, target_body)
        eyes_new_pos = self.anchor_pos + self.eyes_offsets[new_state_name]
        eyes_move = self.eyes.animate.move_to(eyes_new_pos)
        
        self.current_state_name = new_state_name
        self.body.target = target_body
        return AnimationGroup(body_transform, eyes_move)

    def move_anchor_to(self, new_anchor_pos: np.ndarray) -> AnimationGroup:
        current_anchor_vector = self.anchor_vectors[self.current_state_name]
        body_move = self.body.animate.move_to(new_anchor_pos - current_anchor_vector)
        current_eyes_offset = self.eyes_offsets[self.current_state_name]
        eyes_move = self.eyes.animate.move_to(new_anchor_pos + current_eyes_offset)
        self.anchor_pos = new_anchor_pos
        return AnimationGroup(body_move, eyes_move)

    # ====================================================================
    #  IMPROVED: Simple `resize` method
    # ====================================================================
    def resize(self, scale_factor: float, **kwargs) -> Become:
        """
        Returns an animation that resizes the creature.
        
        This method correctly re-initializes all internal components (like eyes)
        to work at the new scale. It uses the `Become` animation to update the
        creature in place, so you don't need to reassign your variable.

        Args:
            scale_factor (float): The factor by which to scale the creature.
            **kwargs: Animation-related keyword arguments (e.g., run_time).

        Returns:
            Become: The animation to be played in a scene.

        Usage in a Scene:
            psi = PsiCreature(body_scale=1.0)
            self.add(psi)
            self.play(psi.resize(3.0, run_time=2)) # Simple and intuitive
            # Now, psi is larger and all its methods will work correctly.
            self.play(psi.squint(PI/4))
        """
        new_body_scale = self.body_scale * scale_factor

        # Create a new target creature with the new scale, inheriting the
        # current creature's state, position, and colors.
        target_creature = PsiCreature(
            initial_anchor_pos=self.anchor_pos,
            initial_state=self.current_state_name,
            body_color=self.templates[self.current_state_name].get_color(),
            eye_color=self.eye_color,
            body_scale=new_body_scale,
        )

        # Return the 'Become' animation, which handles the visual transform
        # and the internal state update automatically.
        return Become(self, target_creature, **kwargs)

    # Delegate all eye methods
    def blink(self, **kwargs) -> AnimationGroup: return self.eyes.blink(**kwargs)
    def look_at(self, target, **kwargs) -> AnimationGroup: return self.eyes.look_at(target, **kwargs)
    def look_straight(self, **kwargs) -> AnimationGroup: return self.eyes.look_straight(**kwargs)
    def bend_sclera(self, direction: np.ndarray, intensity: float=0.4) -> AnimationGroup: return self.eyes.bend_sclera(direction, intensity=intensity)
    def reset_sclera(self) -> AnimationGroup: return self.eyes.reset_sclera()
    def squint(self, theta: float, **kwargs) -> AnimationGroup: return self.eyes.squint(theta, **kwargs)
    def reset_squint(self, **kwargs) -> AnimationGroup: return self.eyes.reset_squint(**kwargs)

# ====================================================================
#  UPDATED: Test Scene demonstrating all features
# ====================================================================

class TestCreatureFullCapabilities(Scene):
    def construct(self):
        title = Text("Creature Full Capabilities").to_edge(UP)
        self.add(title)

        psi = PsiCreature(
            initial_anchor_pos=LEFT * 4,
            body_scale=3.5,
            eye_color=GREEN_D
        )
        anchor_dot = Dot(psi.anchor_pos, color=RED).set_z_index(10)
        self.play(FadeIn(psi), 
                #   FadeIn(anchor_dot)
                  )
        self.wait(1)

        self.play(psi.look_at(title))
        self.play(psi.squint(PI / 5), run_time=0.8)
        self.wait(1)
        self.play(psi.reset_squint(), run_time=0.8)
        self.play(psi.look_straight())
        self.wait(1)

        # Test Body State Change (anchor is stationary, eyes should now move correctly)
        self.play(psi.change_state("pondering"))
        self.wait(2)
        
        # Test Anchor-Based Movement (while in 'pondering' state)
        destination_1 = RIGHT * 4
        self.play(
            psi.move_anchor_to(destination_1),
            # anchor_dot.animate.move_to(destination_1)
        )
        self.wait(1)

        # Test State Change at a New Location
        self.play(psi.change_state("default"))
        self.wait(1)

        # Final Movement and Blink
        destination_2 = ORIGIN
        self.play(
            psi.move_anchor_to(destination_2),
            # anchor_dot.animate.move_to(destination_2),
        )
        self.play(psi.blink())
        self.wait(2)
        
        self.play(psi.move_anchor_to(UP),
                #   anchor_dot.animate.move_to(UP)
                  )
        
        self.play(psi.look_at(LEFT))
        self.wait(1)

        self.play(psi.change_state("pondering"))
        self.wait(1)

        self.play(psi.bend_sclera(UP+RIGHT))
        self.wait(1)

        self.play(psi.reset_sclera())
        self.wait(1)


class TestSize(Scene):
    def construct(self):
        title = Text("Test Proportional Sizing").to_edge(UP)
        
        psi_small = PsiCreature(
            initial_anchor_pos=LEFT * 4,
            body_scale=1.5, # was 1.0, increased slightly for better visibility
            eye_color=GREEN_D
        )
        psi_small_label = Text("body_scale=1.5", font_size=24).next_to(psi_small, DOWN)


        psi_big = PsiCreature(
            initial_anchor_pos=RIGHT * 4,
            body_scale=4.0,
            eye_color=BLUE_C
        )
        psi_big_label = Text("body_scale=4.0", font_size=24).next_to(psi_big, DOWN)

        self.play(
            FadeIn(title),
            FadeIn(psi_small),
            FadeIn(psi_small_label),
            FadeIn(psi_big),
            FadeIn(psi_big_label)
        )
        
        self.wait(1)
        
        self.play(
            psi_small.look_at(psi_big),
            psi_big.look_at(psi_small)
        )
        
        self.wait(1)
        
        self.play(
            psi_small.blink(),
            psi_big.blink()
        )

        self.wait(2)

class TestSimplerResize(Scene):
    def construct(self):
        title = Text("Testing the Simpler 'resize' Method").to_edge(UP)
        self.add(title)

        # 1. Create the initial creature
        psi = PsiCreature(body_scale=1.0, eye_color=TEAL)
        self.play(FadeIn(psi))
        self.wait(1)
        self.play(psi.move_anchor_to(LEFT * 4))
        self.wait(1)

        # 2. Resize the creature using the new, simple syntax
        self.play(psi.move_anchor_to(ORIGIN), psi.resize(3.5, run_time=2))
        # No need to reassign `psi`. It has now "become" the larger creature.
        self.wait(1)

        # 3. Prove that subsequent animations work correctly on the resized creature
        self.play(psi.bend_sclera(UP + RIGHT))
        self.wait(1)
        self.play(psi.reset_sclera(),
                  psi.squint(PI/4, run_time=0.5, rate_func=there_and_back))
        self.wait(1)

        # 4. All other methods remain fully functional
        self.play(psi.move_anchor_to(RIGHT * 4))
        self.play(psi.change_state("pondering"))
        self.play(psi.blink())
        self.wait(2)
