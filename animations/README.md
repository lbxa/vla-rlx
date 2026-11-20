# PCA-guided residual RL animation

A five-stage Manim Community scene adapted from the supplied two-link arm script:
frozen base policy, PCA of residuals, shaped exploration, RL integration, and an
explicitly hypothetical benchmark comparison. The residual cloud is synthetic;
the successful reach is scripted with inverse kinematics, not learned by RL.

Visual style: pure black background, off-white Baskerville text and mathematical
typesetting, open layouts with no panels or boxed labels, and color reserved for
the mathematical geometry. Baskerville is provided by macOS on this machine.
Short titles and essential mathematical labels replace running subtitles; the
policy integration uses an equation diagram rather than a dense flowchart.

From the repository root, render a fast preview:

```sh
uv run --locked --project animations manim -pql --media_dir animations/media -o pca_residual_rl_black animations/pca_residual_rl_arm.py PCAGuidedResidualRL
```

Render at 1080p, 30 fps:

```sh
uv run --locked --project animations manim -pqh --fps 30 --media_dir animations/media -o pca_residual_rl_black animations/pca_residual_rl_arm.py PCAGuidedResidualRL
```

The MP4 is `animations/media/videos/pca_residual_rl_arm/1080p30/pca_residual_rl_black.mp4`.
The `-p` option opens it after rendering. Output and caches are ignored by Git.
Manim is pinned to 0.21.0 in a separate environment. System Cairo/Pango and LaTeX
with `dvisvgm` are required for rendering this scene; they were already installed
on the machine used for the preview.

The target is reachable, the arm uses fixed-length forward kinematics, and the
green path terminates at the target. PCA is computed from 48 seeded samples;
the centered covariance is normalized to trace 2 before blending with identity,
so the noise-shaping animation preserves total variance. Grey candidate paths
use samples from that shaped covariance. Neither PCA nor the scripted reach
demonstrates successful training. The 1,000 versus 450 trajectories in the final
chart are placeholder numbers, with bar heights in the correct 1 : 0.45 ratio.

For PPO/SAC, this is a conceptual covariance module: a real implementation must
account for the full shaped policy distribution and tanh transform in its
log-probability / entropy calculations. No RL algorithm is implemented here.

Reference: [Manim Community documentation](https://docs.manim.community/en/stable/reference.html).
