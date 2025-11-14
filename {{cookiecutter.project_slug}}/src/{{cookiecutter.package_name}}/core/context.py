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
    ctx.update(flatten_dict(paths))

    # 2. Merge manifest row (cube, base, galaxy, array, etc.)
    if row is not None:
        try:
            items = row.items()
        except AttributeError:
            items = dict(row).items()
        for k, v in items:
            ctx[str(k)] = v

    # 3. Apply params.placeholders
    placeholder_map = params.get("placeholders", {}) or {}
    for name, expr in placeholder_map.items():
        ctx[name] = resolve_template(str(expr), ctx)

    # 4. Apply overrides last
    if extra:
        for k, v in extra.items():
            ctx[str(k)] = v

    return ctx
