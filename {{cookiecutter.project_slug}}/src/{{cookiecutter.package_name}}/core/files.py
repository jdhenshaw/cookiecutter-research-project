from __future__ import annotations

from typing import Any, Mapping, Optional

from .config import get_files, get_params, get_paths
from .context import build_generic_context
from .io import resolve_template


def deep_get(mapping: Mapping[str, Any], dotted_key: str) -> Any:
    """Walk a nested mapping using a dotted key.

    Examples
    --------
    >>> deep_get(files_cfg, "file_templates.mom0")
    >>> deep_get(files_cfg, "outputs.tab_completeness")

    Parameters
    ----------
    mapping : Mapping[str, Any]
        Nested dictionary (e.g. loaded from files.yaml).
    dotted_key : str
        Dotted path like "file_templates.mom0".

    Raises
    ------
    KeyError
        If any component of the path is missing.

    Returns
    -------
    Any
        The value at that path.
    """
    parts = dotted_key.split(".")
    current: Any = mapping
    for part in parts:
        if not isinstance(current, Mapping) or part not in current:
            raise KeyError(f"Key path '{dotted_key}' not found (stopped at '{part}').")
        current = current[part]
    return current


def resolve_file(
    files_cfg: Mapping[str, Any],
    key: str,
    context: Mapping[str, Any],
) -> str:
    """Resolve a file template key into a concrete path string.

    Notes
    -----
    The ``key`` can be either:

    - An absolute key rooted at the top of files.yaml, e.g.:
        * ``"outputs.tab_completeness"``
        * ``"outputs.fig_generic"``
    - Or a key relative to the ``file_templates`` block, e.g.:
        * ``"cube"`` → uses ``file_templates.cube``
        * ``"mom0"`` → uses ``file_templates.mom0``
        * ``"alpha_co"`` → uses ``file_templates.alpha_co``

    The value at that key must be a string template and is rendered using
    :func:`resolve_template`.

    Parameters
    ----------
    files_cfg : Mapping[str, Any]
        The entire files configuration (from files.yaml),
        typically via :func:`core.config.get_files`.
    key : str
        Logical key for the template (absolute or relative).
    context : Mapping[str, Any]
        Template context as produced by :func:`build_generic_context`.

    Raises
    ------
    KeyError
        If the key cannot be found.
    TypeError
        If the located value is not a string.

    Returns
    -------
    str
        The resolved filename/path.
    """
    # If the key is already rooted at the top level (e.g. "outputs.*"),
    # respect it. Otherwise, interpret as relative to "file_templates".
    first = key.split(".", 1)[0]
    if first in files_cfg:
        dotted = key
    else:
        dotted = f"file_templates.{key}"

    template = deep_get(files_cfg, dotted)

    if not isinstance(template, str):
        raise TypeError(
            f"Template at '{dotted}' is not a string (got {type(template)!r})."
        )

    return resolve_template(template, context)


def get_path(
    key: str,
    row: Optional[Mapping[str, Any]] = None,
    **extra: Any,
) -> str:
    """Resolve a file path from files.yaml.

    Parameters
    ----------
    key : str
        Logical template key, e.g.:
        - "cube"
        - "mom0"
        - "outputs.tab_completeness"
    row : Mapping[str, Any], optional
        Optional manifest row (e.g. an Astropy Row or dict) providing fields like
        'cube', 'base', 'galaxy', 'array', etc.
    **extra : Any
        Extra context values to inject or override (e.g. task="demo", suffix="test").

    Returns
    -------
    str
        The resolved filesystem path.
    """
    paths = get_paths()
    params = get_params()
    files = get_files()

    ctx = build_generic_context(paths=paths, params=params, row=row, extra=extra)

    return resolve_file(files_cfg=files, key=key, context=ctx)
