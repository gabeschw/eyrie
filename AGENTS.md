# AGENTS.md

Eyrie is a Python CLI tool that scaffolds and manages "eyrie" repos — coordination
workspaces with read-only symlinked sources, curated docs, and multi-agent-platform support.

## Commands

```sh
uv run eyrie init <name>   # scaffold a new eyrie repo
uv run eyrie add <path>    # add a source and auto-sync
uv run eyrie sync          # materialize symlinks + install skills (idempotent)
uv run pytest              # run tests
uv run pytest tests/test_init.py::TestAgentsMd::test_contains_name  # single test
```

## Architecture

- `src/eyrie/cli.py` — click CLI entry point (`main` group, `init`, `add`, and `sync` commands)
- `src/eyrie/init.py` — scaffold generation logic (`create_scaffold`)
- `src/eyrie/add.py` — add source to eyrie.toml (`add_source`)
- `src/eyrie/sync.py` — sync logic (links, docs, skills)
- `src/eyrie/templates.py` — all template content as string constants
- `tests/test_init.py`, `tests/test_sync.py`, `tests/test_add.py` — tests use `click.testing.CliRunner`

## Conventions

- The word "tower" must not appear in code or generated output. Use "eyrie" instead.
- Templates live as plain string constants in `templates.py`, not as separate files or Jinja2.
- `eyrie.toml` uses `[eyrie]` as the top-level table (not `[tower]`).
- Generated eyries use `links/` (read-only, git-ignored) for symlinks to sources.
- The design doc is at `docs/design.md`.

## Build & dependencies

- Build backend: hatchling with `src/` layout
- Runtime: click (CLI)
- Dev: pytest
- Requires Python >=3.11 (uses stdlib `tomllib`)
