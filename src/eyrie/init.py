"""Scaffold generation for eyrie init."""

import json
import subprocess
from pathlib import Path

from eyrie import templates


PRE_COMMIT_HOOK = """\
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
"""


def create_scaffold(target: Path, name: str, description: str) -> None:
    """Create the full eyrie directory structure and files."""
    target.mkdir(parents=True, exist_ok=False)

    # Directories
    (target / "docs" / "domain").mkdir(parents=True)
    (target / "docs" / "meta").mkdir(parents=True)
    (target / "docs" / "topics").mkdir(parents=True)
    (target / "links" / "repos").mkdir(parents=True)
    (target / "links" / "sources").mkdir(parents=True)
    (target / "output").mkdir()
    (target / "scripts").mkdir()
    (target / "scratch").mkdir()
    (target / ".agents" / "skills").mkdir(parents=True)
    (target / ".claude").mkdir()

    # Symlink .claude/skills -> ../.agents/skills
    (target / ".claude" / "skills").symlink_to(Path("..", ".agents", "skills"))

    # Top-level files
    (target / "AGENTS.md").write_text(templates.agents_md(name, description))
    (target / "CLAUDE.md").write_text(templates.CLAUDE_MD)
    (target / "eyrie.toml").write_text(templates.eyrie_toml(name, description))
    (target / ".gitignore").write_text(templates.GITIGNORE)

    # docs/domain/
    (target / "docs" / "domain" / "architecture.md").write_text(templates.ARCHITECTURE_MD)
    (target / "docs" / "domain" / "repos.md").write_text(templates.REPOS_MD)
    (target / "docs" / "domain" / "sources.md").write_text(templates.SOURCES_MD)
    (target / "docs" / "domain" / "glossary.md").write_text(templates.GLOSSARY_MD)
    (target / "docs" / "domain" / "access.md").write_text(templates.ACCESS_MD)

    # docs/meta/
    (target / "docs" / "meta" / "workflow.md").write_text(templates.WORKFLOW_MD)

    # Keep empty dirs in git
    (target / "docs" / "topics" / ".gitkeep").touch()
    (target / "output" / ".gitkeep").touch()
    (target / "scripts" / ".gitkeep").touch()
    (target / "scratch" / ".gitkeep").touch()

    # Git init
    subprocess.run(["git", "init"], cwd=target, check=True, capture_output=True)

    # Pre-commit hook
    hooks_dir = target / ".git" / "hooks"
    hook_script = target / ".git" / "eyrie-pre-commit.sh"
    hook_script.write_text(PRE_COMMIT_HOOK)
    hook_script.chmod(0o755)

    pre_commit = hooks_dir / "pre-commit"
    hook_call = '"$(git rev-parse --show-toplevel)/.git/eyrie-pre-commit.sh"'
    if pre_commit.exists():
        content = pre_commit.read_text()
        if hook_call not in content:
            with pre_commit.open("a") as f:
                f.write(f"\n{hook_call}\n")
    else:
        pre_commit.write_text(f"#!/bin/sh\nexec {hook_call}\n")
        pre_commit.chmod(0o755)

    # Agent permission rules
    _write_opencode_permissions(target)
    _write_claude_permissions(target)

    # Create pyproject.toml for uv script support
    subprocess.run(
        ["uv", "init", "--no-package"],
        cwd=target,
        check=True,
        capture_output=True,
    )


def _write_opencode_permissions(target: Path) -> None:
    """Write opencode.json with deny rules for links/."""
    config = {
        "$schema": "https://opencode.ai/config.json",
        "permission": {
            "edit": {
                "links/**": "deny",
            },
            "bash": {
                "rm links/**": "deny",
                "mv links/**": "deny",
            },
        },
    }
    (target / "opencode.json").write_text(json.dumps(config, indent=2) + "\n")


def _write_claude_permissions(target: Path) -> None:
    """Write .claude/settings.json with deny rules for links/."""
    config = {
        "permissions": {
            "deny": [
                "Edit links/**",
                "Write links/**",
                "Bash rm links/**",
                "Bash mv links/**",
            ]
        }
    }
    (target / ".claude" / "settings.json").write_text(
        json.dumps(config, indent=2) + "\n"
    )
