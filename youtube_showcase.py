# Save this file as "psi_creature_showcase.py"
# Make sure "psi_creature.py" is in the same directory.
# Then run from your terminal:
# manim -pql psi_creature_showcase.py PsiCreatureShowcase

from manim import *
from psi_creature import PsiCreature

class PsiCreatureShowcase(Scene):
    """
    A single, comprehensive scene to demonstrate the full capabilities
    of the PsiCreature class for a promotional video.
    """
    def construct(self):
        # Set a professional, dark background color
        self.camera.background_color = "#222222"

        # Define a consistent, polished style for all code blocks
        # using the parameters from the documentation.
        code_style = {
            "language": "python",
            "tab_width": 4,
            "paragraph_config": {
                "font_size": 24           # A base font size before scaling
            }
        }


        # Introduce the creature
        psi = PsiCreature(
            body_scale=3.0,
            eye_color=BLUE_C,
            initial_anchor_pos=LEFT * 4,
            initial_emotion="neutral"
        )
        anchor_dot = Dot(psi.anchor_pos, color=RED, radius=0.08).set_z_index(10)
        anchor_label = Text("anchor_pos", font_size=24).next_to(anchor_dot, DOWN, buff=0.25)
        
        def create_label(text):
            return Text(text, font_size=32).to_edge(UP)

        psi_text = Text("PsiCreature", font_size=48).move_to(ORIGIN+RIGHT)
        self.play(FadeIn(psi), run_time=1)
        self.wait(1)
        self.play(Write(psi_text, run_time=1))
        self.wait(2)
        self.play(psi.look_at(psi_text))
        self.wait(3)
        self.play(psi.look_straight())
        self.wait(1)
        self.play(psi.blink())
        self.wait(1)
        self.play(FadeOut(psi_text))
        self.wait(16)
        c_text = Text("Fully controlled with code!", font_size=42).next_to(psi.get_right(), 1.2*RIGHT)
        self.play(Write(c_text, run_time=1))
        self.wait(3)
        self.play(FadeOut(c_text))
        self.wait(1)
        self.play(FadeIn(anchor_dot), FadeIn(anchor_label))
        self.wait(1.5)
        # Demonstrate anchor-based movement
        label_move = create_label("Anchor-Based Movement: .move_anchor_to()")
        self.play(FadeIn(label_move, shift=DOWN), FadeOut(anchor_label))

        code_str_move = """
self.play(
    psi.move_anchor_to(RIGHT * 4),
)"""
        code_move = Code(code_string=code_str_move, **code_style).scale(0.8)
        code_move.next_to(label_move, DOWN, buff=0.4)
        self.play(FadeIn(code_move))

        self.play(
            psi.move_anchor_to(RIGHT * 4),
            anchor_dot.animate.move_to(RIGHT * 4),
            run_time=3
        )
        self.wait(6)
        # Demonstrate Gaze control
        self.play(FadeOut(code_move), FadeOut(label_move, shift=UP), FadeOut(anchor_dot))
        label_gaze = create_label("Gaze Control: .look_at()")
        self.play(FadeIn(label_gaze, shift=DOWN))
        self.wait(2)
        target_dot = Dot(LEFT*3 + UP*1, color=YELLOW)
        self.play(Create(target_dot))

        code_str_look = "self.play(psi.look_at(target_dot))"
        code_look = Code(code_string=code_str_look, **code_style).scale(0.8)
        code_look.next_to(label_gaze, DOWN, buff=0.4)
        self.play(FadeIn(code_look))
        self.wait(1)

        self.play(psi.look_at(target_dot))
        self.wait(2)
        self.play(target_dot.animate.move_to(RIGHT*3 + DOWN*2))
        self.play(psi.look_at(target_dot))
        self.wait(2)
        
        self.play(FadeOut(code_look))
        code_str_straight = "self.play(psi.look_straight())"
        code_straight = Code(code_string=code_str_straight, **code_style).scale(0.8)
        code_straight.next_to(label_gaze, DOWN, buff=0.4)
        self.play(FadeIn(code_straight))

        self.play(psi.look_straight())
        self.wait(1)
        self.play(FadeOut(target_dot), FadeOut(label_gaze, shift=UP), FadeOut(code_straight))
        self.wait(0.5)

        # --- PART 2: EXPRESSIONS & BODY LANGUAGE ---

        # Demonstrate Body State changes
        label_state = create_label("Body States: .change_state()")
        self.play(FadeIn(label_state, shift=DOWN))

        code_str_state = 'psi.change_state("pondering")'
        code_state = Code(code_string=code_str_state, **code_style).scale(0.8)
        code_state.next_to(label_state, DOWN, buff=0.4)
        self.play(FadeIn(code_state))

        self.play(psi.change_state("pondering", run_time=1.5))
        self.wait(10)
        
        self.play(FadeOut(code_state))

        self.play(psi.change_state("default", run_time=1.5))
        self.wait(3)
        self.play(FadeOut(label_state, shift=UP))
        self.wait(0.5)

        # Demonstrate Mouth changes
        label_mouths = create_label("Mouth Expressions: .change_mouth()")
        self.play(FadeIn(label_mouths, shift=DOWN))
        self.play(psi.move_anchor_to(ORIGIN), run_time=1)
        
        code_str_mouth_loop = """
for expr in mouth_expressions:
    psi.change_mouth(expr)
"""
        code_mouth_loop = Code(code_string=code_str_mouth_loop, **code_style).scale(0.8)
        code_mouth_loop.next_to(label_mouths, DOWN, buff=0.4)
        self.play(FadeIn(code_mouth_loop))

        mouth_expressions = ["happy", "sad", "unsure", "happy_smirk", "sad_smirk"]
        for expr in mouth_expressions:
            mouth_label = Text(f'"{expr}"', font_size=36).next_to(psi, DOWN)
            self.play(FadeIn(mouth_label, scale=0.5))
            self.play(psi.change_mouth(expr, run_time=0.2))
            self.wait(0.2)
            self.play(FadeOut(mouth_label))

        self.play(FadeOut(code_mouth_loop))
        self.play(psi.change_mouth("neutral"))
        self.play(FadeOut(label_mouths, shift=UP))
        self.wait(0.4)
    
        # bend_sclera and squint
        label_bend = create_label("Eye Expressions: .bend_sclera()")
        self.play(FadeIn(label_bend, shift=DOWN))

        code_str_bend = """
self.play(
    psi.bend_sclera(UP + RIGHT),
)
"""
        code_bend = Code(code_string=code_str_bend, **code_style).scale(0.6)
        code_bend.next_to(label_bend, DOWN, buff=0.4)
        self.play(FadeIn(code_bend))

        self.play(psi.bend_sclera(UP + RIGHT))
        self.play(FadeOut(code_bend))
        self.wait(4)
        code_str_bend = """
self.play(
    psi.bend_sclera(UP + LEFT),
)
"""
        code_bend = Code(code_string=code_str_bend, **code_style).scale(0.6)
        code_bend.next_to(label_bend, DOWN, buff=0.4)
        self.play(FadeIn(code_bend))

        self.play(psi.bend_sclera(UP + LEFT))
        self.play(FadeOut(code_bend))
        self.wait(2)
        code_str_bend = """
self.play(
    psi.bend_sclera(DOWN + LEFT, intensity=0.6),
)
"""
        code_bend = Code(code_string=code_str_bend, **code_style).scale(0.6)
        code_bend.next_to(label_bend, DOWN, buff=0.4)
        self.play(FadeIn(code_bend))

        self.play(psi.bend_sclera(DOWN + LEFT, intensity=0.6))
        self.play(FadeOut(code_bend))
        self.wait(1)

        code_reset_sclera = """
        self.play(psi.reset_sclera())
        """
        code_bend = Code(code_string=code_reset_sclera, **code_style).scale(0.6)
        code_bend.next_to(label_bend, DOWN, buff=0.4)
        self.play(FadeIn(code_bend))

        self.play(psi.reset_sclera())
        self.play(FadeOut(code_bend))
        self.wait(1)

        self.play(FadeOut(label_bend, shift=UP))
        self.wait(0.5)

        # --- PART 4: THE GRAND FINALE - COMBINED ACTIONS ---

        label_finale = create_label("Complex Multi-Part Animations")
        self.play(FadeIn(label_finale, shift=DOWN))

        dot = Dot(LEFT * 4.5, color=YELLOW)
        self.play(Create(dot))
        self.wait(1)
        self.play(psi.move_anchor_to(LEFT * 2))
        # A single, complex animation
        finale_text_1 = MarkupText("Combining actions in <b>one call</b>:", font_size=28).next_to(label_finale, DOWN, buff=0.5)
        self.play(FadeIn(finale_text_1))

        code_str_finale1 = """
psi.change_state(
    "pondering",
    look_at_target=dot,
    change_mouth_to="unsure",
    squint_amount=0.7
)"""
        code_finale1 = Code(code_string=code_str_finale1, **code_style).scale(0.8)
        code_finale1.next_to(psi.get_right(), RIGHT, buff=0.4)
        self.play(FadeIn(code_finale1))
        self.wait(3)
        self.play(
            psi.change_state(
                "pondering",
                look_at_target=dot,
                change_mouth_to="unsure",
                squint_amount=0.7,
                run_time=3
            )
        )
        self.wait(2)

        # Another complex change
        self.play(FadeOut(finale_text_1), FadeOut(code_finale1))
        finale_text_2 = MarkupText("Keeping the body state, but changing expression:", font_size=28).next_to(label_finale, DOWN, buff=0.5)
        self.play(FadeIn(finale_text_2))
        
        code_str_finale2 = """
psi.change_state(
    psi.current_state_name,
    change_mouth_to="happy_smirk",
    reset_squint=True
)"""
        code_finale2 = Code(code_string=code_str_finale2, **code_style).scale(0.8)
        code_finale2.next_to(psi.get_right(), RIGHT, buff=0.4)
        self.play(FadeIn(code_finale2))

        self.play(
            psi.change_state(
                psi.current_state_name,
                change_mouth_to="happy_smirk",
                reset_squint=True,
                run_time=2
            )
        )
        self.wait(2.5)

        # Final reset
        self.play(FadeOut(code_finale2),FadeOut(finale_text_2))
        finale_text_3 = MarkupText("And a smooth reset to the default state.", font_size=28).next_to(label_finale, DOWN, buff=0.5)
        code_str_finale2 = """
psi.change_state("default",
                look_straight=True,
                change_mouth_to="neutral")"""
        code_finale2 = Code(code_string=code_str_finale2, **code_style).scale(0.7)
        code_finale2.next_to(psi.get_right(), RIGHT, buff=0.4)
        self.play(FadeIn(code_finale2),FadeIn(finale_text_3))

        self.play(
            psi.change_state(
                "default",
                look_straight=True,
                change_mouth_to="neutral",
                run_time=2.5
            )
        )
        self.wait(6)

        # --- OUTRO ---
        self.play(FadeOut(dot), FadeOut(label_finale), FadeOut(finale_text_3), FadeOut(code_finale2))
        self.play(psi.move_anchor_to(LEFT * 4.5))

        final_text = Text("Now Available at:", font_size=48)
        url = Text("github.com/amirh0ss3in/PsiCreature", font_size=42).next_to(final_text, DOWN)
        fu = VGroup(final_text, url).next_to(psi.get_right(), 0.6*RIGHT, buff=0.4).scale(0.7)

        self.play(Write(fu))
        self.play(psi.change_state("pondering", look_at_target=url, change_mouth_to="happy"))
        self.wait(30)
        self.play(FadeOut(fu), FadeOut(psi))
        self.wait(1)
        