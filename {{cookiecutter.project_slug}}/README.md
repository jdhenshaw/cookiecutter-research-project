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
- `env/` — Environment setup (requirements, virtualenv)

---

## Setup

```bash
# create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# install dependencies
pip install -r env/requirements.txt
pip install -e .
```

---

## Quickstart

You can run a registered task immediately:

```bash
python -c "from {{ cookiecutter.package_name }}.tasks import run_task; print(run_task('template'))"
```

This writes a small artifact to `data/products/example_artifact.txt`.

---

## Tips

- All data paths and analysis parameters are defined in `config/paths.yaml` and `config/params.yaml`.
- You can create new tasks by adding a file to `src/{{ cookiecutter.package_name }}/tasks/` with a top-level `run()` function.
- The task registry auto-discovers new tasks — no manual imports needed.
- Version control: track only code and configuration; avoid committing large data files.

---
