# Eyrie — design notes

*Living doc. Started 2026-07-29. Update as decisions are made.*

## Implementation status

| Feature | Status |
|---------|--------|
| `eyrie init` — scaffold generation | Done |
| `eyrie init` — git init + pre-commit hook | Done |
| `eyrie init` — agent permission rules | Done |
| `eyrie init` — `uv init --no-package` | Done |
| `eyrie sync` — symlink materialization | Done |
| `eyrie sync` — append-only docs updates | Done |
| `eyrie sync` — skill installation (`npx skills`) | Done |
| `eyrie add` — add source with auto-sync | Done |
| PyPI publishing | Done |
| MCP server config generation | Out of scope (v1) |
| Windows support | Out of scope (v1) |
| Cursor `.cursor/rules/` bridge | Out of scope (v1) |

## What is Eyrie

A CLI tool and scaffold that generalizes the shekel-kb pattern: an **agent control eyrie**
— a coordination and context layer that sits above a set of linked, read-only sources and
lets agents plan cross-context work.

The core pattern (from shekel-kb):
- Plan and understand cross-context work from the eyrie
- Execute it in the individual repo/source
- `links/` is read-only by design
- Curated `docs/` provide persistent agent memory
- Skills extend what the agent can do with specific sources

Eyrie makes this pattern easy to set up in any context — personal (job search, career
notes, side projects), team, or domain-specific (like shekel-kb itself).

## Name

**Eyrie** — confirmed. Rationale:
- An eagle's nest: elevated home base with commanding view, you plan from it, you return
  to it, you don't act from it directly
- Visually contains "eye" — the thing that sees across a large interconnected landscape
  without reaching down to change it
- Available on PyPI (`aerie` is taken); distinctive, no major tool collision
- CLI: `uvx eyrie init my-workspace`

Prior working name was **Atlas**. Other candidates considered: Meridian, Observatory,
Loom, Canopy, Aerie. See naming brainstorm in conversation history for full context.

Related terminology:
- **Agent control eyrie** — the most accurate descriptor of the pattern
- **Meta-repo** / **umbrella repo** — the established name for the repo-aggregation
  structure (undersells the agent/KB side)
- See `docs/meta/kb-pattern-prior-art.md` for full naming analysis

## Target audience

Developers (for now). Non-technical users are not a current target — CLI comfort assumed.

## Acquisition

Zero-install via `uvx`:

```
uvx eyrie init my-career-eyrie
```

Power users can `uv tool install eyrie` for convenience. `uvx` caches the package so
subsequent runs are fast either way.

Eyrie is a Python package published to PyPI. GitHub template repo may be added later as
an alternative for GitHub-native users, but the CLI is the primary path.

## `eyrie init`

Running `eyrie init <name>` creates a new eyrie directory and asks exactly **one question**:

> Describe your eyrie in one or two sentences (who you are, what this coordinates):

The answer is baked into the generated `AGENTS.md` as the opening description. Everything
else — read-only conventions, `links/` structure, `docs/` layout, workflow pattern — is
boilerplate that Eyrie provides.

No platform selection at init time. The scaffold works for all agent platforms by default.

### What `eyrie init` does (in order)

1. Creates the directory `<name>/`
2. Asks the one description question
3. Generates all scaffold files (AGENTS.md, CLAUDE.md, eyrie.toml, docs/, etc.)
4. Runs `git init`
5. Installs the pre-commit hook (`.git/eyrie-pre-commit.sh` + hook entry)
6. Writes agent permission rules (`opencode.json`, `.claude/settings.json`)
7. Runs `uv init --no-package` to create `pyproject.toml`

The generated `eyrie.toml` starts minimal:

```toml
[eyrie]
name = "<name>"
description = "<user's answer>"
```

Sources are added by the user post-init, then `eyrie sync` materializes them.

## Scaffold structure

```
my-career-eyrie/
├── .agents/
│   └── skills/              ← canonical skills location
├── .claude/
│   ├── skills -> ../.agents/skills   ← symlink (not a real dir)
│   └── settings.json        ← Claude-specific config (optional, created on demand)
├── AGENTS.md                ← primary agent instructions, generated from template + init answer
├── CLAUDE.md                ← contains only "@AGENTS.md" for Claude Code compatibility
├── eyrie.toml               ← eyrie config (sources, skills, MCP servers)
├── docs/
│   ├── domain/
│   │   ├── architecture.md  ← stub, agent fills in over time
│   │   ├── repos.md         ← stub, one entry per repo in links/repos/
│   │   ├── sources.md       ← stub, one entry per source in links/sources/
│   │   ├── glossary.md      ← stub, domain terms
│   │   └── access.md        ← stub, credentials and CLI access patterns
│   ├── topics/              ← empty, agent creates files here as investigations open
│   └── meta/
│       └── workflow.md      ← boilerplate: plan here, execute there rule + feedback loop
├── links/
│   ├── repos/               ← symlinks to git repos
│   └── sources/             ← symlinks to folders, vaults, individual files
├── output/                  ← versioned deliverables (plans, reports, exports)
├── scripts/                 ← eyrie-specific automation: export scripts, report generators,
│                              custom helpers. Versioned and reusable, not ephemeral.
│                              Use uv inline script metadata for per-script dependencies.
├── scratch/                 ← ephemeral work, git-ignored
├── pyproject.toml           ← minimal uv project (name, python version); makes `uv run
│                              scripts/foo.py` work with inline script dependencies
└── .gitignore               ← includes: links/, scratch/, .claude/settings.local.json
```

### Skills folder rationale

`.agents/skills/` is canonical because it is the project-level skills path for OpenCode,
Cursor, Codex, GitHub Copilot, and many other agents (per `vercel-labs/skills` registry).
`.claude/skills/` is Claude Code's path — handled by symlinking it to `.agents/skills/`.
`.claude/` stays a real directory (not a symlink) so Claude-specific files (`settings.json`,
`rules/`) can live there independently.

### `output/` vs `scratch/`

- `output/` — versioned, committed. For point-in-time deliverables: plans sent to
  colleagues, reports, decision docs. Subfolders (e.g. `output/reports/`,
  `output/published/`) are user-created as needed.
- `scratch/` — git-ignored. For ephemeral work: drafts, iteration, large exports,
  anything not meant to be versioned.

## `eyrie.toml`

TOML config file at the eyrie root. Chosen over YAML for: no indentation sensitivity,
no implicit type coercions, `tomllib` in Python stdlib (3.11+, no extra dependency).

### Structure

```toml
[eyrie]
name = "career-eyrie"
description = "Coordinate job search across resume, career notes, and research"
skills = ["vercel-labs/agent-skills/git"]   # eyrie-level skills, always available

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
name = "job-research"
path = "~/Library/CloudStorage/Dropbox/job-search"
type = "folder"

[[sources]]
name = "jira"
type = "remote"
description = "Team Jira (team.atlassian.net)"
skills = ["org/skills/atlassian-cli"]
```

### Source types

| Type | Behavior | Links to |
|------|----------|----------|
| `repo` | symlinked into eyrie | `links/repos/<name>` |
| `folder` | symlinked into eyrie; also used for single files | `links/sources/<name>` |
| `remote` | no symlink; documented in `docs/domain/access.md` by agent | — |

Everything under `links/` is unconditionally read-only — there is no `read_only` flag in
`eyrie.toml`. The git hook (installed at `eyrie init`) enforces this at commit time.
Remote sources are implicitly read-only (no local path to write to).

Obsidian vaults are `type = "folder"` — no special type needed. The `obsidian-cli` skill
is what signals to the agent how to work with them.

## Skills

Skills are declared in `eyrie.toml` at two levels:
- **Eyrie-level** (`[eyrie] skills = [...]`) — always available, not tied to a source
- **Per-source** (`[[sources]] skills = [...]`) — associated with a specific source

### Installation

Eyrie delegates entirely to `npx skills` (the `vercel-labs/skills` CLI). `eyrie sync`
calls `npx skills add` for each declared skill. Three source formats are supported
transparently:

```toml
skills = [
  "vercel-labs/agent-skills/obsidian-cli",   # GitHub shorthand (registry)
  "https://github.com/org/repo/skill-name",  # full GitHub URL
  "./my-local-skills/custom-skill",          # local path
]
```

Eyrie does not reinvent skill installation — it just drives `npx skills`.

Node.js / `npx` is required for skill installation but is **not checked at `eyrie init`
time** — only at `eyrie sync` when skill installation is actually attempted. A missing
Node installation produces a clear warning but does not block eyrie creation.

Skills are installed into `.agents/skills/` (the canonical location). The `.claude/skills`
symlink means Claude Code picks them up automatically.

## CLI commands (implemented)

| Command | Description |
|---------|-------------|
| `eyrie init <name>` | Create scaffold, ask one question, install git hook, write agent permission rules |
| `eyrie add <path>` | Add a source to `eyrie.toml` and auto-sync (infers type, supports `--skill`, `--name`, `--type remote`) |
| `eyrie sync` | Materialize/re-link `links/` from `eyrie.toml` + install/update skills via `npx skills` |

## Agent platform support

| File/folder | Purpose | Platform |
|-------------|---------|----------|
| `AGENTS.md` | Primary instructions | OpenCode, Devin CLI, GitHub Copilot agent |
| `CLAUDE.md` | `@AGENTS.md` bridge | Claude Code |
| `.agents/skills/` | Canonical skills | OpenCode, Cursor, Codex, GitHub Copilot, many others |
| `.claude/skills` | Symlink → `.agents/skills/` | Claude Code |

Cursor does not natively read `AGENTS.md`. A `.cursor/rules/` entry is a future optional
addition, not a default.

## Read-only enforcement

Everything under `links/` is unconditionally read-only. Three layers enforce this:

**Layer 1 — AGENTS.md convention**
Generated at `eyrie init`. The agent understands `links/` is read-only from instructions.
No ongoing maintenance needed.

**Layer 2 — Git pre-commit hook**
Installed at `eyrie init` (not `eyrie sync`). Blocks commits to any file whose resolved
real path falls under `links/`. The hook is pure POSIX sh with no dependencies:

```sh
#!/bin/sh
ROOT=$(git rev-parse --show-toplevel)
LINKS="$ROOT/links"

git diff --cached --name-only | while IFS= read -r staged; do
  staged_real=$(realpath "$ROOT/$staged" 2>/dev/null)
  links_real=$(realpath "$LINKS" 2>/dev/null)
  case "$staged_real" in
    "$links_real"/*)
      echo "Eyrie: blocked commit to read-only source (links/)"
      echo "  file: $staged"
      exit 1
      ;;
  esac
done
```

If the user already has a pre-commit hook, Eyrie appends a one-line call to a separate
`.git/eyrie-pre-commit.sh` rather than overwriting the existing hook.

**Layer 3 — Agent permission rules**
Written once by `eyrie init` (not `eyrie sync`) — the deny target is always `links/**`
regardless of what sources are declared, so it never needs to regenerate.

Eyrie writes deny rules for `links/**` into each supported platform's config:
- **OpenCode**: merges a `permission` block into `opencode.json`
- **Claude Code**: merges a `permissions.deny` block into `.claude/settings.json`

No cross-agent standard exists for permission config (confirmed via research, July 2026).
Eyrie handles the translation — same rule, different formats. The `AGENTS.md` prose
instruction is the fallback for platforms Eyrie doesn't explicitly support.

## Out of scope for v1 (future enhancements)

- **Writable linked sources** — if a use case arises where a linked source needs to be
  writable from the eyrie, a separate sibling folder to `links/` could be introduced.

- **MCP servers** — each agent platform (OpenCode, Claude Code, Cursor) uses a different
  config file and schema for MCP servers. For v1, users configure MCP servers manually
  via their agent tool. A future `eyrie sync` could generate platform-specific MCP config
  from `eyrie.toml`, but the credential handling complexity makes this non-trivial.

- **Eyrie-aware child repos** — an opt-in flag per source (`eyrie_aware = true`) that
  installs a skill + context in the child repo making it aware of the eyrie. Useful for
  personal repos where the one-way link limitation doesn't apply. Not appropriate for
  shared team repos where a hardcoded back-reference would break on other machines.

## AGENTS.md generation

AGENTS.md has three layers with different owners:

**Eyrie generates once at `init`, never touches again:**
- `links/` read-only warning — boilerplate, never changes
- Directory tree — static scaffold description
- Working conventions / workflow rule — boilerplate, same for every eyrie
- `docs/` lifecycle explanation — boilerplate
- Opening description — from the `eyrie init` answer

**Eyrie regenerates on `eyrie sync` (derived from `eyrie.toml`):**
- `docs/domain/repos.md` — one entry skeleton per `type = "repo"` source
- `docs/domain/sources.md` — one entry skeleton per `type = "folder"` source

Sync adds new entry skeletons for sources declared in `eyrie.toml` that don't yet appear
in `repos.md` / `sources.md`. It never removes or overwrites existing entries — the agent
fills in descriptions, notes, etc. over time and those are preserved. Sync only appends.

AGENTS.md is never touched by Eyrie after `init` — no command regenerates or modifies it.
The agent and user are free to edit it over time (refining the description, adding context,
etc.). The layout tree shows fixed scaffold shape only — not a live inventory. Live
inventory lives in `docs/domain/repos.md` and `docs/domain/sources.md`, which sync
maintains. Remote sources are documented in `docs/domain/access.md` by the agent.

**Agent maintains over time:**
- Opening description — starts from init answer, agent refines as eyrie matures
- User context / role — agent updates as circumstances change
- Domain-specific context — agent builds this out in `docs/domain/`; AGENTS.md points there
- Topic docs — agent creates/updates under `docs/topics/` as investigations open and close

The key principle: AGENTS.md is the routing layer, not the knowledge store. Knowledge
lives in `docs/` where the agent maintains it. AGENTS.md stays thin.

`docs/meta/workflow.md` is pure boilerplate — the plan-here-execute-there rule and
feedback loop. Eyrie ships it as a template at `init`. AGENTS.md points to it rather
than duplicating it inline.

## Templates

Boilerplate content Eyrie ships at `init`. Collected here for reference when creating the
Eyrie repo.

### `docs/meta/workflow.md`

```markdown
# Workflow: plan here, execute there

## The rule

**Plan and understand cross-source work from this eyrie. Execute it — edits, commits,
PRs — in the individual source repo or folder.**

This split is structural, not a preference:
- `links/` is read-only by design — there is no path to committing a change to a linked
  source from inside the eyrie.
- Each source owns its own toolchain, CI, and conventions. Working there keeps those
  intact instead of routing around them.
- The eyrie has no way to run, test, or lint code in linked repos — only to read it and
  reason about it alongside docs and other sources.

What the eyrie *is* good for: seeing the whole board before you move a piece. Use it to
work out what a change touches, which sources are affected, what the dependencies are,
and what order things need to happen in — then go make the change in the source itself.

## The link only goes one way

`links/` contains symlinks *from* the eyrie *into* the sources. A session opened directly
in a linked source has no automatic awareness that this eyrie exists.

Don't fix this with a symlink back. If a source is a shared repo other people clone, a
hardcoded reference to this eyrie's path would be dead or wrong on every other machine.

Two mechanisms instead:
- **Carry context in, don't link it in.** When starting work in a source, point the agent
  at the relevant eyrie doc by absolute path, or paste the relevant section in.
- **Promote what's durable into the source's own docs.** If something in a topic doc
  settles and matters to anyone working in that source, it belongs in that source's own
  docs — not just referenced remotely from the eyrie.

## Keeping cross-source awareness in sync

Three tiers, matched to how settled the knowledge is:

1. **`docs/domain/architecture.md`** — the enduring big picture. Update only when the
   high-level map itself changes, not for details of an active investigation.

2. **A topic doc per active cross-source question in `docs/topics/`.** Active, evolving,
   eventually resolved or archived. Each file should have: a scope line (which sources,
   what question), a status line, the current state, a decision once made, and a plan
   updated as work lands.

3. **A contract map** — only once concrete cross-source contracts exist worth tracking
   as their own thing. Start light; grow only when a cross-source change needs it.

## The feedback loop

A topic doc isn't a one-time plan — it's a live record. When eyrie-planned work lands in
a source, note it back in the doc that tracked the plan, with enough detail to find it
later. Without that step, the doc goes stale the moment work starts.
```

### `docs/domain/architecture.md` stub

```markdown
# Architecture

*Stub — fill in as you learn how your sources fit together.*

## Sources

<!-- One paragraph per major source: what it is, what it owns, how it relates to others -->

## How they connect

<!-- Data flows, dependencies, contracts between sources -->
```

### AGENTS.md template

The full AGENTS.md template will live in the Eyrie repo rendered at `init` time (Jinja2
or similar). The static boilerplate sections are captured above in "AGENTS.md generation".
The only instance-specific section filled at init is the opening description (from the
`eyrie init` answer).

The template references all domain stubs so the agent knows they exist and how to use them:

```markdown
# AGENTS.md

This is **{{ eyrie.name }}**. {{ eyrie.description }}

This eyrie holds almost no content of its own. Its value is the **`links/`** tree
(symlinks to the real sources) plus the curated **`docs/`** that describe them.

## ⚠️ `links/` is READ-ONLY

Everything under `links/` is **read-only**. Read it freely; **never create, edit, move,
or delete anything inside `links/`**. When a task seems to need a change under `links/`,
propose it and ask first.

`links/` is git-ignored (machine-local symlinks). Do the eyrie's own writing — docs,
notes, reports — in this repo's tracked files, outside `links/`.

## Layout

\```
{{ eyrie.name }}/
├── AGENTS.md          ← you are here
├── CLAUDE.md          ← points here
├── docs/
│   ├── domain/        ← stable reference: see architecture.md, repos.md, sources.md
│   ├── meta/          ← about this eyrie: see workflow.md
│   └── topics/        ← active cross-source investigations
├── output/            ← versioned deliverables, date-prefixed (YYYY-MM-DD-name)
├── scripts/           ← eyrie-specific automation (uv run scripts/foo.py)
├── scratch/           ← ephemeral work, git-ignored
└── links/             ← READ-ONLY symlinks (git-ignored)
    ├── repos/         ← see docs/domain/repos.md
    └── sources/       ← see docs/domain/sources.md
\```

## Where to look first

- **"How does X work / how do these connect?"** → `docs/domain/architecture.md`, then
  `docs/domain/repos.md` or `docs/domain/sources.md` for the relevant source.
- **"What is <term>?"** → `docs/domain/glossary.md`.
- **"How do I access <remote source>?"** → `docs/domain/access.md`.
- **Active cross-source questions and plans** → `docs/topics/` — one file per investigation.
- **Workflow and conventions** → `docs/meta/workflow.md` — read this before planning
  any cross-source work.

`docs/` is split by **lifecycle**, not just topic: `domain/` is stable reference about
your sources and domain (changes rarely); `meta/` is about this eyrie as a tool; `topics/`
is active, evolving investigations — resolved or archived once settled. When you learn
something durable, add it to the right `docs/domain/` file rather than leaving it in chat.

## Working conventions

- Treat `docs/` as persistent memory: consult it for background mid-task, not just at
  the start. Prefer updating a `docs/` file over letting knowledge evaporate into chat.
- When you learn something durable, add it to the right `docs/domain/` file.
- For cross-source work, follow the pattern in `docs/meta/workflow.md`: plan here,
  execute in the source, note results back in the topic doc.
- `output/` is for versioned deliverables sent to others — frozen when sent, never
  treat as current state. Use date-prefix filenames (YYYY-MM-DD-name).
- Facts in these docs reflect a point in time. Verify against live sources before
  acting on specifics — docs describe the shape of things; live sources hold current state.
```

### `docs/domain/repos.md` stub

```markdown
# Repos

*One entry per git repository linked under `links/repos/`. Fill in as you add repos.*

<!-- Template per entry:
## <name>
- **Path:** `links/repos/<name>`
- **What it is:** one sentence
- **Language / stack:** key technologies
- **What it owns:** responsibilities, key outputs
- **Main branch:** e.g. `main`
- **Notes:** anything an agent needs to know about working with it
-->
```

### `docs/domain/sources.md` stub

```markdown
# Sources

*One entry per source linked under `links/`. Fill in as you add sources.*

<!-- Template per entry:
## <name>
- **Path:** `links/sources/<name>`
- **What it is:** one sentence
- **What it owns:** key content, responsibilities
- **Notes:** anything an agent needs to know about working with it
-->
```

### `docs/domain/glossary.md` stub

```markdown
# Glossary

*Domain terms and definitions. Add entries as you encounter terms that need explanation.*

<!-- Template per entry:
**<Term>** — definition. Context or usage notes if needed.
-->
```

### `docs/domain/access.md` stub

```markdown
# Access

*Credentials, CLI tools, and access patterns for remote sources and live data.*

<!-- For each remote source or data system, document:
- What CLI tool or method to use
- Auth setup (how to authenticate, where credentials live)
- Key commands / query patterns
- Gotchas and known issues
-->
```

## Open questions (for future versions)

- **Windows support** — symlinks require developer mode or admin rights on Windows.
  Eyrie v1 targets macOS and Linux only. Windows support would require either an
  alternative to symlinks (junctions, copies) or a compatibility layer.
- **Additional agent platform support** — Cursor doesn't read `AGENTS.md`; a minimal
  `.cursor/rules/eyrie.mdc` pointing to `AGENTS.md` would bridge this. Windsurf, Codex,
  and others similarly could benefit from platform-specific bridge files generated at
  `init`. For v1, OpenCode and Claude Code only.
