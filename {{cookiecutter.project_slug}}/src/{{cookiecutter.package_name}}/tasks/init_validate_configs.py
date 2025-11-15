from __future__ import annotations

from phangs_scouse.core import validate_configs


def run(check_paths: bool = True, check_templates: bool = True) -> None:
    """Validate project configuration files.

    Parameters
    ----------
    check_paths : bool, optional
        Whether to check if paths exist. Defaults to True.
    check_templates : bool, optional
        Whether to validate template resolution. Defaults to True.

    Raises
    ------
    SystemExit
        If validation fails.
    """
    is_valid, errors = validate_configs(
        check_paths=check_paths, check_templates=check_templates
    )

    if is_valid:
        print("Config validation passed")
        return

    print("Config validation failed:")
    for error in errors:
        print(f"  - {error}")
    raise SystemExit(1)


if __name__ == "__main__":
    run()
