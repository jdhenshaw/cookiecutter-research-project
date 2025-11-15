# SYSTEM SUMMARY

**Project:** `cookiecutter-research-project`

## Modules

- `hooks/post_gen_project.py`
  - Functions:
    - main: Run after the project is generated.

- `{{cookiecutter.project_slug}}/src/{{cookiecutter.package_name}}/core/config.py`
  - *Overview*: Configuration loading and caching.
  - Functions:
    - get_configs: Load and cache the PHANGS-ScousePy configuration.
    - get_paths: Return the ``paths`` configuration dictionary.
    - get_params: Return the ``params`` configuration dictionary.
    - get_files: Return the ``files`` configuration dictionary.
    - ensure_project_directories: Ensure that all directories defined in ``paths.yaml`` exist.
    - clear_config_cache: Clear the configuration cache.

- `{{cookiecutter.project_slug}}/src/{{cookiecutter.package_name}}/core/context.py`
  - *Overview*: Template context building and management.
  - Functions:
    - flatten_dict: Flatten a nested dictionary into a single-level dict.
    - build_generic_context: Build the flattened template context for file resolution.

- `{{cookiecutter.project_slug}}/src/{{cookiecutter.package_name}}/core/debug.py`
  - *Overview*: Debugging utilities for template resolution and context inspection.
  - Functions:
    - debug_template: Debug template resolution step-by-step.
    - debug_context: Show all available context keys and their values.

- `{{cookiecutter.project_slug}}/src/{{cookiecutter.package_name}}/core/files.py`
  - *Overview*: File path resolution and template management.
  - Functions:
    - deep_get: Walk a nested mapping using a dotted key.
    - resolve_file: Resolve a file template key into a concrete path string.
    - get_path: Resolve a file path from files.yaml.

- `{{cookiecutter.project_slug}}/src/{{cookiecutter.package_name}}/core/io.py`
  - *Overview*: Input/output operations and template resolution.
  - Functions:
    - project_root: Get the project root directory.
    - load_config: Load configuration files.
    - ensure_directories: Create all directories found inside a nested paths dictionary.
    - make_context: Merge one or more mappings into a flat context dictionary.
    - resolve_template: Resolve a single template string using the provided context.
    - resolve_block: Recursively resolve dict/list/str blocks of templates.
    - get_by_dotted: Retrieve a nested value from a mapping using a dotted key.

- `{{cookiecutter.project_slug}}/src/{{cookiecutter.package_name}}/core/logging_config.py`
  - *Overview*: Logging configuration and setup.
  - Functions:
    - setup_logging: Configure logging for phangs_scouse.
    - get_logger: Get a logger for a specific module.

- `{{cookiecutter.project_slug}}/src/{{cookiecutter.package_name}}/core/manifest.py`
  - *Overview*: Manifest file scanning and management.
  - Functions:
    - scan_files: Scan a directory for files matching the given patterns.
    - default_parser: Default parser returns only the basename.
    - apply_filters: Apply filter callbacks to rows.
    - build_manifest_rows: Build manifest rows from file paths using a basename parser.
    - write_manifest: Write manifest rows to an ECSV file.
    - load_manifest: Load an existing ECSV manifest.

- `{{cookiecutter.project_slug}}/src/{{cookiecutter.package_name}}/core/utils.py`
  - *Overview*: Utility functions for the phangs_scouse core module.
  - Functions:
    - edit_distance: Calculate the Levenshtein distance between two strings.
    - fuzzy_match_key: Find similar keys using edit distance.
    - working_directory: Context manager for temporarily changing the working directory.

- `{{cookiecutter.project_slug}}/src/{{cookiecutter.package_name}}/core/validation.py`
  - Functions:
    - validate_configs: Validate configuration files.
    - validate_paths: Validate that paths exist or can be created.
    - validate_templates: Validate that all templates can be resolved.

- `{{cookiecutter.project_slug}}/src/{{cookiecutter.package_name}}/tasks/init_validate_configs.py`
  - Functions:
    - run: Validate project configuration files.

- `{{cookiecutter.project_slug}}/src/{{cookiecutter.package_name}}/tasks/registry.py`
  - Functions:
    - list_tasks: Return available task names.
    - get_task: Return the task callable for `name`, or raise KeyError.
    - run_task: Run a discovered task by name and return its result.

- `{{cookiecutter.project_slug}}/src/{{cookiecutter.package_name}}/tasks/template.py`
  - Functions:
    - run: Example task: writes a tiny artifact to data/products/.

## Dependency Graph (internal imports)

- `cookiecutter_research_project.{{cookiecutter.project_slug}}.src.{{cookiecutter.package_name}}.core.config` depends on:
  - `cookiecutter_research_project.{{cookiecutter.project_slug}}.src.{{cookiecutter.package_name}}.core.io`
- `cookiecutter_research_project.{{cookiecutter.project_slug}}.src.{{cookiecutter.package_name}}.core.context` depends on:
  - `cookiecutter_research_project.{{cookiecutter.project_slug}}.src.{{cookiecutter.package_name}}.core.io`
- `cookiecutter_research_project.{{cookiecutter.project_slug}}.src.{{cookiecutter.package_name}}.core.debug` depends on:
  - `cookiecutter_research_project.{{cookiecutter.project_slug}}.src.{{cookiecutter.package_name}}.core.config`
  - `cookiecutter_research_project.{{cookiecutter.project_slug}}.src.{{cookiecutter.package_name}}.core.context`
  - `cookiecutter_research_project.{{cookiecutter.project_slug}}.src.{{cookiecutter.package_name}}.core.files`
  - `cookiecutter_research_project.{{cookiecutter.project_slug}}.src.{{cookiecutter.package_name}}.core.io`
- `cookiecutter_research_project.{{cookiecutter.project_slug}}.src.{{cookiecutter.package_name}}.core.files` depends on:
  - `cookiecutter_research_project.{{cookiecutter.project_slug}}.src.{{cookiecutter.package_name}}.core.config`
  - `cookiecutter_research_project.{{cookiecutter.project_slug}}.src.{{cookiecutter.package_name}}.core.context`
  - `cookiecutter_research_project.{{cookiecutter.project_slug}}.src.{{cookiecutter.package_name}}.core.io`
  - `cookiecutter_research_project.{{cookiecutter.project_slug}}.src.{{cookiecutter.package_name}}.core.utils`
- `cookiecutter_research_project.{{cookiecutter.project_slug}}.src.{{cookiecutter.package_name}}.core.io` depends on:
  - `cookiecutter_research_project.{{cookiecutter.project_slug}}.src.{{cookiecutter.package_name}}.core.utils`
- `cookiecutter_research_project.{{cookiecutter.project_slug}}.src.{{cookiecutter.package_name}}.core.validation` depends on:
  - `cookiecutter_research_project.{{cookiecutter.project_slug}}.src.{{cookiecutter.package_name}}.core.config`
  - `cookiecutter_research_project.{{cookiecutter.project_slug}}.src.{{cookiecutter.package_name}}.core.context`
  - `cookiecutter_research_project.{{cookiecutter.project_slug}}.src.{{cookiecutter.package_name}}.core.io`

## Pipeline

<!-- TODO: describe main system flow in 1–3 lines -->
