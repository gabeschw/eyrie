"""Eyrie CLI entry point."""

from pathlib import Path

import click

from eyrie.init import create_scaffold


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
    click.echo("Syncing...")
