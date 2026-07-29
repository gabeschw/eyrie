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

This is **{name}**, an eyrie — a meta-repo with symlinks (`links/`) to real sources and curated `docs/` about them. It holds almost no code of its own.

{description}

## `links/` is READ-ONLY

Never create, edit, move, or delete anything inside `links/`. It is git-ignored (machine-local symlinks). If a task needs a change there, propose it and ask first.

Both `opencode.json` and `.claude/settings.json` enforce this — edits and destructive bash under `links/**` are denied.

## Layout

```
{name}/
├── docs/
│   ├── domain/
│   │   ├── architecture.md  ← how sources fit together
│   │   ├── repos.md         ← one entry per linked repo
│   │   ├── sources.md       ← one entry per linked source
│   │   ├── glossary.md      ← domain terms
│   │   └── access.md        ← credentials and CLI access for remote sources
│   ├── meta/
│   │   └── workflow.md      ← plan-here-execute-there pattern
│   └── topics/              ← active cross-source investigations
├── links/                   ← READ-ONLY symlinks (git-ignored)
│   ├── repos/
│   └── sources/
├── output/                  ← frozen deliverables, date-prefixed (YYYY-MM-DD-name)
├── scripts/                 ← eyrie automation (uv run scripts/foo.py)
└── scratch/                 ← ephemeral work, git-ignored
```

`docs/` is split by lifecycle: `domain/` changes rarely (stable facts about your sources); `topics/` is active and evolving — resolved or archived once settled; `meta/` describes how the eyrie itself works.

Where to look:
- "How does X work / how do these connect?" → `docs/domain/architecture.md`
- "What is <term>?" → `docs/domain/glossary.md`
- "How do I access <remote system>?" → `docs/domain/access.md`
- Details on a specific source → `docs/domain/repos.md` or `docs/domain/sources.md`
- Active plans and investigations → `docs/topics/`

## How to work

- **Plan here, execute in the source.** The eyrie cannot run, test, or lint code in linked repos — only read it. Work out what to change and in what order, then make the change in the source directly. See `docs/meta/workflow.md` for the full pattern.
- **Treat `docs/` as persistent memory.** Consult it mid-task. When you learn something durable, update `docs/domain/` rather than letting knowledge evaporate.
- **All domain docs are stubs.** If you encounter a source or term that lacks an entry, fill it in.
- **`output/` is frozen on delivery.** Date-prefix filenames (`YYYY-MM-DD-name`). Never treat as current state.
- **When docs conflict with live sources, trust the source.** Docs describe the shape of things; live sources hold current state.
"""


def eyrie_toml(name: str, description: str) -> str:
    return f"""\
[eyrie]
name = "{name}"
description = "{description}"
"""
