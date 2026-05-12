# pyright: reportInvalidTypeForm=false, reportMissingImports=false, reportUndefinedVariable=false
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from {{cookiecutter.package_name}}.core import get_paths


def run() -> Path:
    """Example task: writes a tiny artifact to data/products/."""
    out_dir: Path = get_paths()["data"]["products"]
    out_dir.mkdir(parents=True, exist_ok=True)

    out_file = out_dir / "example_artifact.txt"
    timestamp = datetime.now(timezone.utc).isoformat()
    out_file.write_text(f"hello from template task\nwritten: {timestamp}\n")
    return out_file
