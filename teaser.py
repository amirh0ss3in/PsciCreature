from manim import *
from psi_creature import PsiCreature

class Teaser(Scene):
    def construct(self):
        psi = PsiCreature(body_scale=3, eye_color=BLUE_C)
        self.play(FadeIn(psi))
        self.wait(1)

        # Set up the initial state
        self.play(psi.change_state("pondering"))
        self.play(psi.squint(PI / 5), run_time=1)
        self.wait(1)

        # Add a dot to look at
        look_dot = Dot(color=RED).set_z_index(10)
        look_dot.move_to(psi.get_center() + UP + 3*RIGHT)
        self.play(FadeIn(look_dot))

        # --- THE NEW, CORRECTED WAY ---
        # All actions are declared in one call, creating one fluid animation.
        self.play(
            psi.change_state_and_animate(
                new_state_name="hand_up",
                look_at_target=look_dot,
                reset_squint_flag=True
            )
        )
        
        self.wait(1)
        
        # self.play(psi.change_state("hand_up"))
        # self.play(psi.reset_squint())
        # self.play(psi.look_at(look_dot))

        # self.play(psi.change_mouth("happy"))
        # self.wait(1)
        # self.play(FadeOut(look_dot))
        # self.play(psi.change_mouth("sad"))
        # self.wait(1)
        # self.play(psi.change_state("default"))
        # self.wait(1)
        # self.play(psi.change_state("pondering"))
        # self.wait(1)
        # self.play(psi.change_mouth("happy"))
        # self.wait(1)
        # self.play(psi.change_mouth("sad"))
        # self.wait(1)
        # self.play(psi.change_mouth("unsure"))
        # self.wait(1)
        # self.play(psi.change_mouth("happy_smirk"))
        # self.wait(1)
        # self.play(psi.change_mouth("sad_smirk"))
        # self.wait(1)