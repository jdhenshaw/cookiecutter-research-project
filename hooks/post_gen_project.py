from pathlib import Path


def main() -> None:
    """Run after the project is generated."""
    src = Path("pyproject.template.toml")
    dst = Path("pyproject.toml")

    if src.exists() and not dst.exists():
        src.rename(dst)
        print(f"Renamed {src} → {dst}")


if __name__ == "__main__":
    main()
