"""File path resolution and template management.

This module provides functions for resolving file paths from configuration
templates, including support for nested key lookups and fuzzy matching.
"""

from __future__ import annotations

import logging
from typing import Any, Mapping, Optional

from .config import get_files, get_params, get_paths
from .context import build_generic_context
from .io import resolve_template
from .utils import fuzzy_match_key

logger = logging.getLogger(__name__)


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
    for i, part in enumerate(parts):
        if not isinstance(current, Mapping) or part not in current:
            # Build context for error message
            available_keys = (
                list(current.keys()) if isinstance(current, Mapping) else []
            )
            similar = fuzzy_match_key(part, available_keys) if available_keys else []

            path_so_far = ".".join(parts[:i])
            error_msg = f"Key path '{dotted_key}' not found (stopped at '{part}')."
            if path_so_far:
                error_msg += f" Path so far: '{path_so_far}'"
            if available_keys:
                error_msg += f" Available keys at this level: {sorted(available_keys)}"
            if similar:
                error_msg += f" Did you mean: {similar}?"
            raise KeyError(error_msg)
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
    first = key.split(".", 1)[0]
    # Determine if key is absolute or relative to file_templates
    if first in files_cfg:
        # Absolute key
        dotted = key
    else:
        # Relative key
        dotted = f"file_templates.{key}"

    try:
        # Navigate nested dict structure
        template = deep_get(files_cfg, dotted)
    except KeyError as e:
        top_level_keys = list(files_cfg.keys())
        if "file_templates" in files_cfg:
            file_template_keys = (
                list(files_cfg["file_templates"].keys())
                if isinstance(files_cfg["file_templates"], dict)
                else []
            )
        else:
            file_template_keys = []

        error_msg = f"Template key '{key}' not found. "
        if first in top_level_keys:
            error_msg += f"Available keys in '{first}': {sorted(file_template_keys) if first == 'file_templates' else 'N/A'}"
        else:
            error_msg += f"Top-level keys: {sorted(top_level_keys)}"
            if file_template_keys:
                similar = fuzzy_match_key(key, file_template_keys)
                if similar:
                    error_msg += f" Did you mean: {similar}?"
        raise KeyError(error_msg) from e

    if not isinstance(template, str):
        raise TypeError(
            f"Template at '{dotted}' is not a string (got {type(template)!r})."
        )

    try:
        # Substitute placeholders with context values
        return resolve_template(template, context)
    except Exception as e:
        raise RuntimeError(
            f"Failed to resolve template '{dotted}': {e}. "
            f"Template: {template!r}. "
            f"Available context keys: {sorted(context.keys())}"
        ) from e


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

    Raises
    ------
    KeyError
        If the template key is not found.
    RuntimeError
        If template resolution fails.

    Returns
    -------
    str
        The resolved filesystem path.
    """
    try:
        logger.debug("Resolving path for key '%s'", key)
        paths = get_paths()
        params = get_params()
        files = get_files()

        # Merge all context sources (paths, params, row, extra)
        ctx = build_generic_context(paths=paths, params=params, row=row, extra=extra)
        logger.debug(
            "Context built with %d keys: %s", len(ctx), sorted(ctx.keys())[:10]
        )

        # Resolve template to final path
        result = resolve_file(files_cfg=files, key=key, context=ctx)
        logger.debug("Resolved path: %s", result)
        return result
    except (KeyError, RuntimeError):
        raise
    except Exception as e:
        raise RuntimeError(
            f"Failed to resolve path for key '{key}': {e}. "
            f"Row: {dict(row) if row else 'None'}. "
            f"Extra context: {extra if extra else 'None'}"
        ) from e
