"""Eyrie CLI entry point."""

from pathlib import Path

import click

from eyrie.add import add_source
from eyrie.init import create_scaffold
from eyrie.sync import find_eyrie_root, load_config, sync_docs, sync_links, sync_skills


@click.group()
@click.version_option()
def main() -> None:
    """Eyrie — a commanding place above your work."""


@main.command()
@click.argument("name")
def init(name: str) -> None:
    """Create a new Eyrie repo."""
    target = Path(name).resolve()
    eyrie_name = target.name
    if target.exists():
        raise click.ClickException(f"Directory already exists: {target}")

    description = click.prompt(
        "Describe your eyrie in one or two sentences"
        " (who you are, what this coordinates)"
    )

    create_scaffold(target, eyrie_name, description)
    click.echo(f"Created Eyrie repo: {target}")


@main.command()
def sync() -> None:
    """Sync links and skills from eyrie.toml."""
    root = find_eyrie_root()
    config = load_config(root)
    click.echo("Syncing links...")
    sync_links(root, config)
    click.echo("Syncing docs...")
    sync_docs(root, config)
    click.echo("Syncing skills...")
    sync_skills(root, config)


@main.command()
@click.argument("path", required=False)
@click.option("--name", "-n", help="Name for the source (defaults to directory basename)")
@click.option(
    "--type", "source_type", type=click.Choice(["repo", "folder", "remote"]),
    help="Source type (inferred from path if not given)",
)
@click.option("--skill", "-s", "skills", multiple=True, help="Skill to attach (repeatable)")
@click.option("--description", "-d", help="Description (used for remote sources)")
def add(
    path: str | None,
    name: str | None,
    source_type: str | None,
    skills: tuple[str, ...],
    description: str | None,
) -> None:
    """Add a source to eyrie.toml and sync."""
    root = find_eyrie_root()
    source_name = add_source(root, path, name, source_type, skills, description)
    click.echo(f"Added source: {source_name}")

    config = load_config(root)
    click.echo("Syncing links...")
    sync_links(root, config)
    click.echo("Syncing docs...")
    sync_docs(root, config)
    click.echo("Syncing skills...")
    sync_skills(root, config)
