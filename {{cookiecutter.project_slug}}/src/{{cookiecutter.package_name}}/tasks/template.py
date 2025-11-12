# pyright: reportUndefinedVariable=false, reportMissingImports=false
from __future__ import annotations

from datetime import datetime
from importlib import import_module
from pathlib import Path

PACKAGE = "{{cookiecutter.package_name}}"
load_config = import_module(f"{PACKAGE}.core.io").load_config


def run() -> Path:
    """Example task: writes a tiny artifact to data/products/."""
    paths, params = load_config()
    out_dir: Path = paths["data"]["products"]
    out_dir.mkdir(parents=True, exist_ok=True)

    out_file = out_dir / "example_artifact.txt"
    out_file.write_text(f"hello from template task\nwritten: {datetime.utcnow().isoformat()}Z\n")
    return out_file
