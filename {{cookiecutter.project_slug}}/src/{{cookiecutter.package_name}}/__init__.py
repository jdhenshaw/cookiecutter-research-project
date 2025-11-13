__all__ = ["core", "tasks", "plotting"]

try:
    from importlib.metadata import PackageNotFoundError, version

    __version__ = version(__package__ or __name__)
except PackageNotFoundError:
    # Fallback
    try:
        from ._version import version as __version__
    except ImportError:
        __version__ = "0.0.0"
