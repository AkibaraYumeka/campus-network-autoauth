import sys
from pathlib import Path


def get_runtime_dir() -> Path:
    """Get current runtime dir."""

    # binary
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).resolve().parent
    # script with pyproject.toml
    else:
        current_dir = Path(__file__).resolve().parent
        for parent in [current_dir, *current_dir.parents]:
            if (parent / "pyproject.toml").exists():
                return parent
        return Path.cwd()

RUNTIME_DIR = get_runtime_dir()
DATA_DIR = RUNTIME_DIR / "data"
CONFIG_PATH = DATA_DIR / "config.toml"
LOG_DIR = DATA_DIR / "logs"
UA_PATH = DATA_DIR / "ua_profile.json"
