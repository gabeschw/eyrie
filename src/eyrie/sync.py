"""Sync logic: materialize symlinks and install skills from eyrie.toml."""

import shutil
import subprocess
import tomllib
from pathlib import Path

import click


def find_eyrie_root() -> Path:
    """Walk up from cwd to find the directory containing eyrie.toml."""
    current = Path.cwd()
    while True:
        if (current / "eyrie.toml").is_file():
            return current
        parent = current.parent
        if parent == current:
            raise click.ClickException(
                "No eyrie.toml found in current directory or any parent"
            )
        current = parent


def load_config(root: Path) -> dict:
    """Parse eyrie.toml and return its contents."""
    with open(root / "eyrie.toml", "rb") as f:
        return tomllib.load(f)


def sync_links(root: Path, config: dict) -> None:
    """Create symlinks for all sources declared in eyrie.toml."""
    sources = config.get("sources", [])
    if not sources:
        click.echo("No sources declared in eyrie.toml")
        return

    for source in sources:
        name = source["name"]
        source_type = source.get("type", "folder")
        path_str = source.get("path")

        if source_type == "remote":
            click.echo(f"  {name}: remote (no symlink)")
            continue

        if not path_str:
            click.echo(f"  {name}: skipped (no path)")
            continue

        source_path = Path(path_str).expanduser().resolve()
        if not source_path.exists():
            click.echo(f"  {name}: WARNING — path does not exist: {source_path}")
            continue

        if source_type == "repo":
            link_dir = root / "links" / "repos"
        else:
            link_dir = root / "links" / "sources"

        link_dir.mkdir(parents=True, exist_ok=True)
        link = link_dir / name

        if link.is_symlink():
            existing_target = link.resolve()
            if existing_target == source_path:
                click.echo(f"  {name}: already linked")
                continue
            else:
                link.unlink()
                click.echo(f"  {name}: updated → {source_path}")
        else:
            click.echo(f"  {name}: linked → {source_path}")

        link.symlink_to(source_path)


REPO_SKELETON = """\

## {name}
- **Path:** `links/repos/{name}`
- **What it is:**
- **Language / stack:**
- **What it owns:**
- **Main branch:**
- **Notes:**
"""

SOURCE_SKELETON = """\

## {name}
- **Path:** `links/sources/{name}`
- **What it is:**
- **What it owns:**
- **Notes:**
"""


def sync_docs(root: Path, config: dict) -> None:
    """Append skeleton entries to repos.md and sources.md for new sources."""
    sources = config.get("sources", [])
    if not sources:
        return

    repos_md = root / "docs" / "domain" / "repos.md"
    sources_md = root / "docs" / "domain" / "sources.md"

    repos_content = repos_md.read_text() if repos_md.is_file() else ""
    sources_content = sources_md.read_text() if sources_md.is_file() else ""

    repos_additions = []
    sources_additions = []

    for source in sources:
        name = source["name"]
        source_type = source.get("type", "folder")

        if source_type == "remote":
            continue

        if source_type == "repo":
            if f"## {name}" not in repos_content:
                repos_additions.append(REPO_SKELETON.format(name=name))
        else:
            if f"## {name}" not in sources_content:
                sources_additions.append(SOURCE_SKELETON.format(name=name))

    if repos_additions:
        with repos_md.open("a") as f:
            for entry in repos_additions:
                f.write(entry)
        click.echo(f"  Added {len(repos_additions)} entry(s) to docs/domain/repos.md")

    if sources_additions:
        with sources_md.open("a") as f:
            for entry in sources_additions:
                f.write(entry)
        click.echo(
            f"  Added {len(sources_additions)} entry(s) to docs/domain/sources.md"
        )


def sync_skills(root: Path, config: dict) -> None:
    """Install skills declared in eyrie.toml via npx skills add."""
    # Collect all skills: eyrie-level + per-source
    eyrie_config = config.get("eyrie", {})
    all_skills: list[str] = list(eyrie_config.get("skills", []))
    for source in config.get("sources", []):
        all_skills.extend(source.get("skills", []))

    if not all_skills:
        click.echo("  No skills declared")
        return

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique_skills: list[str] = []
    for skill in all_skills:
        if skill not in seen:
            seen.add(skill)
            unique_skills.append(skill)

    if not shutil.which("npx"):
        click.echo(
            "  WARNING — npx not found. Install Node.js to enable skill installation."
        )
        return

    for skill in unique_skills:
        click.echo(f"  Installing: {skill}")
        result = subprocess.run(
            ["npx", "skills", "add", skill],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            click.echo(f"  WARNING — failed to install {skill}: {result.stderr.strip()}")
