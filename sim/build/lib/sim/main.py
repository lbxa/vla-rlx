"""Load the SO101 arm and run MuJoCo's passive viewer."""

import time
from pathlib import Path

import mujoco
import mujoco.viewer

from sim.appearance import apply_appearance


def main():
    scene = Path(__file__).with_name("scene.xml")
    model = mujoco.MjModel.from_xml_path(str(scene))
    apply_appearance(model)
    data = mujoco.MjData(model)

    # These six position actuators use joint angles in radians as targets.
    data.ctrl[:] = data.qpos
    mujoco.mj_forward(model, data)

    with mujoco.viewer.launch_passive(model, data) as viewer:
        while viewer.is_running():
            step_start = time.monotonic()

            # Set targets here, or use the viewer's Control sliders.
            # data.actuator("shoulder_pan").ctrl[0] = 0.5
            mujoco.mj_step(model, data)
            viewer.sync()

            # Pace the simulation approximately in real time.
            remaining = model.opt.timestep - (time.monotonic() - step_start)
            if remaining > 0:
                time.sleep(remaining)


if __name__ == "__main__":
    main()
