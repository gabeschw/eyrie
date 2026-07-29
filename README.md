# Eyrie

A commanding place above your work — scaffold for planning across sources.

Eyrie creates coordination repos where you (and your agents) can see across
multiple projects, notes, and sources without reaching down to change them.
Read-only `links/` point to the real sources; curated `docs/` build persistent
understanding over time.

## Install

```sh
uvx eyrie init my-workspace
```

Or install permanently:

```sh
uv tool install eyrie
```

## Usage

### Create a new eyrie

```sh
eyrie init my-workspace
```

You'll be asked for a one-sentence description. Eyrie then generates the full
scaffold: `AGENTS.md`, `docs/`, `links/`, git repo with a pre-commit hook, and
agent permission rules for OpenCode and Claude Code.

### Add sources

```sh
eyrie add ~/Projects/resume-cv
eyrie add ~/Documents/ObsidianVaults/Career --skill "vercel-labs/agent-skills/obsidian-cli"
eyrie add --type remote --name jira --description "Team Jira (team.atlassian.net)"
```

Type is inferred (`repo` if `.git/` exists, else `folder`), name defaults to the
directory basename, and paths under `$HOME` are stored as `~/...` in `eyrie.toml`.
Each `add` auto-syncs (creates symlinks, appends doc skeletons, installs skills).

You can also edit `eyrie.toml` directly:

```toml
[[sources]]
name = "resume"
path = "~/Projects/resume-cv"
type = "repo"

[[sources]]
name = "career-vault"
path = "~/Documents/ObsidianVaults/Career"
type = "folder"
skills = ["vercel-labs/agent-skills/obsidian-cli"]

[[sources]]
name = "jira"
type = "remote"
description = "Team Jira (team.atlassian.net)"
```

### Sync

```sh
eyrie sync
```

This materializes symlinks under `links/`, appends skeleton entries to
`docs/domain/repos.md` and `sources.md`, and installs any declared skills
via `npx skills add`.

## How it works

```
my-workspace/
├── AGENTS.md        ← agent instructions (generated once, then yours)
├── CLAUDE.md        ← points to AGENTS.md
├── eyrie.toml       ← sources, skills config
├── docs/            ← persistent knowledge (domain, topics, workflow)
├── links/           ← READ-ONLY symlinks to sources (git-ignored)
├── output/          ← versioned deliverables
├── scripts/         ← automation (uv run scripts/foo.py)
└── scratch/         ← ephemeral work (git-ignored)
```

The core pattern: **plan here, execute there.** Use the eyrie to understand
cross-source work, then make changes in the individual source repos.

## Requirements

- Python >= 3.11
- [uv](https://docs.astral.sh/uv/) (for running and installing)
- Node.js / npx (optional, for skill installation via `npx skills`)

## License

MIT
