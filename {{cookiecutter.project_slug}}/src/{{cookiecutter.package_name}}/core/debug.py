"""Debugging utilities for template resolution and context inspection.

This module provides debugging functions to help diagnose template resolution
issues, inspect available context keys, and trace placeholder substitution.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Mapping, Optional

from .config import get_files, get_params, get_paths
from .context import build_generic_context
from .files import deep_get
from .io import _PLACEHOLDER_RE, resolve_template

logger = logging.getLogger(__name__)


def debug_template(
    key: str,
    row: Optional[Mapping[str, Any]] = None,
    **extra: Any,
) -> str:
    """Debug template resolution step-by-step.

    Examples
    --------
    >>> debug_template("mom0", row=manifest_row)

    Parameters
    ----------
    key : str
        Template key to resolve (e.g., "mom0", "outputs.tab_completeness").
    row : Optional[Mapping[str, Any]], optional
        Manifest row providing context.
    **extra : Any
        Extra context values.

    Returns
    -------
    str
        The resolved path.
    """
    paths = get_paths()
    params = get_params()
    files = get_files()

    ctx = build_generic_context(paths=paths, params=params, row=row, extra=extra)

    first = key.split(".", 1)[0]
    if first in files:
        dotted = key
    else:
        dotted = f"file_templates.{key}"

    try:
        template = deep_get(files, dotted)
    except KeyError as e:
        logger.error(f"Template key '{key}' not found: {e}")
        raise

    if not isinstance(template, str):
        logger.error(f"Template at '{dotted}' is not a string (got {type(template)!r})")
        raise TypeError(f"Template at '{dotted}' is not a string")

    logger.info(f"Template: {template}")

    logger.debug(f"Available context keys: {sorted(ctx.keys())}")

    # Find all placeholders for step-by-step logging
    matches = list(_PLACEHOLDER_RE.finditer(template))

    for match in matches:
        placeholder = match.group(0)
        placeholder_key = match.group(1)
        transform = match.group(2)

        if placeholder_key in ctx:
            value = str(ctx[placeholder_key])
            if transform:
                logger.debug(
                    f"Resolving {placeholder}: {placeholder_key} = '{value}' -> transform '{transform}'"
                )
            else:
                logger.debug(f"Resolving {placeholder}: {placeholder_key} = '{value}'")
        else:
            logger.warning(
                f"Placeholder {placeholder} references unknown key '{placeholder_key}'"
            )

    result = resolve_template(template, ctx)
    logger.info(f"Resolved path: {result}")

    return result


def debug_context(
    row: Optional[Mapping[str, Any]] = None,
    **extra: Any,
) -> Dict[str, Any]:
    """Show all available context keys and their values.

    Examples
    --------
    >>> ctx = debug_context(row=manifest_row)
    >>> print(f"Available keys: {list(ctx.keys())}")

    Parameters
    ----------
    row : Optional[Mapping[str, Any]], optional
        Manifest row providing context.
    **extra : Any
        Extra context values.

    Returns
    -------
    Dict[str, Any]
        The full context dictionary.
    """
    paths = get_paths()
    params = get_params()

    ctx = build_generic_context(paths=paths, params=params, row=row, extra=extra)

    logger.info(f"Context has {len(ctx)} keys:")
    for key in sorted(ctx.keys()):
        value = ctx[key]
        value_str = str(value)
        if len(value_str) > 100:
            value_str = value_str[:97] + "..."
        logger.info(f"  {key} = {value_str}")

    return ctx
