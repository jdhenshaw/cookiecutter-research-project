"""Utility functions for the phangs_scouse core module.

This module provides shared utility functions used across the core package,
including string matching algorithms and resource management helpers.
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


def edit_distance(s1: str, s2: str) -> int:
    """Calculate the Levenshtein distance between two strings.

    Notes
    -----

    The Levenshtein distance is the minimum number of single-character edits
    (insertions, deletions, or substitutions) required to change one string
    into another.

    Examples
    --------
    >>> edit_distance("kitten", "sitting")
    3
    >>> edit_distance("hello", "hello")
    0

    Parameters
    ----------
    s1 : str
        The first string to compare.
    s2 : str
        The second string to compare.

    Returns
    -------
    int
        The Levenshtein distance between the two strings.
    """
    if len(s1) < len(s2):
        return edit_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def fuzzy_match_key(
    target: str,
    candidates: list[str],
    max_distance: int = 2,
    case_sensitive: bool = False,
) -> list[str]:
    """Find similar keys using edit distance.

    Examples
    --------
    >>> fuzzy_match_key("mom0", ["mom0", "mom1", "cube", "mom0_mask"])
    ['mom0', 'mom0_mask']

    Parameters
    ----------
    target : str
        The target key to match.
    candidates : list[str]
        List of candidate keys.
    max_distance : int, optional
        Maximum edit distance to consider. Defaults to 2.
    case_sensitive : bool, optional
        Whether to perform case-sensitive matching. Defaults to False.

    Returns
    -------
    list[str]
        List of similar keys, sorted alphabetically.
    """
    matches = []
    target_normalized = target if case_sensitive else target.lower()
    for candidate in candidates:
        candidate_normalized = candidate if case_sensitive else candidate.lower()
        if edit_distance(target_normalized, candidate_normalized) <= max_distance:
            matches.append(candidate)
    return sorted(matches)


@contextmanager
def working_directory(path: Path | str) -> Iterator[Path]:
    """Context manager for temporarily changing the working directory.

    Notes
    -----

    This is a safer alternative to using os.chdir() directly, as it
    automatically restores the original directory even if an exception occurs.

    Examples
    --------
    >>> from pathlib import Path
    >>> with working_directory("/tmp") as new_dir:
    ...     # Do work in /tmp
    ...     pass
    # Automatically returns to original directory

    Parameters
    ----------
    path : Path | str
        The directory to change to.

    Yields
    ------
    Path
        The absolute path of the new working directory.
    """
    import os

    original_dir = Path.cwd().resolve()
    target_dir = Path(path).resolve()

    try:
        os.chdir(target_dir)
        yield target_dir
    finally:
        os.chdir(original_dir)
