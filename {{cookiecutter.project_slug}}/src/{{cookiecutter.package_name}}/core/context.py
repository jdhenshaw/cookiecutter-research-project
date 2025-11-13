from __future__ import annotations

from typing import Any, Dict, Mapping, Optional


def flatten_dict(
    data: Mapping[str, Any],
    parent_key: str = "",
    sep: str = ".",
) -> Dict[str, Any]:
    """Flatten a nested dictionary into a single-level dict.

    Example
    -------
    {"external": {"project": {"cubes": "/x"}}}
    becomes:
    {"external.project.cubes": "/x"}

    Parameters
    ----------
    data : Mapping[str, Any]
        Nested dictionary.
    parent_key : str, optional
        Prefix accumulated through recursion.
    sep : str, optional
        Separator used to join nested keys.

    Returns
    -------
    Dict[str, Any]
        Flattened mapping.
    """
    flat: Dict[str, Any] = {}

    for k, v in data.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, Mapping):
            flat.update(flatten_dict(v, new_key, sep=sep))
        else:
            flat[new_key] = v

    return flat


def apply_template(template: str, ctx: Mapping[str, Any]) -> str:
    """Render a template string using context values.

    Notes
    -----
    - Supports:
        {var}
        {var::upper}
    - Unknown placeholders remain unchanged.

    Parameters
    ----------
    template : str
        Template string.
    ctx : Mapping[str, Any]
        Context mapping.

    Returns
    -------
    str
        Rendered string.
    """
    out = str(template)

    # First handle {key::upper}
    for key, val in ctx.items():
        out = out.replace(f"{{{key}::upper}}", str(val).upper())

    # Then handle {key}
    for key, val in ctx.items():
        out = out.replace(f"{{{key}}}", str(val))

    return out


def build_generic_context(
    paths: Mapping[str, Any],
    params: Mapping[str, Any],
    row: Optional[Mapping[str, Any]] = None,
    extra: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Build a flat, generic context for template resolution.

    Parameters
    ----------
    paths : Mapping[str, Any]
        The dictionary loaded from paths.yaml.
    params : Mapping[str, Any]
        The dictionary loaded from params.yaml.
    row : Mapping[str, Any], optional
        Manifest row (e.g. describing a target), exposed as a dict-like object.
        Can be omitted.
    extra : Mapping[str, Any], optional
        Additional overrides.

    Returns
    -------
    Dict[str, Any]
        A flattened, fully merged context dictionary.
    """

    ctx: Dict[str, Any] = {}

    # 1. Flatten paths.yaml into context
    flat_paths = flatten_dict(paths)
    for k, v in flat_paths.items():
        ctx[k] = v

    # 2. Manifest row adds dynamic keys (e.g. cube, file, base)
    if row:
        for k, v in row.items():
            ctx[str(k)] = v

    # 3. Apply placeholders from params.yaml
    placeholder_map = params.get("placeholders", {}) or {}
    for name, expr in placeholder_map.items():
        ctx[name] = apply_template(str(expr), ctx)

    # 4. Add any explicit overrides
    if extra:
        for k, v in extra.items():
            ctx[str(k)] = v

    return ctx
