from manim import *
from psi_creature import PsiCreature
import random

random.seed(42)

class TheStormTeaser(Scene):
    def construct(self):
        # ====================================================================
        #  BEAT 1: The Single Symbol (0-3s)
        #  A single symbol appears. The creature is curious.
        # ====================================================================
        psi = PsiCreature(initial_anchor_pos = 4*LEFT, body_scale=2.5, eye_color=BLUE_C)
        plus_one = MathTex("+1", font_size=96).move_to(RIGHT * 2)

        self.play(
            FadeIn(psi),
            Write(plus_one)
        )
        self.play(psi.look_at(plus_one))
        self.wait(1)


        # ====================================================================
        #  BEAT 2: The Swarm Begins (3-8s)
        #  More symbols appear, accelerating. The creature becomes unsure.
        # ====================================================================
        rejection_buffer = 0.75
        no_spawn_top = psi.get_top()[1] + rejection_buffer
        no_spawn_bottom = psi.get_bottom()[1] - rejection_buffer
        no_spawn_left = psi.get_left()[0] - rejection_buffer
        no_spawn_right = psi.get_right()[0] + rejection_buffer
        # --- END SETUP ---

        swarm = VGroup()
        for _ in range(20):
            symbol_str = random.choice(["+1", "-1"])
            symbol = MathTex(symbol_str, font_size=random.randint(24, 60))
            
            # Keep generating a random point until it's outside the no-spawn zone
            while True:
                x_pos = random.uniform(-self.camera.frame_width/2, self.camera.frame_width/2)
                y_pos = random.uniform(-self.camera.frame_height/2, self.camera.frame_height/2)
                
                is_inside_box = (
                    no_spawn_left < x_pos < no_spawn_right and
                    no_spawn_bottom < y_pos < no_spawn_top
                )
                
                if not is_inside_box:
                    # This point is valid, so we break the loop
                    target_pos = np.array([x_pos, y_pos, 0])
                    break
            
            symbol.move_to(target_pos)
            symbol.set_opacity(random.uniform(0.3, 0.8))
            swarm.add(symbol)

        self.play(
            FadeOut(plus_one),
            # The creature's expression changes as the chaos begins.
            LaggedStart(
                *[FadeIn(s, scale=0.5) for s in swarm],
                lag_ratio=0.05,
                run_time=3
            )
        )
        self.play(psi.change_mouth("unsure", run_time=1))

        self.wait(0.5)

        # # ====================================================================
        # #  BEAT 3: The Storm (8-15s)
        # #  Chaos intensifies. Overwhelming numbers flash. The creature is stressed.
        # # ====================================================================
        rejection_buffer = 0.5 # A slightly smaller buffer for the smaller creature
        no_spawn_top = psi.get_top()[1] + rejection_buffer
        no_spawn_bottom = psi.get_bottom()[1] - rejection_buffer
        no_spawn_left = psi.get_left()[0] - rejection_buffer
        no_spawn_right = psi.get_right()[0] + rejection_buffer
        # --- END SETUP ---

        more_symbols = VGroup()
        for _ in range(60):
            symbol_str = random.choice(["+1", "-1"])
            symbol = MathTex(symbol_str, font_size=random.randint(30, 60))
            
            # Same rejection sampling logic as before
            while True:
                x_pos = random.uniform(-self.camera.frame_width/2, self.camera.frame_width/2)
                y_pos = random.uniform(-self.camera.frame_height/2, self.camera.frame_height/2)
                is_inside_box = (
                    no_spawn_left < x_pos < no_spawn_right and
                    no_spawn_bottom < y_pos < no_spawn_top
                )
                if not is_inside_box:
                    target_pos = np.array([x_pos, y_pos, 0])
                    break
            
            symbol.move_to(target_pos)
            more_symbols.add(symbol)
            


        # # The creature shrinks, becoming overwhelmed and sad.
        self.play(LaggedStart(*[FadeIn(s) for s in more_symbols], lag_ratio=0.01, run_time=2))
        self.play(psi.change_state(psi.current_state_name, change_mouth_to="sad", run_time=2))

        # ====================================================================
        #  BEAT 4: Hard Cut to Black (15-16s)
        #  Sudden silence and darkness for impact.
        # ====================================================================
        self.play(FadeOut(swarm, more_symbols), run_time=0.25)
        self.wait(1)

        n10 = MathTex("2^{10}", font_size=120, color=YELLOW).set_z_index(100).next_to(psi.get_right() + 2*RIGHT)
        n30 = MathTex("2^{30}", font_size=140, color=ORANGE).set_z_index(100).next_to(psi.get_right() + 2*RIGHT)
        n300 = MathTex("2^{300}", font_size=160, color=RED).set_z_index(100).next_to(psi.get_right() + 2*RIGHT)

        self.play(psi.look_at(n10))
        self.play(Write(n10), run_time=0.3)
        self.play(psi.change_state("pondering", change_mouth_to="unsure", squint_amount=PI/6))
        self.wait(1.5)
        self.play(FadeOut(n10), run_time=0.2)
        self.play(Write(n30), run_time=0.3)
        self.wait(1.5)
        self.play(FadeOut(n30), run_time=0.2)
        self.play(Write(n300), run_time=0.3)
        self.play(psi.change_state("default", change_mouth_to="sad_smirk", reset_squint=True))
        self.wait(1.5)
        self.play(FadeOut(n300), run_time=0.2)
        self.wait(0.5)

        # ====================================================================
        #  BEAT 5: The Calm Reveal (16-22s)
        #  The simple solution appears. The creature is relieved and intrigued.
        # ====================================================================
        solution = VGroup(
            Rectangle(width=3, height=2, color=BLUE_B, fill_opacity=1, stroke_width=0),
            Rectangle(width=3, height=2, color=RED_B, fill_opacity=1, stroke_width=0)
        ).arrange(RIGHT, buff=0)

        
        # self.play(FadeIn(psi))
        self.play(psi.move_anchor_to(solution.get_left() + 2*LEFT))


        # ====================================================================
        #  BEAT 6: The Hook (22-30s)
        #  The creature addresses the viewer. The mysterious title appears.
        # ====================================================================
        self.play(FadeIn(solution, scale=0.8))
        self.play(psi.change_state("pondering", change_mouth_to="happy_smirk", look_at_target=solution, bend_direction=RIGHT+UP, bend_intensity=0.1))
        title = Text("This Weird Approximation Solves an Impossible Problem.", font_size=32, weight=BOLD).to_edge(UP)
        self.play(Write(title))
        self.wait(2)

        self.play(FadeOut(solution))

        self.play(
            psi.change_state(new_state_name="hand_up",
                             look_at_target=title,
                             change_mouth_to="happy",
                             reset_squint=True)
        )
        self.wait(2)
        self.play(FadeOut(psi),
                  title.animate.move_to(ORIGIN))
        subtitle = Text("Coming Soon!", font_size=28, color=GRAY_A).next_to(title, 2*DOWN)
        self.play(FadeIn(subtitle, shift=UP))
        self.wait(2.5)