import modal

app = modal.App("sim-notebook")

image = (
    modal.Image.from_registry(
        "nvidia/cuda:12.8.0-devel-ubuntu24.04",
        add_python="3.12",
    )
    .entrypoint([])
    .apt_install(
        "git",
        "git-lfs",
        "build-essential",
        "ffmpeg",
        "libegl1",
    )
    .pip_install("uv", "ipykernel")
    .env({"CUDA_HOME": "/usr/local/cuda"})
    .run_commands(
        "git lfs install",
        "git clone --recurse-submodules "
        "https://github.com/NVIDIA/Isaac-GR00T.git "
        "/opt/Isaac-GR00T",
    )
    .workdir("/opt/Isaac-GR00T")
    .run_commands(
        "uv --version",
        "git rev-parse HEAD > /opt/gr00t-revision.txt",
    )
    .run_commands(
        # Install into the image's Python environment.
        # Consume upstream's lockfile without re-resolving cross-platform wheels.
        # Keep Modal and ipykernel, which are not dependencies of GR00T.
        "UV_PROJECT_ENVIRONMENT=\"$(python -c 'import sys; print(sys.prefix)')\" "
        'uv sync --frozen --inexact --python "$(command -v python)"',
    )
    .run_commands(
        # Check imports during the build; no GPU required.
        "python -c 'import gr00t; import torch; import torchcodec'",
    )
    # tqdm's notebook progress bars need widgets in the kernel environment.
    .pip_install("ipywidgets==8.1.9")
    .run_commands(
        "python -c 'from tqdm.notebook import tqdm; "
        "bar = tqdm(total=1, display=False); bar.update(); bar.close()'",
    )
)


@app.function(image=image)
def notebook_image():
    pass
