"""Template content for scaffold generation."""

WORKFLOW_MD = """\
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
"""

ARCHITECTURE_MD = """\
# Architecture

*Stub — fill in as you learn how your sources fit together.*

## Sources

<!-- One paragraph per major source: what it is, what it owns, how it relates to others -->

## How they connect

<!-- Data flows, dependencies, contracts between sources -->
"""

REPOS_MD = """\
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
"""

SOURCES_MD = """\
# Sources

*One entry per source linked under `links/`. Fill in as you add sources.*

<!-- Template per entry:
## <name>
- **Path:** `links/sources/<name>`
- **What it is:** one sentence
- **What it owns:** key content, responsibilities
- **Notes:** anything an agent needs to know about working with it
-->
"""

GLOSSARY_MD = """\
# Glossary

*Domain terms and definitions. Add entries as you encounter terms that need explanation.*

<!-- Template per entry:
**<Term>** — definition. Context or usage notes if needed.
-->
"""

ACCESS_MD = """\
# Access

*Credentials, CLI tools, and access patterns for remote sources and live data.*

<!-- For each remote source or data system, document:
- What CLI tool or method to use
- Auth setup (how to authenticate, where credentials live)
- Key commands / query patterns
- Gotchas and known issues
-->
"""

GITIGNORE = """\
links/
scratch/
.claude/settings.local.json
.venv/
__pycache__/
"""

CLAUDE_MD = """\
@AGENTS.md
"""


def agents_md(name: str, description: str) -> str:
    return f"""\
# AGENTS.md

This is **{name}**. {description}

This eyrie holds almost no content of its own. Its value is the **`links/`** tree
(symlinks to the real sources) plus the curated **`docs/`** that describe them.

## `links/` is READ-ONLY

Everything under `links/` is **read-only**. Read it freely; **never create, edit, move,
or delete anything inside `links/`**. When a task seems to need a change under `links/`,
propose it and ask first.

`links/` is git-ignored (machine-local symlinks). Do the eyrie's own writing — docs,
notes, reports — in this repo's tracked files, outside `links/`.

## Layout

```
{name}/
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
```

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
"""


def eyrie_toml(name: str, description: str) -> str:
    return f"""\
[eyrie]
name = "{name}"
description = "{description}"
"""
