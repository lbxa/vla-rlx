"""Headless checks: uv run --package sim python -m unittest discover -s sim/tests."""

import unittest
import warnings

import gymnasium as gym
import mujoco
import numpy as np
from gymnasium.utils.env_checker import check_env

from sim.envs import TASKS
from sim.envs.rubix_stack import RubixStackEnv


class RubixStackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.env = RubixStackEnv()

    @classmethod
    def tearDownClass(cls):
        cls.env.close()

    def setUp(self):
        self.env.reset(seed=7)

    def place_stack(self):
        """Synthetic state for checking the detector, not a robot control policy."""
        for name, z in [("large_cube", 0.0285), ("small_cube", 0.077)]:
            joint = self.env.data.joint(f"{name}_joint")
            joint.qpos[:] = [0.23, 0.09, z, 1, 0, 0, 0]
            joint.qvel[:] = 0
        mujoco.mj_forward(self.env.model, self.env.data)

    def test_gymnasium_contract(self):
        with warnings.catch_warnings():
            # Raw radians and unbounded physical observations are intentional.
            warnings.filterwarnings("ignore", category=UserWarning)
            check_env(self.env, skip_render_check=True)

    def test_seeded_resets_and_randomization(self):
        first, _ = self.env.reset(seed=42)
        colours = self.env.model.geom_rgba.copy()
        second, info = self.env.reset(seed=42)
        for name in first:
            np.testing.assert_array_equal(first[name], second[name])
        np.testing.assert_array_equal(colours, self.env.model.geom_rgba)
        self.assertFalse(info["is_success"])
        third, _ = self.env.reset(seed=43)
        self.assertFalse(np.array_equal(first["cubes"], third["cubes"]))
        self.assertFalse(np.array_equal(colours, self.env.model.geom_rgba))
        for seed in range(30):
            _, info = self.env.reset(seed=seed)
            self.assertFalse(info["out_of_workspace"])
            self.assertFalse(self.env._contact(*self.env.cube_geoms))

    def test_actions_and_observations(self):
        obs, _ = self.env.reset(seed=1)
        saved = obs["robot"].copy()
        for _ in range(50):
            _, reward, terminated, truncated, _ = self.env.step([0, 0, 0, 0, 0, 1])
        self.assertAlmostEqual(self.env.data.time, 1.0)
        self.assertEqual(reward, 0)
        self.assertFalse(terminated or truncated)
        self.assertTrue(np.isfinite(self.env.data.qpos).all())
        np.testing.assert_array_equal(obs["robot"], saved)
        np.testing.assert_array_equal(self.env.data.warning.number, 0)
        for bad in [np.zeros(20), [0, 0, 0, 0, 0, np.nan]]:
            with self.assertRaises(ValueError):
                self.env.step(bad)

    def test_stable_released_stack_requires_lift_history(self):
        self.place_stack()
        # Resting on a stack alone is not proof that the robot grasped and lifted.
        for _ in range(40):
            _, reward, done, _, info = self.env.step([0, 0, 0, 0, 0, 1])
        self.assertTrue(info["is_stacked"])
        self.assertFalse(done)
        self.assertEqual(reward, 0)
        # Isolate the hold timer after the earlier grasp/lift milestone.
        self.env.has_grasped = self.env.has_lifted = True
        for _ in range(24):
            _, reward, done, _, info = self.env.step([0, 0, 0, 0, 0, 1])
            self.assertFalse(done)
        _, reward, done, _, info = self.env.step([0, 0, 0, 0, 0, 1])
        self.assertTrue(done and info["is_success"])
        self.assertEqual(reward, 1)
        self.assertAlmostEqual(info["stable_seconds"], 0.5)

    def test_hover_motion_and_overhang_are_not_stacks(self):
        self.place_stack()
        self.env.data.joint("small_cube_joint").qpos[2] += 0.01
        mujoco.mj_forward(self.env.model, self.env.data)
        self.assertFalse(self.env._is_stacked())
        self.place_stack()
        self.env.data.joint("small_cube_joint").qvel[0] = 0.1
        self.assertFalse(self.env._is_stacked())
        self.place_stack()
        self.env.data.joint("small_cube_joint").qpos[0] += 0.015
        mujoco.mj_forward(self.env.model, self.env.data)
        self.assertFalse(self.env._is_stacked())

    def test_workspace_exit_terminates(self):
        self.env.data.joint("small_cube_joint").qpos[0] = 0.6
        _, reward, terminated, truncated, info = self.env.step([0, 0, 0, 0, 0, 1])
        self.assertTrue(terminated and info["out_of_workspace"])
        self.assertFalse(truncated or info["is_success"])
        self.assertEqual(reward, 0)

    def test_registry_and_stubs(self):
        self.assertEqual(len(TASKS), 7)
        for task in TASKS:
            if task != "rubix-stack-v1":
                with self.assertRaisesRegex(NotImplementedError, f"{task} is a stub"):
                    gym.make(task)
        with gym.make("rubix-stack-v1", max_episode_steps=1) as env:
            env.reset(seed=3)
            _, _, terminated, truncated, _ = env.step([0, 0, 0, 0, 0, 1])
            self.assertTrue(truncated)
            self.assertFalse(terminated)


if __name__ == "__main__":
    unittest.main()
