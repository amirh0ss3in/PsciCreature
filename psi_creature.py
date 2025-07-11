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
#  Mouth Class
# ====================================================================
class Mouth(VGroup):
    def __init__(
        self,
        emotion: str = "neutral",
        width: float = 0.01,
        emotion_intensity: float = 0.1,
        **kwargs
    ):
        super().__init__()
        self.emotion = emotion
        self.width = width
        self.emotion_intensity = emotion_intensity
        self.bezier_kwargs = kwargs.copy()
        if "color" not in kwargs:
            kwargs["color"] = BLACK
        if "stroke_width" not in kwargs:
            kwargs["stroke_width"] = 2
        start_point = LEFT * width / 2
        end_point = RIGHT * width / 2
        handle_base_1 = LEFT * width / 4
        handle_base_2 = RIGHT * width / 4
        if emotion == "happy":
            handle1 = handle_base_1 + DOWN * emotion_intensity
            handle2 = handle_base_2 + DOWN * emotion_intensity
        elif emotion == "sad":
            handle1 = handle_base_1 + UP * emotion_intensity
            handle2 = handle_base_2 + UP * emotion_intensity
        elif emotion == "unsure":
            handle1 = handle_base_1 + UP * emotion_intensity * 0.4
            handle2 = handle_base_2 + DOWN * emotion_intensity * 0.7
        elif emotion == "neutral":
            handle1 = handle_base_1
            handle2 = handle_base_2
        elif emotion == "happy_smirk":
            handle1 = handle_base_1 + LEFT * emotion_intensity * 0.4
            handle2 = handle_base_2 + DOWN * emotion_intensity * 0.7
            start_point += 0.08*UP
            end_point += 0.08*DOWN
        elif emotion == "sad_smirk":
            handle1 = handle_base_1 - RIGHT * emotion_intensity * 0.4
            handle2 = handle_base_2 - DOWN * emotion_intensity * 0.5
            start_point += 0.08*DOWN
            end_point += 0.04*UP
        else: # Default to neutral
            handle1 = handle_base_1
            handle2 = handle_base_2
        mouth_curve = CubicBezier(start_point, handle1, handle2, end_point, **kwargs)
        self.add(mouth_curve)

# ====================================================================
#  PsiCreature CLASS - FULLY CORRECTED AND IMPROVED
# ====================================================================

class PsiCreature(VGroup):
    def __init__(
        self,
        initial_anchor_pos: np.ndarray = ORIGIN,
        initial_state: str = "default",
        initial_emotion: str = "neutral",
        body_color: ManimColor = BLUE_E,
        eye_color: ManimColor = BLUE_C,
        body_scale: float = 2.0,
        eyes_separation: float = 0.48,
        eye_width: float = 0.3,
        eye_height: float = 0.3,
        mouth_width: float = 0.25,
        mouth_emotion_intensity: float = 0.1,
        mouth_kwargs: dict = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        # Store key *unscaled* creation parameters for resizing
        self.body_scale = body_scale
        self.eye_color = eye_color
        self.mouth_width = mouth_width
        self.mouth_emotion_intensity = mouth_emotion_intensity
        self.mouth_kwargs = mouth_kwargs or {}

        # assets directory:
        self.templates = {}
        assets_dir = "assets"
        for filename in os.listdir(assets_dir):
            # Check if the file is an SVG file
            if filename.endswith(".svg"):
                # Construct the full path to the SVG file
                svg_path = os.path.join(assets_dir, filename)

                # Get the template name by removing the extension
                template_name = os.path.splitext(filename)[0]

                # Create the SVGMobject and add it to the dictionary
                self.templates[template_name] = SVGMobject(svg_path).set_color(body_color)

        for template in self.templates.values():
            template.set_height(self.body_scale)

        self.anchor_vectors = {
            state: template.submobjects[-1].get_center()
            for state, template in self.templates.items()
        }

        # --- THIS IS THE CENTRAL SCALING LOGIC ---
        default_body_scale = 2.0
        scale_factor = self.body_scale / default_body_scale

        # Calculate scaled dimensions for all components
        scaled_eye_width = eye_width * scale_factor
        scaled_eye_height = eye_height * scale_factor
        scaled_eyes_separation = eyes_separation * scale_factor
        scaled_mouth_width = self.mouth_width * scale_factor
        scaled_mouth_emotion_intensity = self.mouth_emotion_intensity * scale_factor

        # Scale mouth stroke width
        final_mouth_kwargs = self.mouth_kwargs.copy()
        base_stroke_width = final_mouth_kwargs.get("stroke_width", 2)
        final_mouth_kwargs["stroke_width"] = base_stroke_width * scale_factor
        # --- END OF SCALING LOGIC ---

        self.eyes = Eyes(
            separation=scaled_eyes_separation,
            eye_width=scaled_eye_width,
            eye_height=scaled_eye_height,
            iris_color=self.eye_color
        )
        self.mouth = Mouth(
            emotion=initial_emotion,
            width=scaled_mouth_width,
            emotion_intensity=scaled_mouth_emotion_intensity,
            **final_mouth_kwargs
        )
        
        self.eyes_offsets = {}
        self.mouth_offsets = {}
        for state, template in self.templates.items():
            stable_x = self.anchor_vectors[state][0]
            target_y_eyes = template.get_top()[1] - (self.eyes.get_height() * 0.9)
            eyes_center_in_template = np.array([stable_x, target_y_eyes, 0])
            self.eyes_offsets[state] = eyes_center_in_template - self.anchor_vectors[state]
            target_y_mouth = self.anchor_vectors[state][1] + (self.body_scale * 0.2)
            mouth_center_in_template = np.array([stable_x, target_y_mouth, 0])
            self.mouth_offsets[state] = mouth_center_in_template - self.anchor_vectors[state]

        if initial_state not in self.templates:
            raise ValueError(f"Initial state '{initial_state}' is not valid.")
        self.current_state_name = initial_state
        self.anchor_pos = initial_anchor_pos

        self.body = self._create_body_at_anchor(self.current_state_name, self.anchor_pos)
        self.eyes.move_to(self.anchor_pos + self.eyes_offsets[self.current_state_name])
        self.mouth.move_to(self.anchor_pos + self.mouth_offsets[self.current_state_name])
        self.add(self.body, self.eyes, self.mouth)

    def _create_body_at_anchor(self, state_name, anchor_target_pos):
        template = self.templates[state_name]
        anchor_vector = self.anchor_vectors[state_name]
        mobj = template.copy()
        mobj.move_to(anchor_target_pos - anchor_vector)
        return mobj

    def change_state(self, new_state_name: str) -> AnimationGroup:
        """
        A simple state change. For more complex, simultaneous animations,
        use change_state_and_animate.
        """
        return self.change_state_and_animate(new_state_name)

    def change_state_and_animate(
        self,
        new_state_name: str,
        look_at_target: Mobject | np.ndarray = None,
        squint_theta: float = None,
        reset_squint_flag: bool = False,
        **kwargs
    ) -> AnimationGroup:
        """
        Creates a composite animation for changing state while simultaneously
        performing other actions like looking or squinting. This method resolves
        animation conflicts by calculating all targets based on the final state.

        Args:
            new_state_name (str): The target state for the body.
            look_at_target (Mobject | np.ndarray, optional): The target to look at.
            squint_theta (float, optional): The angle for the squint.
            reset_squint_flag (bool, optional): If True, resets any existing squint.

        Returns:
            AnimationGroup: A single animation group to be passed to `self.play()`.
        """
        if new_state_name not in self.templates:
            raise ValueError(f"Cannot change to '{new_state_name}'; not a valid state.")

        # 1. Get base animations for body and mouth moving to new state
        target_body = self._create_body_at_anchor(new_state_name, self.anchor_pos)
        body_transform = Transform(self.body, target_body)

        mouth_new_pos = self.anchor_pos + self.mouth_offsets[new_state_name]
        mouth_move = self.mouth.animate.move_to(mouth_new_pos)

        # This will hold all animations to be played together
        all_anims = [body_transform, mouth_move]

        # 2. Handle the eyes, which are the source of the conflict.
        # We need to create a single Transform for the entire eye group
        # that incorporates movement, squinting, and looking.

        # Create a deep copy of the eyes to modify into the final target
        target_eyes = self.eyes.copy()

        # Move the entire target eye group to its final position
        eyes_new_pos = self.anchor_pos + self.eyes_offsets[new_state_name]
        target_eyes.move_to(eyes_new_pos)

        # Apply squint/reset to the *target* eyes
        if reset_squint_flag:
            # Get the reset animation and apply its target to our target_eyes
            reset_anim = target_eyes.reset_squint()
            target_eyes.left_eye.sclera.become(reset_anim.animations[0].target_mobject)
            target_eyes.right_eye.sclera.become(reset_anim.animations[1].target_mobject)
        elif squint_theta is not None:
            # Get the squint animation and apply its target
            squint_anim = target_eyes.squint(squint_theta)
            target_eyes.left_eye.sclera.become(squint_anim.animations[0].target_mobject)
            target_eyes.right_eye.sclera.become(squint_anim.animations[1].target_mobject)

        # Apply look_at to the *target* eyes (which are now in their final position)
        if look_at_target is not None:
            target_point = look_at_target.get_center() if isinstance(look_at_target, Mobject) else look_at_target
            
            # Manually move the pupils of the target_eyes, NOT animating
            for i, eye in enumerate([target_eyes.left_eye, target_eyes.right_eye]):
                direction = target_point - eye.sclera.get_center()
                if np.linalg.norm(direction) > 0:
                    unit_direction = normalize(direction)
                    max_offset = (eye.sclera.height / 2) - eye.iris.radius
                    pupil_new_pos = eye.sclera.get_center() + unit_direction * max_offset
                    eye.iris_pupil_group.move_to(pupil_new_pos)

        # Now, create the single Transform from current eyes to the fully configured target_eyes
        eyes_transform = Transform(self.eyes, target_eyes)
        all_anims.append(eyes_transform)
        
        # 3. Update the creature's state variables for future animations
        self.current_state_name = new_state_name
        self.body.target = target_body # For Manim's internal tracking

        return AnimationGroup(*all_anims, **kwargs)

    def move_anchor_to(self, new_anchor_pos: np.ndarray) -> AnimationGroup:
        current_anchor_vector = self.anchor_vectors[self.current_state_name]
        body_move = self.body.animate.move_to(new_anchor_pos - current_anchor_vector)
        current_eyes_offset = self.eyes_offsets[self.current_state_name]
        eyes_move = self.eyes.animate.move_to(new_anchor_pos + current_eyes_offset)
        current_mouth_offset = self.mouth_offsets[self.current_state_name]
        mouth_move = self.mouth.animate.move_to(new_anchor_pos + current_mouth_offset)
        self.anchor_pos = new_anchor_pos
        return AnimationGroup(body_move, eyes_move, mouth_move)

    def resize(self, scale_factor: float, **kwargs) -> Become:
        new_body_scale = self.body_scale * scale_factor
        target_creature = PsiCreature(
            initial_anchor_pos=self.anchor_pos,
            initial_state=self.current_state_name,
            initial_emotion=self.mouth.emotion,
            body_color=self.templates[self.current_state_name].get_color(),
            eye_color=self.eye_color,
            body_scale=new_body_scale,
            mouth_width=self.mouth_width, # Pass unscaled value
            mouth_emotion_intensity=self.mouth_emotion_intensity, # Pass unscaled value
            mouth_kwargs=self.mouth_kwargs # Pass original kwargs
        )
        return Become(self, target_creature, **kwargs)

    def change_mouth(self, new_emotion: str, **kwargs) -> Become:
        # Create the new mouth using the CURRENTLY scaled parameters
        # from the existing mouth to ensure consistency.
        target_mouth = Mouth(
            emotion=new_emotion,
            width=self.mouth.width,
            emotion_intensity=self.mouth.emotion_intensity,
            **self.mouth.bezier_kwargs
        )
        target_mouth.move_to(self.mouth)
        return Become(self.mouth, target_mouth, **kwargs)

    # Delegate eye and mouth methods
    def blink(self, **kwargs) -> AnimationGroup: return self.eyes.blink(**kwargs)
    def look_at(self, target, **kwargs) -> AnimationGroup: return self.eyes.look_at(target, **kwargs)
    def look_straight(self, **kwargs) -> AnimationGroup: return self.eyes.look_straight(**kwargs)
    def bend_sclera(self, direction: np.ndarray, intensity: float=0.4) -> AnimationGroup: return self.eyes.bend_sclera(direction, intensity=intensity)
    def reset_sclera(self) -> AnimationGroup: return self.eyes.reset_sclera()
    def squint(self, theta: float, **kwargs) -> AnimationGroup: return self.eyes.squint(theta, **kwargs)
    def reset_squint(self, **kwargs) -> AnimationGroup: return self.eyes.reset_squint(**kwargs)
