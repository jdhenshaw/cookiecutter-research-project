from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Mapping, Tuple, Union

import yaml

logger = logging.getLogger(__name__)


# --- small helpers -----------------------------------------------------------


def project_root(start: Union[str, Path] = ".") -> Path:
    """Get the project root directory.

    Notes
    -----
    Best-effort project root finder: walk up until we see `config/` or `.git/`.
    Falls back to absolute path of `start` if nothing is found.

    Parameters
    ----------
    start : Union[str, Path], optional
        The starting directory to search for the project root.
        By default, the current directory.

    Returns
    -------
    Path
        The project root directory.
    """
    p = Path(start).resolve()
    for parent in [p, *p.parents]:
        if (parent / "config").is_dir() or (parent / ".git").exists():
            return parent
    return p


def _expand(p: Union[str, Path]) -> Path:
    """Expand ~ and $VARS and return a resolved Path (not necessarily existing).

    Parameters
    ----------
    p : Union[str, Path]
        The path to expand.

    Returns
    -------
    Path
        The expanded path.
    """
    return Path(os.path.expandvars(os.path.expanduser(str(p)))).resolve()


def _load_yaml(file_path: Path) -> dict[str, Any]:
    """Load a YAML file if it exists; return {} if missing.

    Parameters
    ----------
    file_path : Path
        The path to the YAML file.

    Returns
    -------
    dict[str, Any]
        The YAML file contents.
    """
    if file_path.exists():
        with file_path.open("r") as f:
            data = yaml.safe_load(f)
            return data or {}
    logger.warning("Config file not found: %s", file_path)
    return {}


def _coerce_paths(obj: Any, base: Path) -> Any:
    """Recursively convert any string that looks like a path into a Path.

    Notes
    -----
    Resolved relative to `base`. Leaves non-strings untouched.

    Parameters
    ----------
    obj : Any
        The object to coerce.
    base : Path
        The base path to resolve relative paths against.

    Returns
    -------
    Any
        The coerced object.
    """
    if isinstance(obj, dict):
        return {k: _coerce_paths(v, base) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_coerce_paths(v, base) for v in obj]
    if isinstance(obj, str):
        p = _expand(obj)
        if not Path(obj).is_absolute() and not str(obj).startswith((".", "..")):
            p = base / obj
        return Path(p)
    return obj


def load_config(
    config_dir: Union[str, Path] = "config",
) -> Tuple[Mapping[str, Any], Mapping[str, Any]]:
    """Load `config/paths.yaml` and `config/params.yaml`.

    Notes
    -----
    - Relative paths in `paths.yaml` are resolved from the project root.
    - `~` and `$ENV_VARS` are expanded.
    - Path-like entries are returned as `Path` objects.

    Parameters
    ----------
    config_dir : Union[str, Path], optional
        The directory containing the project configuration.
        By default, "config".

    Returns
    -------
    Tuple[Mapping[str, Any], Mapping[str, Any]]
        The project configuration.
    """
    root = project_root()
    cfg_dir = (root / config_dir).resolve()

    paths_file = cfg_dir / "paths.yaml"
    params_file = cfg_dir / "params.yaml"

    raw_paths = _load_yaml(paths_file)
    params = _load_yaml(params_file)

    paths = _coerce_paths(raw_paths, base=root)

    return paths, params


def ensure_directories(paths_dict: Mapping[str, Any]) -> list[Path]:
    """Create all directories found inside a nested paths dictionary.

    Notes
    -----
    Any values that are `Path` will be treated as directories to ensure.
    For dict/list values, the function recurses.

    Parameters
    ----------
    paths_dict : Mapping[str, Any]
        The paths dictionary to ensure.

    Returns
    -------
    list[Path]
        The list of directories that were created (empty if none).
    """
    created: list[Path] = []

    def _walk(v: Any):
        if isinstance(v, Path):
            target = v.parent if v.suffix else v
            if not target.exists():
                target.mkdir(parents=True, exist_ok=True)
                created.append(target)
        elif isinstance(v, dict):
            for vv in v.values():
                _walk(vv)
        elif isinstance(v, list):
            for vv in v:
                _walk(vv)

    _walk(paths_dict)
    if created:
        logger.info("Created %d directories", len(created))
    return created
