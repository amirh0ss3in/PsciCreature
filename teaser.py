from manim import *
from psi_creature import PsiCreature

class Teaser(Scene):
    def construct(self):
        psi = PsiCreature(body_scale=3, eye_color=BLUE_C)
        self.play(FadeIn(psi))
        self.wait(1)
        self.play(psi.change_state("pondering"))
        self.wait(1)
        self.play(psi.change_state("hand_up"))
        self.wait(1)
        self.play(psi.change_state("default"))