"""Manifest file scanning and management.

This module provides functions for scanning directories, parsing filenames,
building manifest tables, and reading/writing ECSV manifest files.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List

from astropy.table import Table


def scan_files(
    root: Path | str,
    patterns: Iterable[str] = ("*",),
    recursive: bool = False,
) -> List[Path]:
    """
    Scan a directory for files matching the given patterns.

    Parameters
    ----------
    root : Path or str
        Directory to scan.
    patterns : iterable of str
        Glob patterns, e.g. ["*.fits", "*.txt"].
    recursive : bool, optional
        Whether to use recursive globbing (**).

    Returns
    -------
    list[Path]
        Sorted list of matching paths.
    """
    root = Path(root)
    files: list[Path] = []

    for pat in patterns:
        if recursive:
            files.extend(root.rglob(pat))
        else:
            files.extend(root.glob(pat))

    # Unique & sorted
    return sorted(set(f for f in files if f.is_file()))


def default_parser(base: str) -> Dict[str, Any]:
    """
    Default parser returns only the basename.

    Useful if the user wants a manifest but has no filename rules.

    Parameters
    ----------
    base : str
        Filename without extension.

    Returns
    -------
    dict
        {"base": base}
    """
    return {"base": base}


def apply_filters(
    items: Iterable[Dict[str, Any]],
    filters: Iterable[Callable[[Dict[str, Any]], bool]] | None,
) -> List[Dict[str, Any]]:
    """
    Apply filter callbacks to rows.

    Parameters
    ----------
    items : iterable of dict
        Parsed manifest rows.
    filters : optional iterable of callables
        Each must accept a row dict and return True/False.

    Returns
    -------
    list[dict]
        Filtered rows.
    """
    if not filters:
        return list(items)

    out = []
    for row in items:
        if all(f(row) for f in filters):
            out.append(row)
    return out


def build_manifest_rows(
    files: Iterable[Path],
    parser: Callable[[str], Dict[str, Any]] = default_parser,
    filters: Iterable[Callable[[Dict[str, Any]], bool]] | None = None,
) -> List[Dict[str, Any]]:
    """
    Build manifest rows from file paths using a basename parser.

    Parameters
    ----------
    files : iterable of Path
        Paths discovered via scan_files().
    parser : callable
        Function taking a basename (no extension) and returning a dict.
        Example: {"galaxy": "...", "array": "..."}.
    filters : iterable of callable, optional
        Row-level filters. Each receives a row-dict and must return True/False.

    Returns
    -------
    list[dict]
        List of parsed, optionally filtered manifest rows.
    """
    rows = []
    for p in files:
        # Filename without extension
        base = p.stem
        # Always include path and base
        entry = {"path": str(p), "base": base}
        # Add parsed fields (e.g., galaxy, array)
        entry.update(parser(base))
        rows.append(entry)

    # Apply domain-specific filters
    return apply_filters(rows, filters)


def write_manifest(
    rows: Iterable[Dict[str, Any]],
    out_path: Path | str,
    overwrite: bool = True,
) -> Path:
    """
    Write manifest rows to an ECSV file.

    Parameters
    ----------
    rows : iterable of dict
        Manifest rows.
    out_path : Path or str
        Target output file.
    overwrite : bool
        Overwrite existing file.

    Returns
    -------
    Path
        The resulting file path.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    Table(rows).write(out_path, format="ascii.ecsv", overwrite=overwrite)
    return out_path


def load_manifest(path: Path | str) -> Table:
    """
    Load an existing ECSV manifest.

    Parameters
    ----------
    path : Path or str
        ECSV file path.

    Returns
    -------
    Astropy Table
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Manifest not found: {path}")
    return Table.read(path, format="ascii.ecsv")
