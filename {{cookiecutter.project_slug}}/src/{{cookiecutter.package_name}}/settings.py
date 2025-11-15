from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ENV_PATH = PROJECT_ROOT / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)


def get_env(
    key: str, default: str | None = None, *, required: bool = False
) -> str | None:
    """
    Get an environment variable, optionally enforcing that it exists.

    Notes
    -----
    This function is a wrapper around the ``os.getenv`` function that adds
    optional required checking and default values.

    Examples
    --------
    >>> OPENAI_API_KEY = get_env("OPENAI_API_KEY", required=True)

    Parameters
    ----------
    key : str
        The environment variable to get.
    default : str | None, optional
        The default value to return if the environment variable is not set.
    required : bool, optional
        Whether the environment variable is required. If True and the environment variable is not set, a RuntimeError will be raised.

    Raises
    ------
    RuntimeError
        If the environment variable is required and not set.

    Returns
    -------
    str | None
        The environment variable value.
    """
    value = os.getenv(key, default)
    if required and value is None:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return value


OPENAI_API_KEY = get_env("OPENAI_API_KEY")
OPENAI_BASE_URL = get_env("OPENAI_BASE_URL")
ENV = get_env("ENV", "dev")
LOG_LEVEL = get_env("LOG_LEVEL", "INFO")
