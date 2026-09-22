# SO101 MuJoCo environments

A small task suite built directly on MuJoCo, with Gymnasium's `reset` / `step`
interface. Task names and goals follow [the thesis](https://vla.lbxa.net/).
The white SO101 includes its physical wrist camera and mount.

## Run

From the workspace root:

```sh
uv run --package sim sim
uv run --package sim sim --env rubix-stack-v1 --seed 42
uv run --package sim sim --list-envs
uv run --package sim sim --robot-only
```

Inside `sim/`, omit `--package sim`: `uv run sim`.
The entry point is in `sim/pyproject.toml`. `launch.py` sets up uv's Python
shared-library path and uses `mjpython` on macOS, as required by MuJoCo's
[passive viewer](https://mujoco.readthedocs.io/en/stable/python.html#passive-viewer).

Expand **Control** to move joints with the sliders. Press **R** to reset, drag to
orbit, and scroll to zoom. On success or a workspace exit the task pauses until
reset. The interactive viewer has no time limit; Python episodes last at most
30 simulated seconds. `--robot-only` opens the original arm-and-floor scene.

## Tasks

| ID | Status | Goal |
| --- | --- | --- |
| `rubix-stack-v1` | Implemented | Stack the smaller cube on the larger one. |
| `bus-table-easy-v1` | Stub | Put a few pens and a glue stick in a pen holder. |
| `bus-table-medium-v1` | Stub | Clear more objects, including a new pen geometry. |
| `bus-table-hard-v1` | Stub | Clear a cluttered table with varied pens. |
| `close-bottle-lid-v1` | Stub | Seat the metal lid on the bottle. |
| `erase-whiteboard-v1` | Stub | Wipe a red stroke off the whiteboard with a cloth. |
| `close-french-press` | Stub | Place the lid and push the plunger down. |

The spelling `rubix` and the unversioned French press ID match the thesis.
Selecting a stub raises `NotImplementedError` with its task ID.

## Use from Python

```python
import gymnasium as gym
import sim.envs  # Registers the seven IDs.

with gym.make("rubix-stack-v1", render_mode="rgb_array") as env:
    observation, info = env.reset(seed=42)
    action = [0, 0, 0, 0, 0, 1]  # Hold the starting pose, with the gripper open.
    observation, reward, terminated, truncated, info = env.step(action)
    image = env.render()  # 480 x 640 RGB uint8 array; omit render_mode for headless use.
```

Actions are six **absolute joint angles in radians**, in this order:
`shoulder_pan`, `shoulder_lift`, `elbow_flex`, `wrist_flex`, `wrist_roll`, `gripper`.
Finite targets are clipped to the imported actuator limits. The gripper uses
radians, not LeRobot's 0–100 scale. Each action runs ten 2 ms physics steps (50 Hz).

Observations are independent NumPy arrays in a dictionary:

- `robot`: `(position, velocity)` for each of the six joints, in action order.
- `cubes`: small then large; each has position XYZ, quaternion WXYZ, linear
  velocity XYZ and angular velocity XYZ (MuJoCo free-joint coordinates).
- `task`: grasp recorded, lift recorded, and fraction of the stable hold completed.

These are simulation state observations. Images come separately from `render()`;
`camera="front"` or `camera="top"` selects the view. The wrist camera asset is
physical geometry, not yet a calibrated rendered camera or a VLA observation pipeline.

## Rubik's stack defaults

The cubes are rigid boxes with decorative 3×3 face tiles, not twistable puzzles.
Their edges default to **40 mm** and **57 mm**, as agreed; pass `small_cube_size`
and `large_cube_size` to `gym.make` to change them (metres, smaller < larger,
maximum 80 mm). Reset randomizes non-overlapping tabletop positions, yaw rotations,
and the assignment of the six face colours, reproducibly with `seed`.

The tabletop is 56 × 50 cm with its surface at z=0. The arm faces +X; spawn
positions are x=14–28 cm and y=−13–13 cm. The cubes have provisional masses of
60 g and 90 g and sliding friction 1.0. These are simulation defaults to calibrate
against the real setup, not measurements from the thesis.

Reward is **1 on success, 0 otherwise**. Success requires:

1. The small cube contacted both gripper fingers and was lifted at least 15 mm
   clear of the tabletop.
2. Its footprint fits on the larger cube, with physical contact between them
   and between the larger cube and the table.
3. Both cubes are released from the robot and nearly stationary for 0.5 seconds.

A cube crossing a tabletop edge or falling below the table ends the episode with
zero reward. The Gymnasium time limit sets `truncated=True` after 1,500 actions;
success or workspace exit sets `terminated=True`. Reset after either. `info`
reports `is_success`, `has_grasped`, `has_lifted`, `is_stacked`,
`out_of_workspace`, and `stable_seconds`. This sparse reward is not the thesis's
manually scored DTP metric. No controller or trained policy is included.

## Read and change the code

1. `envs/__init__.py`: the seven task registrations; `stubs.py` holds placeholders.
2. `envs/rubix_scene.py`: load our scene with MuJoCo's
   [MjSpec](https://mujoco.readthedocs.io/en/stable/python.html#model-editing),
   add the table, cubes and cameras, then compile.
3. `envs/rubix_stack.py`: reset, physics stepping, observations and success checks.
4. `main.py`: choose an environment and run the passive viewer.
5. `appearance.py`: set named printed-part materials to white in memory.

Keep `assets/` and `so101-nexus-main/` pristine. Our `scene.xml` includes
`assets/so101_new_calib_camera.xml`; all task geometry and appearance overrides
are applied in our own files. The imported XML retains its original materials,
and its mesh directory remains `assets/assets/`. The reference project inspired
the Gymnasium interface; its training framework is not a runtime dependency.

Run the headless checks from the workspace root:

```sh
uv run --package sim python -m unittest discover -s sim/tests -v
```

The tests cover the Gymnasium contract, seeding, physics, stack detection,
workspace exits and stubs. The stack detector test uses a synthetic stacked state;
it does not demonstrate a robot policy completing the task.

## Modal image

Deploy `modal_image.py` using the workspace venv, from the workspace root:

```sh
.venv/bin/python -m modal deploy sim/modal_image.py
```

With the venv activated and `sim/` as the working directory, use
`modal deploy modal_image.py`. If authentication has expired, run
`.venv/bin/python -m modal setup` from the workspace root. Deployment also needs
network access from the Codex sandbox.

The image installs upstream Isaac-GR00T into the container's Python environment
and records the cloned commit in `/opt/gr00t-revision.txt`. It uses
`uv sync --frozen --inexact`: `--frozen` consumes the upstream lockfile as-is,
avoiding the cross-platform FlashAttention metadata error during lockfile
validation; `--inexact` retains Modal and `ipykernel`. Changes to upstream
`pyproject.toml` must already be reflected in its lockfile.

The image also includes `ipywidgets` for tqdm's notebook progress bars and checks
that a widget-backed progress bar can be created during the build. After changing
the image, use the updated image for your notebook runtime. For an already
running kernel that reports `IProgress not found`, run `%pip install ipywidgets`
in a notebook cell and restart the kernel before reimporting tqdm.

Keep each `run_commands` argument on one shell-command line: a leading newline
produces an empty Docker `RUN` instruction. Dependency installation and import
checks use separate image layers so changing a check can reuse the installation.
See [Modal's image guide](https://modal.com/docs/guide/images) and
[uv's sync documentation](https://docs.astral.sh/uv/concepts/projects/sync/).
