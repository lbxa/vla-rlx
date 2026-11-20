"""A synthetic, reproducible illustration of PCA-shaped residual exploration.

Render from the repository root:
    uv run --project animations manim -qm --media_dir animations/media -o pca_residual_rl_black \
        animations/pca_residual_rl_arm.py PCAGuidedResidualRL
"""

import numpy as np
from manim import (
    DOWN, LEFT, RIGHT, UP, Arrow, Axes, Circle, Create, DashedLine, Dot,
    FadeIn, FadeOut, Flash, GrowArrow, GrowFromEdge, Indicate,
    LaggedStart, Line, MathTex, Rectangle,
    Scene, Text, TracedPath, Transform, VGroup,
    VMobject, ValueTracker, always_redraw, linear,
)


BG = "#000000"
INK = "#F0EDE6"
MUTED = "#AAA8A2"
BLUE = "#58C4DD"
RED = "#FC6255"
GOLD = "#FFFF00"
TEAL = "#5CD0B3"
GREEN = "#83C167"
BASE = np.array([-5.65, -1.60, 0.0])
LENGTHS = (2.3, 1.75)
TARGET = np.array([-2.05, 0.10, 0.0])
START = np.deg2rad([85.0, -125.0])
BASE_STOP = np.deg2rad([43.0, -69.0])
SEED = 7


def forward_kinematics(angles):
    """Return the fixed base, elbow and end effector in scene coordinates."""
    a, b = angles
    elbow = BASE + LENGTHS[0] * np.array([np.cos(a), np.sin(a), 0.0])
    tip = elbow + LENGTHS[1] * np.array([np.cos(a + b), np.sin(a + b), 0.0])
    return BASE.copy(), elbow, tip


def inverse_kinematics(target):
    """Elbow-up solution for a reachable 2D target; reject unreachable inputs."""
    x, y = (np.asarray(target) - BASE)[:2]
    l1, l2 = LENGTHS
    cosine = (x * x + y * y - l1 * l1 - l2 * l2) / (2 * l1 * l2)
    if not -1.0 <= cosine <= 1.0:
        raise ValueError("Target is outside the two-link arm's reachable workspace")
    b = -np.arccos(cosine)
    a = np.arctan2(y, x) - np.arctan2(l2 * np.sin(b), l1 + l2 * np.cos(b))
    return np.array([a, b])


def residual_pca():
    """Fit PCA to synthetic joint corrections oriented around the desired reach.

    Center the samples and normalize total variance to two. This keeps the
    overall exploration variance fixed when interpolating from identity to C.
    The data is a schematic construction, not collected robot rollouts.
    """
    rng = np.random.default_rng(SEED)
    direction = inverse_kinematics(TARGET) - BASE_STOP
    direction /= np.linalg.norm(direction)
    basis = np.column_stack([direction, [-direction[1], direction[0]]])
    samples = rng.normal(size=(48, 2)) @ np.diag([1.25, 0.32]) @ basis.T
    samples -= samples.mean(axis=0)
    samples *= np.sqrt(2.0 / np.trace(np.cov(samples, rowvar=False)))
    values, vectors = np.linalg.eigh(np.cov(samples, rowvar=False))
    values, vectors = values[::-1], vectors[:, ::-1]
    # Fix the otherwise arbitrary eigenvector sign for a stable illustration.
    if vectors[:, 0] @ direction < 0:
        vectors[:, 0] *= -1
    return samples, values, vectors


def label(text, size=24, position=None):
    result = Text(text, font="Baskerville", font_size=size, color=INK)
    if position is not None:
        result.move_to(position)
    return result


class PCAGuidedResidualRL(Scene):
    """Five stages: frozen policy, PCA, shaped exploration, RL wiring, hypothesis."""

    def heading(self, title):
        return label(title, 39).to_edge(UP, buff=0.5)

    def arm(self, angles):
        base, elbow, tip = forward_kinematics(angles)
        return VGroup(
            Line(base, elbow, stroke_width=12, color=BLUE),
            Line(elbow, tip, stroke_width=10, color=BLUE),
            Dot(base, radius=0.105, color=INK),
            Dot(elbow, radius=0.095, color=INK),
            Dot(tip, radius=0.09, color=BLUE),
        ).set_z_index(4)

    def trajectory(self, start, end, color, width=3, opacity=1):
        points = [forward_kinematics((1 - t) * start + t * end)[2]
                  for t in np.linspace(0, 1, 70)]
        return VMobject().set_points_as_corners(points).set_stroke(color, width, opacity)

    def contour(self, plane, values, vectors, color=GOLD, radius=1.8):
        angles = np.linspace(0, 2 * np.pi, 121)
        circle = np.array([np.cos(angles), np.sin(angles)])
        points = radius * vectors @ np.diag(np.sqrt(values)) @ circle
        return VMobject().set_points_as_corners(
            [plane.c2p(x, y) for x, y in points.T]
        ).set_stroke(color, 3).set_fill(color, 0.045)

    def clear_stage(self):
        # Stop traces and dynamic geometry before fading to the next chapter.
        for mob in self.mobjects:
            mob.clear_updaters(recursive=True)
        self.play(*[FadeOut(mob) for mob in list(self.mobjects)], run_time=0.7)
        self.clear()

    def construct(self):
        self.camera.background_color = BG
        self.robot_and_pca()
        self.clear_stage()
        self.rl_integration()
        self.clear_stage()
        self.benchmark_hypothesis()

    def robot_and_pca(self):
        heading = self.heading("Base policy + residual")
        ground = Line(BASE + [-0.35, -0.16, 0], BASE + [0.35, -0.16, 0],
                      color=INK, stroke_width=2)
        target = Circle(radius=0.15, color=GREEN, fill_opacity=0.15).move_to(TARGET)
        target_label = label("target", 21).next_to(target, UP, buff=0.2)
        theta1, theta2 = ValueTracker(START[0]), ValueTracker(START[1])
        robot = always_redraw(lambda: self.arm([theta1.get_value(), theta2.get_value()]))
        frozen = label("Frozen base policy", 28, [3.35, 0.95, 0])
        formula = MathTex(r"a_t = a_t^{(0)} + \delta a_t", font_size=48, color=INK)
        formula.move_to([3.35, -0.10, 0])
        self.play(FadeIn(heading), run_time=1)
        self.play(Create(ground),
                  FadeIn(target), FadeIn(target_label), FadeIn(robot),
                  FadeIn(frozen), FadeIn(formula), run_time=1)
        trace = TracedPath(lambda: forward_kinematics(
            [theta1.get_value(), theta2.get_value()])[2],
            stroke_color=RED, stroke_width=4)
        self.add(trace)
        self.play(theta1.animate.set_value(BASE_STOP[0]),
                  theta2.animate.set_value(BASE_STOP[1]), run_time=3)
        trace.clear_updaters()
        miss_point = forward_kinematics(BASE_STOP)[2]
        gap = DashedLine(miss_point, TARGET, color=RED, stroke_width=2, dash_length=0.07)
        self.play(Create(gap), Indicate(target, color=GREEN), run_time=0.8)
        self.wait(1.8)

        # PCA directions are fitted to centered residual corrections.
        self.play(Transform(heading, self.heading("PCA of synthetic residuals")),
                  FadeOut(frozen), FadeOut(formula), run_time=0.8)
        plane = Axes(
            x_range=[-4, 4, 1], y_range=[-4, 4, 1], x_length=4.4, y_length=4.4,
            axis_config={"stroke_color": INK, "stroke_opacity": 0.5,
                         "stroke_width": 1.2, "include_ticks": False},
            tips=False,
        ).move_to([3.35, -0.10, 0])
        x_label = MathTex(r"\Delta\theta_1", font_size=25, color=INK).next_to(plane, RIGHT, buff=0.10)
        y_label = MathTex(r"\Delta\theta_2", font_size=25, color=INK).next_to(plane, LEFT, buff=0.1)
        y_label.shift(UP * 1.2)
        samples, values, vectors = residual_pca()
        dots = VGroup(*[Dot(plane.c2p(x, y), radius=0.035, color=INK) for x, y in samples])
        ellipse = self.contour(plane, values, vectors)
        center = plane.c2p(0, 0)
        pc_arrows, pc_labels = VGroup(), VGroup()
        for i, (name, color) in enumerate([("PC1", GOLD), ("PC2", TEAL)]):
            end = plane.c2p(*(1.8 * np.sqrt(values[i]) * vectors[:, i]))
            arrow = Arrow(center, end, buff=0, color=color, stroke_width=4,
                          max_tip_length_to_length_ratio=0.14)
            pc_arrows.add(arrow)
            pc_labels.add(label(name, 21).next_to(arrow.get_end(),
                                                UP if i == 0 else LEFT, buff=0.16))
        variance = label(f"PC1: {values[0] / values.sum():.0%} of variance", 26,
                         [3.35, -2.65, 0])
        self.play(Create(plane), FadeIn(x_label), FadeIn(y_label), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(dot) for dot in dots], lag_ratio=0.025), run_time=1.8)
        self.play(Create(ellipse), *[GrowArrow(arrow) for arrow in pc_arrows], run_time=1.5)
        self.play(FadeIn(pc_labels), FadeIn(variance), run_time=0.6)
        self.wait(2.2)

        # The interpolated covariance has fixed trace, so only its shape changes.
        self.play(Transform(heading, self.heading("Shape the exploration")),
                  FadeOut(dots), FadeOut(ellipse), FadeOut(pc_arrows),
                  FadeOut(pc_labels), FadeOut(variance), run_time=0.8)
        rho = ValueTracker(0)
        noise_shape = always_redraw(lambda: self.contour(
            plane, (1 - rho.get_value()) + rho.get_value() * values, vectors))
        circle = self.contour(plane, np.ones(2), np.eye(2), MUTED).set_stroke(opacity=0.35)
        blend_formula = MathTex(r"K=(1-\rho)I+\rho\,U\Lambda U^{\mathsf T}",
                                font_size=32, color=INK).move_to([3.35, -2.65, 0])
        self.play(FadeIn(circle), FadeIn(noise_shape), FadeIn(blend_formula),
                  run_time=0.8)
        self.wait(0.7)
        self.play(rho.animate.set_value(0.85), run_time=3, rate_func=linear)
        noise_shape.clear_updaters()
        self.wait(1)

        # Candidate joint trajectories are samples from the fitted noise model.
        rng = np.random.default_rng(SEED + 1)
        noise_root = vectors @ np.diag(np.sqrt(0.15 + 0.85 * values))
        goal = inverse_kinematics(TARGET)
        correction = goal - BASE_STOP
        candidate_ends = [BASE_STOP + 0.7 * correction + 0.22 * noise_root @ epsilon
                          for epsilon in rng.normal(size=(6, 2))]
        paths = VGroup(*[self.trajectory(BASE_STOP, end, MUTED, 2, 0.55)
                         for end in candidate_ends])
        self.play(FadeOut(gap),
            LaggedStart(*[Create(path) for path in paths], lag_ratio=0.12), run_time=1.8)
        self.wait(0.8)
        corrected_trace = TracedPath(lambda: forward_kinematics(
            [theta1.get_value(), theta2.get_value()])[2], stroke_color=GREEN, stroke_width=5)
        self.add(corrected_trace)
        self.play(theta1.animate.set_value(goal[0]), theta2.animate.set_value(goal[1]), run_time=3)
        corrected_trace.clear_updaters()
        self.play(Flash(TARGET, color=GREEN, line_length=0.12, flash_radius=0.2), run_time=0.7)
        self.wait(2.3)

    def rl_integration(self):
        heading = self.heading("PCA shapes the residual policy")
        base = MathTex(r"a_t^{(0)}", font_size=52, color=INK).move_to([-3.5, 1.05, 0])
        frozen = label("frozen", 23).next_to(base, UP, buff=0.22)
        residual = MathTex(
            r"b\odot\tanh(", r"m_\theta(s_t)", "+", r"L\epsilon_t", ")",
            font_size=43, color=INK,
        ).move_to([-2.7, -0.7, 0])
        plus = MathTex("+", font_size=52, color=INK).move_to([1.4, 1.05, 0])
        action = MathTex(r"a_t", font_size=52, color=INK).move_to([3.15, 1.05, 0])
        robot = label("Robot", 32, [5.15, 1.05, 0])
        connections = [
            (base.get_right(), plus.get_left(), RED),
            (residual.get_right(), plus.get_bottom(), BLUE),
            (plus.get_right(), action.get_left(), INK),
            (action.get_right(), robot.get_left(), INK),
        ]
        arrows = VGroup(*[Arrow(start, end, buff=0.16, color=color, stroke_width=2.5,
                               max_tip_length_to_length_ratio=0.12)
                           for start, end, color in connections])
        covariance = MathTex(r"LL^{\mathsf T}=K", font_size=38, color=INK)
        covariance.move_to([residual[3].get_center()[0], -2.05, 0])
        noise_arrow = Arrow(covariance.get_top(), residual[3].get_bottom(),
                            buff=0.15, color=GOLD, stroke_width=2.5,
                            max_tip_length_to_length_ratio=0.15)
        epsilon = MathTex(r"\epsilon_t\sim\mathcal{N}(0,I)", font_size=34, color=INK)
        epsilon.move_to([-4.35, -2.05, 0])
        algorithms = label("TD3  ·  PPO  ·  SAC", 25, [0, -3.25, 0])
        self.play(FadeIn(heading), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(mob) for mob in [base, frozen, residual, plus, action, robot]],
                             lag_ratio=0.12), run_time=1.7)
        self.play(LaggedStart(*[GrowArrow(arrow) for arrow in arrows], lag_ratio=0.08), run_time=1.8)
        self.play(FadeIn(covariance), FadeIn(epsilon), GrowArrow(noise_arrow), run_time=1.2)
        self.play(FadeIn(algorithms), run_time=0.8)
        self.wait(4)

    def benchmark_hypothesis(self):
        heading = self.heading("A sample-efficiency hypothesis")
        origin_y = -1.55
        chart_left, chart_right = -5.8, -0.6
        ticks = VGroup()
        for value in [0, 500, 1000]:
            y = origin_y + value / 1000 * 2.7
            ticks.add(Line([chart_left, y, 0], [chart_right, y, 0],
                           color=INK, stroke_width=1, stroke_opacity=0.15))
            ticks.add(label(str(value), 19, [chart_left - 0.4, y, 0]))
        bars, names, counts = VGroup(), VGroup(), VGroup()
        for x, value, name, color in [(-4.4, 1000, "Vanilla\nresidual RL", RED),
                                      (-2.1, 450, "PCA-guided\nresidual RL", GREEN)]:
            height = value / 1000 * 2.7
            bar = Rectangle(width=1, height=height, color=color,
                            fill_color=color, fill_opacity=0.8, stroke_width=0)
            bar.move_to([x, origin_y + height / 2, 0])
            bars.add(bar)
            names.add(label(name, 23, [x, origin_y - 0.48, 0]))
            counts.add(label(f"{value:,}", 29).next_to(bar, UP, buff=0.16))
        chart_title = label("Trajectories to 95% success", 23, [-3.3, 1.91, 0])
        figure = label("55%", 86, [3.1, 0.35, 0])
        explanation = label("fewer trajectories", 27,
                            [3.1, -0.65, 0])
        caveat = label("Illustrative values — not measured results", 23, [0, -3.15, 0])
        self.play(FadeIn(heading), FadeIn(chart_title), FadeIn(ticks), FadeIn(caveat), run_time=0.9)
        self.play(*[GrowFromEdge(bar, DOWN) for bar in bars], FadeIn(names), run_time=1.4)
        self.play(FadeIn(counts), FadeIn(figure), FadeIn(explanation), run_time=1)
        self.wait(4.5)
