from manim import *
import numpy as np
import os

# ====================================================================
#  The intelligent Sclera Class
# ====================================================================

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

    # --- NEW SQUINT LOGIC ---
    def _get_squint_target(self, theta: float) -> 'Sclera':
        """
        Calculates the target points for a squint animation.
        Theta = 0 means fully open, Theta = PI/2 means fully closed.
        """
        target_points = self.original_points.copy()
        # Clamp theta to be between 0 and PI/2
        theta = np.clip(theta, 0, PI / 2)

        # Max vertical extent of the original sclera
        max_y = self.height / 2

        # Calculate the squint factor: 0 for open, 1 for closed
        # Using sin(theta) maps 0 to 0 (no squint) and PI/2 to 1 (full squint)
        squint_factor = np.sin(theta)

        for i, point in enumerate(self.original_points):
            # Avoid division by zero if sclera has no height (e.g., scaled to 0)
            if max_y == 0:
                continue
            
            # Normalized vertical position (0 at center, 1 at top/bottom edges)
            norm_y = np.abs(point[1]) / max_y

            # Falloff weight: points closer to the poles are affected more strongly
            # Using a power function creates a smooth curve, affecting ends more.
            falloff_weight = norm_y ** 2 # Can be adjusted (e.g., norm_y ** 3) for different curves

            # Calculate vertical displacement
            # Points above center (positive y) move downwards (negative displacement)
            # Points below center (negative y) move upwards (positive displacement)
            displacement_y = -point[1] * falloff_weight * squint_factor
            
            target_points[i, 1] += displacement_y

        target_sclera = self.copy()
        target_sclera.set_points(target_points)
        target_sclera.move_to(self) # Keep sclera centered
        return target_sclera

    def get_squint_animation(self, theta: float) -> Animation:
        """
        Returns an animation for the Sclera to squint.
        Theta = 0 means fully open, Theta = PI/2 means fully closed.
        """
        return Transform(self, self._get_squint_target(theta))

    def get_reset_animation(self) -> Animation:
        """The single, authoritative method to reset the Sclera to its original shape."""
        target_mobject = self.copy()
        target_mobject.set_points(self.original_points)
        target_mobject.move_to(self)
        return Transform(self, target_mobject)


# ====================================================================
#  The Eye Class
# ====================================================================

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
    
    def reset_sclera(self) -> Animation:
        """Resets any deformation by restoring the original points."""
        return self.sclera.get_reset_animation()
    
    # --- NEW SQUINT METHODS ---
    def squint(self, theta: float, **kwargs) -> Animation:
        """Squints the eye by deforming the sclera."""
        return self.sclera.get_squint_animation(theta)

    def reset_squint(self, **kwargs) -> Animation:
        """Resets the eye from a squinted state to its original open shape."""
        # The reset_sclera method correctly restores the original (non-squinted) shape.
        return self.sclera.get_reset_animation()
    
# ====================================================================
#  Higher-level classes (now call the corrected methods)
# ====================================================================

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

    # --- NEW SQUINT METHODS ---
    def squint(self, theta: float, **kwargs) -> AnimationGroup:
        """Squints both eyes simultaneously."""
        return AnimationGroup(self.left_eye.squint(theta, **kwargs), self.right_eye.squint(theta, **kwargs))

    def reset_squint(self, **kwargs) -> AnimationGroup:
        """Resets both eyes from a squinted state."""
        return AnimationGroup(self.left_eye.reset_squint(**kwargs), self.right_eye.reset_squint(**kwargs))

class PsiCreature(VGroup):
    def __init__(self, body_color: ManimColor = BLUE_E, eye_color: ManimColor = BLUE_C, body_scale: float = 2.0, eyes_separation: float = 1.5, eye_width: float = 0.8, eye_height: float = 0.8, **kwargs):
        super().__init__(**kwargs)
        svg_file_path = "Psi.svg"
        if os.path.exists(svg_file_path): self.body = SVGMobject(svg_file_path).set_color(body_color)
        else:
            print(f"Warning: {svg_file_path} not found. Using a Circle placeholder.")
            self.body = Circle(radius=1.0, color=body_color, fill_opacity=1).set_width(1.5)
        self.body.set_height(body_scale)
        self.eyes = Eyes(separation=eyes_separation, eye_width=eye_width, eye_height=eye_height, iris_color=eye_color)
        target_y = self.body.get_top()[1] - (self.eyes.get_height() * 0.25)
        self.eyes.move_to(np.array([self.body.get_center()[0], target_y, 0]))
        self.add(self.body, self.eyes)

    # Delegate all methods
    def blink(self, **kwargs) -> AnimationGroup: return self.eyes.blink(**kwargs)
    def look_at(self, target, **kwargs) -> AnimationGroup: return self.eyes.look_at(target, **kwargs)
    def look_straight(self, **kwargs) -> AnimationGroup: return self.eyes.look_straight(**kwargs)
    def bend_sclera(self, direction: np.ndarray, intensity: float = 0.4) -> AnimationGroup: return self.eyes.bend_sclera(direction, intensity=intensity)
    def reset_sclera(self) -> AnimationGroup: return self.eyes.reset_sclera()

    # --- NEW SQUINT METHODS ---
    def squint(self, theta: float, **kwargs) -> AnimationGroup:
        """Squints the creature's eyes."""
        return self.eyes.squint(theta, **kwargs)

    def reset_squint(self, **kwargs) -> AnimationGroup:
        """Resets the creature's eyes from a squinted state."""
        return self.eyes.reset_squint(**kwargs)

# ====================================================================
#  Final Test Scene 
# ====================================================================

class TestEyeExpressionsScene(Scene):
    def construct(self):
        title = Text("Creature Expressions").to_edge(UP)
        self.add(title)
        psi = PsiCreature(body_scale=3.5, eye_color=GREEN_D)
        psi.to_edge(LEFT, buff=1.5)

        self.play(FadeIn(psi))
        self.play(psi.look_at(title))
        self.wait(1)

        # --- ANGRY ---
        angry_text = Text("Angry").next_to(psi, RIGHT, buff=0.5).scale(0.8)
        self.play(Write(angry_text))
        self.play(psi.bend_sclera(UP + RIGHT, intensity=0.35), run_time=0.6)
        self.wait(2)
        self.play(psi.reset_sclera(), run_time=0.6)
        self.play(FadeOut(angry_text))
        self.wait(0.5)

        # --- SAD ---
        sad_text = Text("Sad").next_to(psi, RIGHT, buff=0.5).scale(0.8)
        self.play(Write(sad_text))
        self.play(psi.bend_sclera(UP + LEFT, intensity=0.3), run_time=0.7)
        self.wait(2)
        self.play(psi.reset_sclera(), run_time=0.7)
        self.play(FadeOut(sad_text))
        self.wait(0.5)
        
        # --- SUSPICIOUS / SQUINT ---
        suspicious_text = Text("Suspicious / Squint").next_to(psi, RIGHT, buff=0.5).scale(0.8)
        self.play(Write(suspicious_text))
        # theta = PI/4 for a moderate squint (half closed)
        self.play(psi.squint(PI/5), run_time=0.8)
        self.wait(2)
        self.play(psi.reset_squint(), run_time=0.8)
        self.play(FadeOut(suspicious_text))
        self.wait(0.5)

        # --- Final animation ---
        self.wait(1)
        self.play(psi.look_straight(), psi.blink())
        self.wait(2)
        self.play(FadeOut(psi, title))