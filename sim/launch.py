"""Entry point for `uv run sim`, including macOS viewer setup."""

import os
import sys
import sysconfig
from pathlib import Path


def main():
    if sys.platform != "darwin":
        from .main import main as simulate

        simulate()
        return

    # Let mjpython find uv's Python shared library, preserving existing paths.
    libdir = sysconfig.get_config_var("LIBDIR")
    fallback = os.environ.get("DYLD_FALLBACK_LIBRARY_PATH")
    os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = (
        f"{libdir}:{fallback}" if fallback else libdir
    )
    mjpython = Path(sys.executable).with_name("mjpython")
    os.execv(mjpython, [str(mjpython), "-m", "sim.main", *sys.argv[1:]])
