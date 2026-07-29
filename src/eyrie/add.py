"""Add a source to eyrie.toml."""

import tomllib
from pathlib import Path

import click


def add_source(
    root: Path,
    path: str | None,
    name: str | None,
    source_type: str | None,
    skills: tuple[str, ...],
    description: str | None,
) -> str:
    """Add a source entry to eyrie.toml. Returns the resolved name."""
    toml_path = root / "eyrie.toml"
    config_text = toml_path.read_text()

    # Parse to validate and check for duplicates
    with open(toml_path, "rb") as f:
        config = tomllib.load(f)

    # Resolve name
    if name is None:
        if path is None:
            raise click.ClickException("--name is required for remote sources")
        name = Path(path).expanduser().resolve().name

    # Check for duplicates
    existing_names = {s["name"] for s in config.get("sources", [])}
    if name in existing_names:
        raise click.ClickException(f"Source '{name}' already exists in eyrie.toml")

    # Infer type
    if source_type is None:
        if path is None:
            source_type = "remote"
        else:
            resolved = Path(path).expanduser().resolve()
            source_type = "repo" if (resolved / ".git").is_dir() else "folder"

    # Validate path exists (unless remote)
    if source_type != "remote":
        if path is None:
            raise click.ClickException("Path is required for non-remote sources")
        resolved = Path(path).expanduser().resolve()
        if not resolved.exists():
            raise click.ClickException(f"Path does not exist: {resolved}")

    # Build the toml entry
    portable_path = _to_portable_path(path) if path else None
    entry = _format_toml_entry(name, portable_path, source_type, skills, description)

    # Append to eyrie.toml
    with toml_path.open("a") as f:
        f.write(entry)

    return name


def _to_portable_path(path: str) -> str:
    """Convert path to use ~ when under $HOME."""
    resolved = Path(path).expanduser().resolve()
    home = Path.home()
    try:
        relative = resolved.relative_to(home)
        return f"~/{relative}"
    except ValueError:
        return str(resolved)


def _format_toml_entry(
    name: str,
    path: str | None,
    source_type: str,
    skills: tuple[str, ...],
    description: str | None,
) -> str:
    """Format a [[sources]] TOML entry."""
    lines = ["\n[[sources]]", f'name = "{name}"']
    if path:
        lines.append(f'path = "{path}"')
    lines.append(f'type = "{source_type}"')
    if description:
        lines.append(f'description = "{description}"')
    if skills:
        skills_list = ", ".join(f'"{s}"' for s in skills)
        lines.append(f"skills = [{skills_list}]")
    return "\n".join(lines) + "\n"
