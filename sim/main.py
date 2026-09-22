"""Select a task and explore it in MuJoCo's passive viewer."""

import argparse
import time
from pathlib import Path
from threading import Event

import gymnasium as gym
import mujoco
import mujoco.viewer

from sim.appearance import apply_appearance
from sim.envs import TASKS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", choices=TASKS, default="rubix-stack-v1")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--list-envs", action="store_true")
    parser.add_argument("--robot-only", action="store_true", help="Open the original bare-arm scene.")
    args = parser.parse_args()
    if args.list_envs:
        for task, description in TASKS.items():
            status = "ready" if task == "rubix-stack-v1" else "stub"
            print(f"{task:24} [{status}] {description}")
        return

    env = None
    if args.robot_only:
        model = mujoco.MjModel.from_xml_path(str(Path(__file__).with_name("scene.xml")))
        apply_appearance(model)
        data = mujoco.MjData(model)
        data.ctrl[:] = data.qpos
        mujoco.mj_forward(model, data)
        dt = model.opt.timestep
    else:
        try:
            # Interactive exploration has no time limit; gym.make normally has 30 s.
            env = gym.make(args.env, max_episode_steps=-1)
        except NotImplementedError as error:
            parser.error(str(error))
        env.reset(seed=args.seed)
        model, data, dt = env.unwrapped.model, env.unwrapped.data, env.unwrapped.dt

    reset_requested = Event()
    done = False
    print("Use the Control sliders to move the arm. Press R to reset the task.")
    try:
        with mujoco.viewer.launch_passive(
            model, data, key_callback=lambda key: reset_requested.set() if key == ord("R") else None,
        ) as viewer:
            if env is not None:
                with viewer.lock():
                    viewer.cam.lookat[:] = [0.18, 0, 0.10]
                    viewer.cam.distance = 0.85
                    viewer.cam.azimuth = 135
                    viewer.cam.elevation = -35
            while viewer.is_running():
                step_start = time.monotonic()
                if reset_requested.is_set():
                    if env is not None:
                        env.reset()
                    else:
                        mujoco.mj_resetData(model, data)
                        mujoco.mj_forward(model, data)
                    done = False
                    reset_requested.clear()
                if not done:
                    if env is None:
                        mujoco.mj_step(model, data)
                    else:
                        # Six absolute joint targets, read from the Control sliders.
                        _, _, done, _, info = env.step(data.ctrl.copy())
                        if done:
                            print("Stack complete! Press R." if info["is_success"] else "Cube left the workspace. Press R.")
                viewer.sync()
                remaining = dt - (time.monotonic() - step_start)
                if remaining > 0:
                    time.sleep(remaining)
    finally:
        if env is not None:
            env.close()


if __name__ == "__main__":
    main()
