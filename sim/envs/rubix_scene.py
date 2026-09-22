"""Compose our tabletop and rigid cubes on top of the untouched SO101 assets."""

from pathlib import Path

import mujoco
import numpy as np

from sim.appearance import apply_appearance

# Table edges in metres. The top is z=0, at the robot's mounting surface.
WORKSPACE = np.array([[-0.10, 0.46], [-0.25, 0.25]])
PALETTE = np.array([
    [0.90, 0.03, 0.03, 1], [1.00, 0.35, 0.02, 1],
    [0.02, 0.30, 0.90, 1], [0.03, 0.65, 0.12, 1],
    [0.95, 0.85, 0.02, 1], [0.95, 0.95, 0.95, 1],
])


def add_cube(spec, name, edge, mass):
    """One physical box, with 54 massless, non-colliding coloured tiles."""
    half = edge / 2
    body = spec.worldbody.add_body(name=name, pos=[0.2, 0, half])
    body.add_freejoint(name=f"{name}_joint")
    body.add_geom(
        name=name, type=mujoco.mjtGeom.mjGEOM_BOX, size=[half] * 3,
        mass=mass, rgba=[0.025, 0.025, 0.025, 1],
        friction=[1, 0.005, 0.0001], condim=4,
    )
    for face in range(6):
        axis, side = face // 2, (-1 if face % 2 == 0 else 1)
        plane_axes = [i for i in range(3) if i != axis]
        for row in range(3):
            for col in range(3):
                pos = np.zeros(3)
                pos[axis] = side * (half + 0.0001)
                pos[plane_axes] = (np.array([row, col]) - 1) * edge / 3
                size = np.full(3, edge / 6 * 0.87)
                size[axis] = 0.0001
                body.add_geom(
                    name=f"{name}_tile_{face}_{row}_{col}",
                    type=mujoco.mjtGeom.mjGEOM_BOX, pos=pos, size=size,
                    rgba=PALETTE[face], mass=0, contype=0, conaffinity=0, group=2,
                )


def build_model(small_edge, large_edge):
    root = Path(__file__).resolve().parents[1]
    spec = mujoco.MjSpec.from_file(str(root / "scene.xml"))
    spec.meshdir = str(root / "assets" / "assets")
    spec.modelname = "rubix-stack-v1"
    spec.geom("floor").pos[2] = -0.75
    spec.worldbody.add_geom(
        name="table", type=mujoco.mjtGeom.mjGEOM_BOX,
        pos=[0.18, 0, -0.025], size=[0.28, 0.25, 0.025],
        rgba=[0.55, 0.45, 0.33, 1], friction=[1, 0.005, 0.0001],
    )
    add_cube(spec, "small_cube", small_edge, mass=0.06)
    add_cube(spec, "large_cube", large_edge, mass=0.09)
    # Camera target belongs to the world, so object motion cannot move the view.
    spec.worldbody.add_body(name="camera_target", pos=[0.18, 0, 0.12])
    for name, pos in [("front", [0.85, -0.8, 0.65]), ("top", [0.18, 0, 1.1])]:
        spec.worldbody.add_camera(
            name=name, pos=pos, mode=mujoco.mjtCamLight.mjCAMLIGHT_TARGETBODY,
            targetbody="camera_target", fovy=45,
        )
    model = spec.compile()
    apply_appearance(model)
    return model
