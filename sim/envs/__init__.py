"""The seven task IDs from https://vla.lbxa.net/. Import to register them."""

from gymnasium.envs.registration import register

TASKS = {
    "rubix-stack-v1": "Stack the smaller Rubik's cube on the larger cube.",
    "bus-table-easy-v1": "Put a few pens and a glue stick in the pen holder.",
    "bus-table-medium-v1": "Clear more objects, including a new pen geometry.",
    "bus-table-hard-v1": "Clear a cluttered table of varied pens and a glue stick.",
    "close-bottle-lid-v1": "Seat the metal lid on its bottle, without screwing it on.",
    "erase-whiteboard-v1": "Use the cloth to erase a red stroke on the whiteboard.",
    "close-french-press": "Position the lid and press the plunger down.",
}

for task_id in TASKS:
    implemented = task_id == "rubix-stack-v1"
    register(
        id=task_id,
        entry_point=(
            "sim.envs.rubix_stack:RubixStackEnv"
            if implemented else "sim.envs.stubs:UnimplementedEnv"
        ),
        kwargs={} if implemented else {"task_id": task_id},
        max_episode_steps=1500,  # 30 seconds at 50 Hz.
    )
