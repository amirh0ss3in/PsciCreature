from manim import *
from psi_creature import PsiCreature
# ====================================================================
#  UPDATED: Test Scene demonstrating all features
# ====================================================================

class MultiPartTest(Scene):
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
        self.play(psi.resize(4/3)) # change body scale from 3 to 4
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


class TestMouthExpressions(Scene):
    def construct(self):
        title = Text("Testing Mouth Expressions and Integration").to_edge(UP)
        self.add(title)

        # 1. Create creature with non-default stroke width
        psi = PsiCreature(
            body_scale=3.0, 
            eye_color=PURPLE_B,
        )
        self.play(FadeIn(psi))
        self.wait(1)

        # 2. Cycle through mouth expressions
        self.play(psi.change_mouth("happy", run_time=0.5))
        self.wait(1)
        self.play(psi.change_mouth("sad", run_time=0.5))
        self.wait(1)
        self.play(psi.change_mouth("unsure", run_time=0.7))
        self.wait(1)
        self.play(psi.change_mouth("happy_smirk", run_time=0.7))
        self.wait(1)
        self.play(psi.change_mouth("sad_smirk", run_time=0.7))
        self.wait(1)
        
        # 3. Test that mouth moves correctly with the body
        self.play(psi.move_anchor_to(LEFT * 4))
        self.play(psi.change_state("pondering"))
        self.play(psi.change_mouth("happy_smirk"))
        self.wait(2)

        # 4. Test that mouth resizes correctly.
        #    Notice the mouth stroke becomes thinner and the 'unsure' expression
        #    is proportionally less intense, maintaining the same look.
        self.play(psi.move_anchor_to(ORIGIN), psi.resize(0.5, run_time=2))
        self.wait(1)

        # 5. Prove the resized mouth can still change expressions correctly.
        self.play(psi.change_mouth("happy"))
        self.play(psi.blink())
        self.wait(2)