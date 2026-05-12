# pyright: reportInvalidTypeForm=false, reportMissingImports=false, reportUndefinedVariable=false
from __future__ import annotations

import typer

from .core import validate_configs
from .tasks import list_tasks, run_task

app = typer.Typer(
    name="{{ cookiecutter.project_slug }}",
    help="Project CLI for {{ cookiecutter.project_name }}.",
    no_args_is_help=True,
)


@app.command("list")
def list_cmd() -> None:
    """List registered tasks."""
    for name in list_tasks():
        typer.echo(name)


@app.command()
def run(task: str) -> None:
    """Run a registered task by name."""
    result = run_task(task)
    if result is not None:
        typer.echo(result)


@app.command()
def validate() -> None:
    """Validate project configuration files."""
    is_valid, errors = validate_configs()
    if is_valid:
        typer.echo("Config validation passed")
        raise typer.Exit(0)
    typer.echo("Config validation failed:")
    for err in errors:
        typer.echo(f"  - {err}")
    raise typer.Exit(1)
