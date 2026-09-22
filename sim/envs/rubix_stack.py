"""A small native MuJoCo environment with Gymnasium's reset/step interface."""

import gymnasium as gym
import mujoco
import numpy as np
from gymnasium import spaces

from .rubix_scene import PALETTE, WORKSPACE, build_model

JOINTS = ("shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper")
CUBES = ("small_cube", "large_cube")


class RubixStackEnv(gym.Env):
    metadata = {"render_modes": ["rgb_array"], "render_fps": 50}

    def __init__(self, render_mode=None, small_cube_size=0.040, large_cube_size=0.057,
                 camera="front", width=640, height=480):
        if not 0 < small_cube_size < large_cube_size <= 0.080:
            raise ValueError("Require 0 < small_cube_size < large_cube_size <= 0.080 metres.")
        if render_mode not in (None, "rgb_array") or camera not in ("front", "top"):
            raise ValueError("Use render_mode=None or 'rgb_array', and camera='front' or 'top'.")
        self.render_mode, self.camera = render_mode, camera
        self.width, self.height = width, height
        self.half_sizes = np.array([small_cube_size, large_cube_size]) / 2
        self.model = build_model(small_cube_size, large_cube_size)
        self.data = mujoco.MjData(self.model)
        self.frame_skip = 10
        self.model.opt.timestep = 0.002
        self.dt = self.frame_skip * self.model.opt.timestep
        self.action_space = spaces.Box(
            self.model.actuator_ctrlrange[:, 0].copy(),
            self.model.actuator_ctrlrange[:, 1].copy(), dtype=np.float64,
        )
        self.observation_space = spaces.Dict({
            "robot": spaces.Box(-np.inf, np.inf, (12,), np.float64),
            "cubes": spaces.Box(-np.inf, np.inf, (26,), np.float64),
            "task": spaces.Box(0, 1, (3,), np.float64),
        })
        self.cube_geoms = [self.model.geom(name).id for name in CUBES]
        self.table_geom = self.model.geom("table").id
        self.finger_bodies = {self.model.body(name).id for name in ("gripper", "moving_jaw_so101_v1")}
        # All descendants of the arm base, including its camera and moving jaw.
        self.robot_bodies = {self.model.body("base").id}
        for body in range(1, self.model.nbody):
            if self.model.body_parentid[body] in self.robot_bodies:
                self.robot_bodies.add(body)
        self.renderer = None
        self.has_grasped = self.has_lifted = False
        self.stable_steps = 0

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        mujoco.mj_resetData(self.model, self.data)
        self.has_grasped = self.has_lifted = False
        self.stable_steps = 0
        self.data.joint("gripper").qpos[0] = 1.0
        self.data.ctrl[:] = [self.data.joint(name).qpos[0] for name in JOINTS]
        # Circumscribed circles keep the boxes separate for every sampled yaw.
        clearance = np.sqrt(2) * self.half_sizes.sum() + 0.015
        for _ in range(1000):
            xy = self.np_random.uniform([0.14, -0.13], [0.28, 0.13], size=(2, 2))
            if np.linalg.norm(xy[0] - xy[1]) > clearance:
                break
        else:
            raise RuntimeError("Could not sample separated cubes.")
        for i, name in enumerate(CUBES):
            yaw = self.np_random.uniform(-np.pi, np.pi)
            self.data.joint(f"{name}_joint").qpos[:] = [
                *xy[i], self.half_sizes[i], np.cos(yaw / 2), 0, 0, np.sin(yaw / 2),
            ]
            colours = self.np_random.permutation(PALETTE)
            for face in range(6):
                for row in range(3):
                    for col in range(3):
                        self.model.geom(f"{name}_tile_{face}_{row}_{col}").rgba[:] = colours[face]
        mujoco.mj_forward(self.model, self.data)
        return self._observation(), self._info()

    def step(self, action):
        action = np.asarray(action, dtype=np.float64)
        if action.shape != (6,) or not np.isfinite(action).all():
            raise ValueError("Action must contain six finite joint targets in radians.")
        self.data.ctrl[:] = np.clip(action, self.action_space.low, self.action_space.high)
        # Check grasp and lift at physics rate, so brief contacts aren't missed.
        for _ in range(self.frame_skip):
            mujoco.mj_step(self.model, self.data)
            mujoco.mj_forward(self.model, self.data)
            touching = self._touching_bodies(self.cube_geoms[0])
            self.has_grasped |= self.finger_bodies <= touching
            small = self.data.body("small_cube")
            bottom = small.xpos[2] - np.abs(small.xmat.reshape(3, 3)[2]).sum() * self.half_sizes[0]
            self.has_lifted |= self.has_grasped and bottom > 0.015
        stacked = self._is_stacked()
        self.stable_steps = self.stable_steps + 1 if stacked and self.has_lifted else 0
        info = self._info()
        terminated = info["is_success"] or info["out_of_workspace"]
        return self._observation(), float(info["is_success"]), terminated, False, info

    def _touching_bodies(self, geom):
        bodies = set()
        for contact in self.data.contact:
            if contact.dist <= 0 and geom in contact.geom:
                other = contact.geom[1] if contact.geom[0] == geom else contact.geom[0]
                bodies.add(int(self.model.geom_bodyid[other]))
        return bodies

    def _contact(self, first, second):
        return any(c.dist <= 0 and set(c.geom) == {first, second} for c in self.data.contact)

    def _is_stacked(self):
        small, large = (self.data.body(name) for name in CUBES)
        rotation = large.xmat.reshape(3, 3)
        relative = rotation.T @ (small.xpos - large.xpos)
        extent = np.abs(rotation.T @ small.xmat.reshape(3, 3)) @ np.full(3, self.half_sizes[0])
        # A cube may land on any face; find the large cube's upward local axis.
        up = int(np.argmax(np.abs(rotation[2])))
        planar = [axis for axis in range(3) if axis != up]
        upright = abs(rotation[2, up]) > np.cos(np.deg2rad(10))
        contained = np.all(np.abs(relative[planar]) + extent[planar] <= self.half_sizes[1] + 0.001)
        above = abs(relative[up] * np.sign(rotation[2, up]) - self.half_sizes[1] - extent[up]) < 0.003
        still = all(
            np.linalg.norm(self.data.joint(f"{name}_joint").qvel[:3]) < 0.01
            and np.linalg.norm(self.data.joint(f"{name}_joint").qvel[3:]) < 0.15
            for name in CUBES
        )
        released = all(not self._touching_bodies(geom) & self.robot_bodies for geom in self.cube_geoms)
        return bool(upright and contained and above and still and released
                    and self._contact(*self.cube_geoms)
                    and self._contact(self.cube_geoms[1], self.table_geom))

    def _out_of_workspace(self):
        for name, half in zip(CUBES, self.half_sizes):
            body = self.data.body(name)
            extent = np.abs(body.xmat.reshape(3, 3)) @ np.full(3, half)
            if (np.any(body.xpos[:2] - extent[:2] < WORKSPACE[:, 0])
                    or np.any(body.xpos[:2] + extent[:2] > WORKSPACE[:, 1])
                    or body.xpos[2] < -0.02):
                return True
        return False

    def _info(self):
        outside = self._out_of_workspace()
        return {"is_success": self.stable_steps >= 25 and not outside,
                "has_grasped": bool(self.has_grasped), "has_lifted": bool(self.has_lifted),
                "is_stacked": self._is_stacked(), "out_of_workspace": outside,
                "stable_seconds": self.stable_steps * self.dt}

    def _observation(self):
        return {
            "robot": np.concatenate([np.r_[self.data.joint(name).qpos, self.data.joint(name).qvel] for name in JOINTS]),
            "cubes": np.concatenate([np.r_[self.data.joint(f"{name}_joint").qpos,
                                           self.data.joint(f"{name}_joint").qvel] for name in CUBES]),
            "task": np.array([self.has_grasped, self.has_lifted, min(self.stable_steps / 25, 1)], dtype=np.float64),
        }

    def render(self):
        if self.render_mode != "rgb_array":
            return None
        if self.renderer is None:
            self.renderer = mujoco.Renderer(self.model, height=self.height, width=self.width)
        self.renderer.update_scene(self.data, camera=self.camera)
        return self.renderer.render()

    def close(self):
        if self.renderer is not None:
            self.renderer.close()
            self.renderer = None
