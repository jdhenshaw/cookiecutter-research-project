from __future__ import annotations

import importlib
import pkgutil
from types import ModuleType
from typing import Callable, Iterable

PACKAGE = "{{cookiecutter.package_name}}"
TASKS_PKG = f"{PACKAGE}.tasks"
_TASKS: dict[str, Callable[..., object]] = {}
_DISCOVERED = False


def _iter_task_modules() -> Iterable[ModuleType]:
    """Yield imported task modules in `{{cookiecutter.package_name}}.tasks`."""
    pkg = importlib.import_module(TASKS_PKG)
    for modinfo in pkgutil.iter_modules(pkg.__path__):
        name = modinfo.name
        if name.startswith("_") or name in {"registry"}:
            continue
        yield importlib.import_module(f"{TASKS_PKG}.{name}")


def _discover(force: bool = False) -> None:
    """Populate the _TASKS cache by importing task modules.

    Parameters
    ----------
    force : bool, optional
        Whether to force a refresh of the task modules.
    """
    global _DISCOVERED
    if _DISCOVERED and not force:
        return
    _TASKS.clear()
    for mod in _iter_task_modules():
        # Optional override: TASK_NAME = "nice-name"
        task_name = getattr(mod, "TASK_NAME", mod.__name__.split(".")[-1])
        run_fn = getattr(mod, "run", None)
        if callable(run_fn):
            _TASKS[task_name] = run_fn
    _DISCOVERED = True


def list_tasks(force_refresh: bool = False) -> list[str]:
    """Return available task names.

    Parameters
    ----------
    force_refresh : bool, optional
        Whether to force a refresh of the task modules.

    Returns
    -------
    list[str]
        The available task names.
    """
    _discover(force=force_refresh)
    return sorted(_TASKS.keys())


def get_task(name: str) -> Callable[..., object]:
    """Return the task callable for `name`, or raise KeyError.

    Parameters
    ----------
    name : str
        The name of the task to get.

    Raises
    ------
    KeyError
        If the task is not found.

    Returns
    -------
    Callable[..., object]
        The task callable.
    """
    _discover()
    try:
        return _TASKS[name]
    except KeyError as exc:
        raise KeyError(f"Task '{name}' not found. Available: {', '.join(list_tasks())}") from exc


def run_task(name: str, *args, **kwargs) -> object:
    """Run a discovered task by name and return its result.

    Parameters
    ----------
    name : str
        The name of the task to run.
    *args : Any
        The arguments to pass to the task.
    **kwargs : Any
        The keyword arguments to pass to the task.

    Returns
    -------
    object
        The result of the task.
    """
    fn = get_task(name)
    return fn(*args, **kwargs)
