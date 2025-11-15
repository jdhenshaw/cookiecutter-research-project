# src/phangs_scouse/core/llm.py

from __future__ import annotations

from phangs_scouse.settings import OPENAI_API_KEY, OPENAI_BASE_URL

from . import logging_config

logger = logging_config.get_logger(__name__)

try:
    from openai import OpenAI

    _HAS_OPENAI = True
except ImportError:
    OpenAI = None  # type: ignore
    _HAS_OPENAI = False


class LLMUnavailableError(RuntimeError):
    """Raised when LLM functionality is used but OpenAI is not installed."""


def assert_llm_available():
    """Raise a clean error if the user hasn't installed optional LLM deps."""
    if not _HAS_OPENAI:
        raise LLMUnavailableError(
            "LLM features require the optional dependency 'openai'.\n"
            "Install it via:\n\n    pip install phangs-scouse[llm]\n"
        )


def get_openai_client() -> "OpenAI":
    """
    Return a configured OpenAI client using environment variables,
    IF optional deps are available.
    """
    assert_llm_available()

    if not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Create a `.env` from `.env_template` "
            "and set your key."
        )

    kwargs = {"api_key": OPENAI_API_KEY}
    if OPENAI_BASE_URL:
        kwargs["base_url"] = OPENAI_BASE_URL

    return OpenAI(**kwargs)


def chat(model: str, messages: list[dict], **kwargs):
    """Convenience wrapper around OpenAI chat completions.

    Parameters
    ----------
    model : str
        The model to use for the chat completion.
    messages : list[dict]
        The messages to send to the model.
    **kwargs : Any
        Additional keyword arguments to pass to the OpenAI client.

    Returns
    -------
    OpenAIResponse
        The response from the OpenAI API.
    """
    assert_llm_available()
    client = get_openai_client()
    return client.chat.completions.create(
        model=model,
        messages=messages,
        **kwargs,
    )
