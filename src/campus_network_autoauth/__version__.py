from importlib.metadata import PackageNotFoundError, metadata, version
from pathlib import Path

PACKAGE_NAME = "campus-network-autoauth"
__version__ = "0.0.0+dev"
__description__ = "Description not available."


def _load_from_metadata():
    """Load version and description from package metadata."""

    try:
        return version(PACKAGE_NAME), metadata(PACKAGE_NAME)["Summary"]
    except PackageNotFoundError:
        return None


def _load_from_pyproject():
    """Load version and description from pyproject.toml."""

    try:
        import tomlkit

        pyproject_path = Path(__file__).resolve().parent.parent / "pyproject.toml"
        if not pyproject_path.exists():
            return None
        data = tomlkit.parse(pyproject_path.read_text(encoding="utf-8"))
        project = data.get("project", {})
        return project.get("version"), project.get("description")
    except Exception:
        return None


_result = _load_from_metadata() or _load_from_pyproject()
if _result:
    __version__, __description__ = _result
