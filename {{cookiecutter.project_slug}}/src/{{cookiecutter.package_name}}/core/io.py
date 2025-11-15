"""Input/output operations and template resolution.

This module handles YAML configuration loading, path manipulation, and
template string resolution with placeholder substitution.
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, Mapping, Tuple, Union

import yaml

from .utils import fuzzy_match_key

logger = logging.getLogger(__name__)


# Project root & basic YAML loading
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
    # Walk up directory tree looking for project root markers
    for parent in [p, *p.parents]:
        if (parent / "config").is_dir() or (parent / ".git").exists():
            return parent
    # Fallback to starting directory
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
        # Expand ~ and $VARS
        p = _expand(obj)
        # Relative path, resolve from base
        if not Path(obj).is_absolute() and not str(obj).startswith((".", "..")):
            p = base / obj
        return Path(p)
    return obj


# Config loading
def load_config(
    config_dir: Union[str, Path] = "config",
) -> Tuple[Mapping[str, Any], Mapping[str, Any], Mapping[str, Any]]:
    """Load configuration files.

    Notes
    -----
    - Relative paths in `paths.yaml` are resolved from the project root and
      returned as `Path` objects (or nested dict/list of `Path`).
    - `~` and `$ENV_VARS` are expanded for path-like entries.
    - `params.yaml` and `files.yaml` are returned as plain dictionaries.
    - Any missing file is logged and treated as an empty dict.

    Parameters
    ----------
    config_dir : Union[str, Path], optional
        The directory containing the project configuration.
        By default, "config".

    Returns
    -------
    Tuple[Mapping[str, Any], Mapping[str, Any], Mapping[str, Any]]
        (paths, params, files) configuration dictionaries.
    """
    root = project_root()
    cfg_dir = (root / config_dir).resolve()
    logger.debug("Loading configs from %s (project root: %s)", cfg_dir, root)

    paths_file = cfg_dir / "paths.yaml"
    params_file = cfg_dir / "params.yaml"
    files_file = cfg_dir / "files.yaml"

    raw_paths = _load_yaml(paths_file)
    params = _load_yaml(params_file)
    files = _load_yaml(files_file)

    # Convert string paths to Path objects
    paths = _coerce_paths(raw_paths, base=root)
    logger.debug(
        "Loaded configs: paths (%d top-level keys), params (%d top-level keys), files (%d top-level keys)",
        len(raw_paths),
        len(params),
        len(files),
    )

    return paths, params, files


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

    def _walk(v: Any) -> None:
        if isinstance(v, Path):
            # Use parent dir if Path points to file
            target = v.parent if v.suffix else v
            if not target.exists():
                # Create directory tree
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


# Context and template utilities
def make_context(*sources: Mapping[str, Any], **overrides: Any) -> Dict[str, Any]:
    """Merge one or more mappings into a flat context dictionary.

    Notes
    -----
    - Later sources override earlier ones.
    - Keyword arguments override everything.
    - Values are kept as-is; they are converted to strings only at formatting
      time inside `resolve_template`.

    Parameters
    ----------
    *sources : Mapping[str, Any]
        One or more mappings to merge.
    **overrides : Any
        Explicit key/value overrides.

    Returns
    -------
    Dict[str, Any]
        A merged context dictionary.
    """
    ctx: Dict[str, Any] = {}
    for src in sources:
        for k, v in src.items():
            ctx[str(k)] = v
    for k, v in overrides.items():
        ctx[str(k)] = v
    return ctx


# Generic transform functions for placeholders like {key::upper}
_DEFAULT_TRANSFORMS = {
    "upper": lambda s: s.upper(),
    "lower": lambda s: s.lower(),
    "title": lambda s: s.title(),
    "strip": lambda s: s.strip(),
}


_PLACEHOLDER_RE = re.compile(r"{([A-Za-z0-9_.]+)(?:::(\w+))?}")


def resolve_template(
    template: str,
    context: Mapping[str, Any],
    extra_transforms: Mapping[str, Any] | None = None,
    strict: bool = False,
    suppress_warnings: bool = False,
) -> str:
    """Resolve a single template string using the provided context.

    Notes
    -----
    - Placeholders use `{key}` syntax.
    - Simple inline transforms are supported via `{key::upper}`, `{key::lower}`,
      `{key::title}`, `{key::strip}`.
    - Unknown keys are left untouched in the output (unless strict=True).
    - Unknown transform names are ignored (the raw value is used).

    Parameters
    ----------
    template : str
        The template string containing placeholders.
    context : Mapping[str, Any]
        A mapping of keys to values used for substitution.
    extra_transforms : Mapping[str, Any], optional
        Mapping of transform name -> callable(str) -> str, which will be merged
        with the default transforms.
    strict : bool, optional
        If True, raise KeyError for unknown placeholders. Defaults to False.

    Raises
    ------
    KeyError
        If strict=True and a placeholder references an unknown key.

    Returns
    -------
    str
        The rendered string.
    """
    if not template:
        return ""

    transforms: Dict[str, Any] = dict(_DEFAULT_TRANSFORMS)
    if extra_transforms:
        transforms.update(extra_transforms)

    context_keys = list(context.keys())
    unresolved_placeholders: list[str] = []

    def _repl(match: re.Match) -> str:
        """Replace a single placeholder in the template string.

        Parameters
        ----------
        match : re.Match
            The match object from the regular expression.

        Returns
        -------
        str
            The replaced string.
        """
        key = match.group(1)
        tname = match.group(2)
        placeholder = match.group(0)

        if key not in context:
            if strict:
                # Suggest similar keys for typos
                similar = fuzzy_match_key(key, context_keys)
                error_msg = (
                    f"Placeholder '{placeholder}' references unknown key '{key}'. "
                    f"Available context keys: {sorted(context_keys)}"
                )
                if similar:
                    error_msg += f" Did you mean: {similar}?"
                raise KeyError(error_msg)
            unresolved_placeholders.append(placeholder)
            # Leave placeholder unchanged if not in context
            return match.group(0)

        value = str(context[key])
        if tname:
            func = transforms.get(tname)
            if callable(func):
                try:
                    value = func(value)
                except Exception as exc:
                    logger.warning(
                        "Error applying transform '%s' to key '%s': %s. "
                        "Using untransformed value.",
                        tname,
                        key,
                        exc,
                    )
            else:
                logger.warning(
                    "Unknown transform '%s' for key '%s'. Available transforms: %s. "
                    "Using untransformed value.",
                    tname,
                    key,
                    list(transforms.keys()),
                )
        return value

    logger.debug("Resolving template: %s", template)
    # Replace all {placeholder} matches
    result = _PLACEHOLDER_RE.sub(_repl, str(template))
    logger.debug("Resolved template result: %s", result)

    if unresolved_placeholders and not strict:
        # Check if any placeholders remain in output
        remaining_unresolved = _PLACEHOLDER_RE.findall(result)
        if remaining_unresolved and not suppress_warnings:
            unresolved_keys = {match[0] for match in remaining_unresolved}
            logger.warning(
                "Template contains unresolved placeholders: %s. Available context keys: %s",
                unresolved_keys,
                sorted(context_keys),
            )
        elif remaining_unresolved and suppress_warnings:
            unresolved_keys = {match[0] for match in remaining_unresolved}
            logger.debug(
                "Template contains unresolved placeholders (suppressed): %s. Available context keys: %s",
                unresolved_keys,
                sorted(context_keys),
            )
        else:
            logger.debug(
                "Some placeholders were initially unresolved but may be resolved later: %s",
                set(unresolved_placeholders),
            )

    return result


def resolve_block(
    obj: Any,
    context: Mapping[str, Any],
    extra_transforms: Mapping[str, Any] | None = None,
) -> Any:
    """Recursively resolve dict/list/str blocks of templates.

    Parameters
    ----------
    obj : Any
        A nested structure (dict/list/str) containing template strings.
    context : Mapping[str, Any]
        Context mapping used for substitution.
    extra_transforms : Mapping[str, Any], optional
        Extra transforms passed to `resolve_template`.

    Returns
    -------
    Any
        Structure with all strings rendered; non-strings returned unchanged.
    """
    if isinstance(obj, str):
        return resolve_template(obj, context, extra_transforms=extra_transforms)
    if isinstance(obj, dict):
        return {
            k: resolve_block(v, context, extra_transforms=extra_transforms)
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [
            resolve_block(v, context, extra_transforms=extra_transforms) for v in obj
        ]
    return obj


# Generic helper: dotted key lookup
def get_by_dotted(mapping: Mapping[str, Any], dotted: str) -> Any:
    """Retrieve a nested value from a mapping using a dotted key.

    Examples
    --------
    >>> d = {"a": {"b": {"c": 1}}}
    >>> get_by_dotted(d, "a.b.c")
    1

    Parameters
    ----------
    mapping : Mapping[str, Any]
        The nested mapping to query.
    dotted : str
        Dotted path, e.g. ``"file_templates.moment0.strict"``.

    Raises
    ------
    KeyError
        If any part of the dotted path is missing.

    Returns
    -------
    Any
        The retrieved value.
    """
    current: Any = mapping
    for part in dotted.split("."):
        if not isinstance(current, Mapping) or part not in current:
            raise KeyError(f"Key '{part}' not found while resolving '{dotted}'")
        current = current[part]
    return current
