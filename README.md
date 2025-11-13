# Cookiecutter Research Project Template

A clean, flexible **Cookiecutter template** for reproducible research projects.

> Designed to organize data, code, notebooks, and figures in a consistent way.

---

## What It Does

This template helps you:

- Keep research projects modular and reproducible.
- Separate raw data, processed outputs, and figures cleanly.
- Standardize your project structure for future work.

---

## Folder Structure

The generated project looks like this:

```
my-research-project/
├── config/          # configuration files (paths, parameters)
├── data/
│   ├── core/        # raw or base data
│   ├── products/    # processed, publishable outputs
│   └── scratch/     # temporary or intermediate files
├── src/
│   ├── core/        # reusable code (I/O, config loading)
│   ├── tasks/       # analysis routines
│   └── plotting/    # visualization utilities
├── notebooks/       # Jupyter notebooks
├── figures/         # output figures
├── tables/          # output tables
├── presentations/   # project presentations
├── manuscripts/     # project manuscripts
├── env/             # environment setup (requirements, virtualenv)
└── README.md
```

---

## How to Use

```bash
pip install cookiecutter
cookiecutter gh:jdhenshaw/cookiecutter-research-project
```

Then follow the prompts to name your new project and set up your environment.

---

## Quickstart (inside a generated project)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r env/requirements.txt
pip install -e .
python -c "from my_research_project.tasks import run_task; print(run_task('template'))"
```

---

## Notes

- Configuration lives in `config/paths.yaml` and `config/params.yaml`.
- Add new tasks under `src/<project_name>/tasks/` with a `run()` function.
- Data is never tracked in Git — only configuration, scripts, and outputs.

---

## Credits

Created by **Jonathan D. Henshaw**

---

> 📘 The generated project includes its own README with similar content customized to your project’s name and description.
