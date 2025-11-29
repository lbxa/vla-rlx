# GR00T Inference Pipeline Fix - Summary

## Problem Diagnosis

### Error 1: AttributeError: 'GR00T_N1_5_Config' object has no attribute 'backbone_cfg'

**Root Cause**: Your checkpoint (`./checkpoints/so101_gr00t_test`) was created using **LeRobot's training pipeline**, which saves in `GrootConfig` format. However, `scripts/inference_service.py` expects a **native Isaac-GR00T checkpoint** in `GR00T_N1_5_Config` format.

**Checkpoint Format Comparison**:

```
YOUR CHECKPOINT (LeRobot):
config.json  → GrootConfig (type: "groot")
model.safetensors  → GrootPolicy weights
policy_preprocessor.json  → Normalization stats embedded here
policy_postprocessor.json

EXPECTED (Isaac-GR00T):
config.json  → GR00T_N1_5_Config (model_type: "gr00t_n1_5")
model.safetensors  → GR00T_N1_5 weights
experiment_cfg/metadata.json  → Normalization stats
```

### Error 2: ValueError: No metadata found for embodiment tag: new_embodiment

**Root Cause**: When trying the base model (`nvidia/GR00T-N1.5-3B`), it doesn't have metadata for your custom embodiment tag `new_embodiment`. The base model only has metadata for predefined embodiments (gr1, so100, etc.).

## Solution

I created **`scripts/lerobot_inference_service.py`** - a specialized inference server that:

✅ Loads LeRobot checkpoint format (GrootPolicy)  
✅ Wraps it to work with gr00t inference server infrastructure  
✅ Uses embedded normalization stats from preprocessor/postprocessor  
✅ Provides same ZMQ/HTTP interface as original script  
✅ No metadata files needed

## How to Use

### 1. Start the Inference Server

```bash
cd /home/lucas/c/vla-rlx/gr00t

# ZMQ Server (recommended)
/home/lucas/miniconda3/envs/gr00t/bin/python scripts/lerobot_inference_service.py \
    --checkpoint_path ./checkpoints/so101_gr00t_test \
    --server \
    --port 5555
```

### 2. Connect from Your Robot Code

```python
from gr00t.eval.robot import RobotInferenceClient

# Connect to server
client = RobotInferenceClient(host="localhost", port=5555)

# Send observations, get actions
action = client.get_action(observations)
```

### 3. (Optional) Enable TensorRT for 2-3x Faster Inference

```bash
cd /home/lucas/c/vla-rlx/gr00t

# Step 1: Export ONNX (one-time, ~5 minutes)
python deployment_scripts/export_onnx.py

# Step 2: Build engines (one-time, ~20 minutes)
bash deployment_scripts/build_engine.sh

# Step 3: Start server with TensorRT
/home/lucas/miniconda3/envs/gr00t/bin/python scripts/lerobot_inference_service.py \
    --checkpoint_path ./checkpoints/so101_gr00t_test \
    --server \
    --use-tensorrt \
    --trt-engine-path ./gr00t_engine \
    --port 5555
```

### 4. Test the Server

In a new terminal:

```bash
# Test client
/home/lucas/miniconda3/envs/gr00t/bin/python scripts/lerobot_inference_service.py \
    --checkpoint_path ./checkpoints/so101_gr00t_test \
    --client \
    --port 5555
```

## Files Created

1. **`gr00t/scripts/lerobot_inference_service.py`** - Main inference server script
2. **`gr00t/scripts/LEROBOT_INFERENCE_README.md`** - Detailed documentation
3. **`INFERENCE_FIX_SUMMARY.md`** - This file

## Key Differences

| Aspect                     | lerobot_inference_service.py | Original inference_service.py |
| -------------------------- | ---------------------------- | ----------------------------- |
| Works with your checkpoint | ✅ YES                       | ❌ NO (format mismatch)       |
| Requires data_config arg   | ❌ NO                        | ✅ YES                        |
| Requires experiment_cfg/   | ❌ NO                        | ✅ YES                        |
| Supports custom embodiment | ✅ YES                       | ⚠️ Only if metadata exists    |
| TensorRT support           | ✅ YES                       | ✅ YES                        |

## Troubleshooting

### GPU Out of Memory

```bash
# Check GPU usage
nvidia-smi

# Free up memory or use CPU
--device cpu
```

### Server Already Running

```bash
# Find and kill existing server
ps aux | grep lerobot_inference_service
kill <PID>

# Or use different port
--port 5556
```

### Import Errors

Always use the full conda environment path:

```bash
/home/lucas/miniconda3/envs/gr00t/bin/python scripts/lerobot_inference_service.py ...
```

## Why This Happened

The Isaac-GR00T repository provides two training approaches:

1. **Native Isaac-GR00T training** (`gr00t/experiment/train.py`)

   - Saves in GR00T_N1_5_Config format
   - Compatible with `scripts/inference_service.py`

2. **LeRobot integration** (`lerobot/scripts/lerobot_train.py`)
   - Saves in GrootConfig format (LeRobot standard)
   - **NOT compatible** with `scripts/inference_service.py`
   - Requires `scripts/lerobot_inference_service.py` (NEW)

You used LeRobot training, so you need the LeRobot inference script.

## Next Steps

1. ✅ **Test the server** with the client mode
2. ✅ **Integrate** with your SO-101 robot control code
3. ⏭️ **Deploy** persistently (systemd/docker)
4. ⏭️ **Benchmark** inference latency
5. ⏭️ **Consider** TensorRT conversion for production (if needed)

## Documentation

- **Detailed usage**: `gr00t/scripts/LEROBOT_INFERENCE_README.md`
- **Original Isaac-GR00T docs**: <https://github.com/NVIDIA/Isaac-GR00T/blob/main/getting_started/5_policy_deployment.md>
- **LeRobot docs**: `lerobot/README.md`

## Questions?

The script follows the same patterns as the original `inference_service.py`, so all the robot integration examples from the NVIDIA docs will work - just use `lerobot_inference_service.py` instead of `inference_service.py`.
