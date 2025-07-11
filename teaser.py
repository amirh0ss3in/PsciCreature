from manim import *
from psi_creature import PsiCreature

class Teaser(Scene):
    def construct(self):
        # Initial setup
        psi = PsiCreature(body_scale=3, eye_color=BLUE_C, initial_emotion="neutral")
        dot = Dot(LEFT * 4, color=YELLOW)
        self.add(dot)
        self.play(FadeIn(psi))
        self.wait()

        # --- ACTION 1: A complex, multi-part expression change ---
        # The creature will ponder, look at the dot, get a bit unsure, and squint.
        # All actions happen smoothly and simultaneously in one animation.
        self.play(
            psi.change_state(
                "pondering",
                look_at_target=dot,
                change_mouth_to="unsure",
                squint_amount=0.7,
                run_time=2
            )
        )
        self.play(psi.move_anchor_to(2*RIGHT+UP))
        self.wait()

        # --- ACTION 2: Change expression while keeping the same body shape ---
        # The creature decides it's happy about the dot.
        # We pass its *current* state to keep the body the same.
        self.play(
            psi.change_state(
                psi.current_state_name, # Keep the "pondering" body
                change_mouth_to="happy_smirk",
                reset_squint=True, # Open eyes wide again
                run_time=1.5
            )
        )
        self.wait()

        # --- ACTION 3: Reset everything ---
        # The creature returns to its default state, looking forward.
        self.play(
            psi.change_state(
                "default",
                look_straight=True,
                change_mouth_to="neutral",
                run_time=2
            )
        )
        self.wait()

        # --- ACTION 4: Demonstrate Sclera Bend ---
        # Creature looks up and left, bending its eyes in anticipation
        self.play(
            psi.change_state(
                psi.current_state_name,
                look_at_target=UP+LEFT,
                bend_direction=UP+LEFT,
                change_mouth_to="happy",
                bend_intensity=0.5
            )
        )
        self.wait()

        # Reset the bend
        self.play(psi.change_state(psi.current_state_name, reset_sclera=True))
        self.wait()