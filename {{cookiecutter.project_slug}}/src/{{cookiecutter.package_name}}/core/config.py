from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping, Tuple, Union

from .io import (
    ensure_directories as _core_ensure_directories,
)
from .io import (
    load_config as _core_load_config,
)


@lru_cache(maxsize=1)
def get_configs(
    config_dir: Union[str, Path] = "config",
) -> Tuple[Mapping[str, Any], Mapping[str, Any], Mapping[str, Any]]:
    """Load and cache the PHANGS-ScousePy configuration.

    Notes
    -----
    This is a thin wrapper around ``core.io.load_config`` that adds
    caching. The first call reads:

    - ``paths.yaml``  → directory layout (as Path objects)
    - ``params.yaml`` → project parameters
    - ``files.yaml``  → file template definitions

    Subsequent calls return the cached result.

    Parameters
    ----------
    config_dir : Union[str, Path], optional
        Directory containing the YAML config files. Defaults to ``"config"``.

    Returns
    -------
    Tuple[Mapping[str, Any], Mapping[str, Any], Mapping[str, Any]]
        ``(paths, params, files)`` dictionaries.
    """
    return _core_load_config(config_dir=config_dir)


def get_paths(config_dir: Union[str, Path] = "config") -> Mapping[str, Any]:
    """Return the ``paths`` configuration dictionary.

    Parameters
    ----------
    config_dir : Union[str, Path], optional
        Directory containing the YAML config files. Defaults to ``"config"``.

    Returns
    -------
    Mapping[str, Any]
        The ``paths`` configuration dictionary.
    """
    paths, _, _ = get_configs(config_dir=config_dir)
    return paths


def get_params(config_dir: Union[str, Path] = "config") -> Mapping[str, Any]:
    """Return the ``params`` configuration dictionary.

    Parameters
    ----------
    config_dir : Union[str, Path], optional
        Directory containing the YAML config files. Defaults to ``"config"``.

    Returns
    -------
    Mapping[str, Any]
        The ``params`` configuration dictionary.
    """
    _, params, _ = get_configs(config_dir=config_dir)
    return params


def get_files(config_dir: Union[str, Path] = "config") -> Mapping[str, Any]:
    """Return the ``files`` configuration dictionary.

    Parameters
    ----------
    config_dir : Union[str, Path], optional
        Directory containing the YAML config files. Defaults to ``"config"``.

    Returns
    -------
    Mapping[str, Any]
        The ``files`` configuration dictionary.
    """
    _, _, files = get_configs(config_dir=config_dir)
    return files


def ensure_project_directories(config_dir: Union[str, Path] = "config") -> None:
    """Ensure that all directories defined in ``paths.yaml`` exist.

    Notes
    -----
    This is a convenience wrapper around ``core.io.ensure_directories``.
    It is safe to call multiple times.

    Parameters
    ----------
    config_dir : Union[str, Path], optional
        Directory containing the YAML config files. Defaults to ``"config"``.
    """
    paths = get_paths(config_dir=config_dir)
    _core_ensure_directories(paths)
