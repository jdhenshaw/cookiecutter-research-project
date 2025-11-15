from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Mapping, Set, Tuple

from .io import _PLACEHOLDER_RE

logger = logging.getLogger(__name__)


def validate_configs(
    config_dir: str | Path = "config",
    check_paths: bool = True,
    check_templates: bool = True,
) -> Tuple[bool, List[str]]:
    """Validate configuration files.

    Parameters
    ----------
    config_dir : str | Path, optional
        Directory containing config files. Defaults to "config".
    check_paths : bool, optional
        Whether to check if paths exist. Defaults to True.
    check_templates : bool, optional
        Whether to validate template resolution. Defaults to True.

    Returns
    -------
    Tuple[bool, List[str]]
        (is_valid, list_of_errors) tuple.
    """
    from .config import get_configs

    errors: List[str] = []

    try:
        paths, params, files = get_configs(config_dir=config_dir)
    except Exception as e:
        errors.append(f"Failed to load configs: {e}")
        return False, errors

    if not paths:
        errors.append("paths.yaml is empty or missing")
    if not params:
        errors.append("params.yaml is empty or missing")
    if not files:
        errors.append("files.yaml is empty or missing")

    if errors:
        # Early return if basic structure is missing
        return False, errors

    if check_paths:
        # Verify paths exist or are creatable
        path_errors = validate_paths(paths)
        errors.extend(path_errors)

    if check_templates:
        # Check template resolvability
        template_errors = validate_templates(files, paths, params)
        errors.extend(template_errors)

    # Detect circular dependencies
    placeholder_errors = _check_placeholder_circular_deps(params)
    errors.extend(placeholder_errors)

    return len(errors) == 0, errors


def validate_paths(paths: Mapping[str, Any], check_external: bool = True) -> List[str]:
    """Validate that paths exist or can be created.

    Parameters
    ----------
    paths : Mapping[str, Any]
        Paths configuration dictionary.
    check_external : bool, optional
        Whether to check external paths (warns if missing, doesn't error).
        Defaults to True.

    Returns
    -------
    List[str]
        List of error messages (empty if valid).
    """
    errors: List[str] = []
    warnings: List[str] = []

    def _check_path(value: Any, key_path: str) -> None:
        if isinstance(value, Path):
            # Heuristic to identify external paths
            is_external = "external" in key_path.lower()
            if is_external and check_external:
                if not value.exists():
                    # Warn only, don't error
                    warnings.append(
                        f"External path does not exist: {key_path} = {value}"
                    )
            elif not is_external:
                # Use parent dir if Path is a file
                parent = value.parent if value.suffix else value
                # Check if directory tree is creatable
                if not parent.exists() and not parent.parent.exists():
                    errors.append(f"Path parent does not exist: {key_path} = {value}")
        elif isinstance(value, dict):
            for k, v in value.items():
                _check_path(v, f"{key_path}.{k}" if key_path else k)
        elif isinstance(value, list):
            for i, v in enumerate(value):
                _check_path(v, f"{key_path}[{i}]")

    _check_path(paths, "")

    for warning in warnings:
        logger.warning(warning)

    return errors


def validate_templates(
    files: Mapping[str, Any],
    paths: Mapping[str, Any],
    params: Mapping[str, Any],
) -> List[str]:
    """Validate that all templates can be resolved.

    Parameters
    ----------
    files : Mapping[str, Any]
        Files configuration dictionary.
    paths : Mapping[str, Any]
        Paths configuration dictionary.
    params : Mapping[str, Any]
        Parameters configuration dictionary.

    Returns
    -------
    List[str]
        List of error messages (empty if valid).
    """
    errors: List[str] = []

    templates: Dict[str, str] = {}

    if "file_templates" in files:
        for key, value in files["file_templates"].items():
            if isinstance(value, str):
                templates[f"file_templates.{key}"] = value

    if "outputs" in files:
        for key, value in files["outputs"].items():
            if isinstance(value, str):
                templates[f"outputs.{key}"] = value

    all_placeholders: Set[str] = set()
    for template in templates.values():
        # Extract all {placeholder} keys from templates
        matches = _PLACEHOLDER_RE.findall(template)
        for match in matches:
            placeholder_key = match[0]
            all_placeholders.add(placeholder_key)

    from .context import flatten_dict

    # Get flattened path keys (e.g., data.core, external.phangs.cubes)
    flat_paths = flatten_dict(paths)
    available_keys = set(flat_paths.keys())

    # Add top-level param keys
    available_keys.update(params.keys())

    if "placeholders" in params:
        # Add placeholder names themselves
        available_keys.update(params["placeholders"].keys())

    for placeholder in all_placeholders:
        # Dotted keys must exist in paths structure
        if "." in placeholder:
            if placeholder not in available_keys:
                parts = placeholder.split(".")
                current = paths
                valid = True
                # Walk nested structure to verify path exists
                for part in parts:
                    if isinstance(current, dict) and part in current:
                        current = current[part]
                    else:
                        valid = False
                        break

                if not valid:
                    errors.append(
                        f"Template placeholder '{placeholder}' references unknown context key"
                    )
        else:
            # Simple keys: check static config or assume dynamic (from row/extra context)
            if placeholder in paths or placeholder in params:
                pass  # Valid static key
            elif placeholder not in available_keys:
                logger.debug(
                    "Template placeholder '%s' not found in static config - assuming dynamic",
                    placeholder,
                )

    return errors


def _check_placeholder_circular_deps(params: Mapping[str, Any]) -> List[str]:
    """Check for circular dependencies in placeholder definitions.

    Parameters
    ----------
    params : Mapping[str, Any]
        Parameters configuration dictionary.

    Returns
    -------
    List[str]
        List of error messages (empty if no circular deps).
    """
    errors: List[str] = []

    placeholders = params.get("placeholders", {})
    if not placeholders:
        return errors

    deps: Dict[str, Set[str]] = {}
    for name, expr in placeholders.items():
        if isinstance(expr, str):
            # Extract dependencies from placeholder expression
            matches = _PLACEHOLDER_RE.findall(expr)
            deps[name] = {match[0] for match in matches}

    visited: Set[str] = set()
    # Track current recursion path for cycle detection
    rec_stack: Set[str] = set()

    def _has_cycle(node: str) -> bool:
        visited.add(node)
        # Mark as being processed
        rec_stack.add(node)

        for dep in deps.get(node, set()):
            if dep not in visited:
                # Recursively check dependencies
                if _has_cycle(dep):
                    return True
            elif dep in rec_stack:
                # Found back-edge: cycle detected
                cycle = list(rec_stack) + [dep]
                errors.append(
                    f"Circular dependency detected in placeholders: {' -> '.join(cycle)}"
                )
                return True

        # Remove from recursion stack when done
        rec_stack.remove(node)
        return False

    for name in placeholders:
        if name not in visited:
            _has_cycle(name)

    return errors
