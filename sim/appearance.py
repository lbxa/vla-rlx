"""Application colours layered over the unchanged SO101 asset materials."""

WHITE_MATERIALS = (
    "base_motor_holder_so101_v1_material",
    "base_so101_v2_material",
    "waveshare_mounting_plate_so101_v2_material",
    "motor_holder_so101_base_v1_material",
    "rotation_pitch_so101_v1_material",
    "upper_arm_so101_v1_material",
    "under_arm_so101_v1_material",
    "motor_holder_so101_wrist_v1_material",
    "wrist_roll_pitch_so101_v2_material",
    "wrist_roll_follower_so101_v1_material",
    "moving_jaw_so101_v1_material",
    "wrist_camera_mount_so101_v1_material",
)


def apply_appearance(model):
    # Change only the loaded model in memory, before the viewer starts.
    for name in WHITE_MATERIALS:
        model.mat(name).rgba[:] = (1, 1, 1, 1)
