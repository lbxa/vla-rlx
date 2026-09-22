"""Named placeholders; selecting one must never silently run another task."""

import gymnasium as gym


class UnimplementedEnv(gym.Env):
    def __init__(self, task_id, **kwargs):
        raise NotImplementedError(f"{task_id} is a stub. Start with rubix-stack-v1.")
