# {{ cookiecutter.project_name }}

A clean, flexible research project template generated from **cookiecutter-research-project**.

> {{ cookiecutter.description }}

---

## Structure

- `config/` — Configuration files (paths, parameters, settings)
- `data/` — Data directories:
  - `core/` — Raw or base data
  - `products/` — Processed, publishable outputs
  - `scratch/` — Temporary or intermediate data
- `src/` — Source code for reusable modules:
  - `core/` — I/O and configuration utilities
  - `tasks/` — Reproducible analysis tasks
  - `plotting/` — Figure and visualization scripts
- `pipelines/` — Optional workflow definitions (Snakemake, YAML, etc.)
- `notebooks/` — Jupyter notebooks for exploration or papers
- `figures/` — Output figures and plots
- `tables/` — Output tables
- `presentations/` - Project Presentations
- `manuscripts/` - Project Manuscripts

---

## Setup

```bash
# create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# install the project (with dev tooling and notebook support)
pip install -e ".[dev,notebook]"
```

---

## Quickstart

You can run a registered task immediately:

```bash
{{ cookiecutter.project_slug }} run template
```

This writes a small artifact to `data/products/example_artifact.txt`.

---

## Tips

- All data paths and analysis parameters are defined in `config/paths.yaml` and `config/params.yaml`.
- You can create new tasks by adding a file to `src/{{ cookiecutter.package_name }}/tasks/` with a top-level `run()` function.
- The task registry auto-discovers new tasks — no manual imports needed.
- Version control: track only code and configuration; avoid committing large data files.

---
