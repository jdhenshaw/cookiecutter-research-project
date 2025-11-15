"""Template context building and management.

This module provides functions for building flattened context dictionaries
from configuration files, manifest rows, and extra parameters for use
in template resolution.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

from .io import resolve_template


def flatten_dict(
    data: Mapping[str, Any],
    parent_key: str = "",
    sep: str = ".",
) -> Dict[str, Any]:
    """Flatten a nested dictionary into a single-level dict.

    Parameters
    ----------
    data : Mapping[str, Any]
        The nested dictionary to flatten.
    parent_key : str, optional
        The key to prepend to each flattened key.
    sep : str, optional
        The separator to use between keys.

    Returns
    -------
    Dict[str, Any]
        The flattened dictionary.
    """
    flat: Dict[str, Any] = {}
    for k, v in data.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, Mapping):
            flat.update(flatten_dict(v, new_key, sep=sep))
        else:
            flat[new_key] = v
    return flat


def build_generic_context(
    paths: Mapping[str, Any],
    params: Mapping[str, Any],
    row: Optional[Mapping[str, Any]] = None,
    extra: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Build the flattened template context for file resolution.

    Parameters
    ----------
    paths : Mapping[str, Any]
        The paths configuration.
    params : Mapping[str, Any]
        The parameters configuration.
    row : Optional[Mapping[str, Any]], optional
        The manifest row.
    extra : Optional[Mapping[str, Any]], optional
        Extra context values to inject or override (e.g. "task", "suffix").

    Returns
    -------
    Dict[str, Any]
        The flattened template context.
    """
    ctx: Dict[str, Any] = {}

    # 1. Flatten paths.yaml
    # Converts nested paths to dotted keys (e.g., data.core)
    ctx.update(flatten_dict(paths))

    # 2. Merge manifest row (cube, base, galaxy, array, etc.)
    if row is not None:
        # Try dict-like interface first
        try:
            items = row.items()
        except (AttributeError, TypeError):
            # Convert Astropy Row to dict
            try:
                row_dict = dict(row)
                items = row_dict.items()
            except (TypeError, ValueError):
                # Fallback to attributes
                items = [
                    (k, getattr(row, k)) for k in dir(row) if not k.startswith("_")
                ]

        for k, v in items:
            if not callable(v):
                # Add row data to context (overrides flattened paths if same key)
                ctx[str(k)] = v

    # 3. Apply params.placeholders
    placeholder_map = params.get("placeholders", {}) or {}
    for name, expr in placeholder_map.items():
        # Resolve placeholders using current context
        ctx[name] = resolve_template(str(expr), ctx, suppress_warnings=True)

    # 4. Apply overrides last
    if extra:
        for k, v in extra.items():
            # Extra context has highest precedence
            ctx[str(k)] = v

    return ctx
