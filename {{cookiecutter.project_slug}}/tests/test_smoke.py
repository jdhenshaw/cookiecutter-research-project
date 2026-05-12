# pyright: reportMissingImports=false, reportUndefinedVariable=false
"""Smoke tests for a freshly generated project."""

from {{cookiecutter.package_name}}.core import validate_configs
from {{cookiecutter.package_name}}.tasks import list_tasks, run_task


def test_validate_configs_passes():
    is_valid, errors = validate_configs()
    assert is_valid, errors


def test_template_task_writes_artifact():
    out_path = run_task("template")
    assert out_path.exists()
    assert "hello from template task" in out_path.read_text()


def test_template_task_is_registered():
    assert "template" in list_tasks()
