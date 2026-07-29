"""Tests for eyrie init."""

import json
import os

import pytest
from click.testing import CliRunner

from eyrie.cli import main


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def eyrie_repo(tmp_path, runner):
    """Create an eyrie and return its path."""
    target = tmp_path / "my-eyrie"
    result = runner.invoke(main, ["init", str(target)], input="A test eyrie\n")
    assert result.exit_code == 0, result.output
    return target


class TestScaffoldStructure:
    def test_creates_directory(self, eyrie_repo):
        assert eyrie_repo.is_dir()

    def test_top_level_files(self, eyrie_repo):
        assert (eyrie_repo / "AGENTS.md").is_file()
        assert (eyrie_repo / "CLAUDE.md").is_file()
        assert (eyrie_repo / "eyrie.toml").is_file()
        assert (eyrie_repo / ".gitignore").is_file()
        assert (eyrie_repo / "opencode.json").is_file()

    def test_docs_structure(self, eyrie_repo):
        assert (eyrie_repo / "docs" / "domain" / "architecture.md").is_file()
        assert (eyrie_repo / "docs" / "domain" / "repos.md").is_file()
        assert (eyrie_repo / "docs" / "domain" / "sources.md").is_file()
        assert (eyrie_repo / "docs" / "domain" / "glossary.md").is_file()
        assert (eyrie_repo / "docs" / "domain" / "access.md").is_file()
        assert (eyrie_repo / "docs" / "meta" / "workflow.md").is_file()
        assert (eyrie_repo / "docs" / "topics").is_dir()

    def test_other_dirs(self, eyrie_repo):
        assert (eyrie_repo / "links" / "repos").is_dir()
        assert (eyrie_repo / "links" / "sources").is_dir()
        assert (eyrie_repo / "output").is_dir()
        assert (eyrie_repo / "scripts").is_dir()
        assert (eyrie_repo / "scratch").is_dir()

    def test_skills_symlink(self, eyrie_repo):
        link = eyrie_repo / ".claude" / "skills"
        assert link.is_symlink()
        assert link.resolve() == (eyrie_repo / ".agents" / "skills").resolve()


class TestAgentsMd:
    def test_contains_name(self, eyrie_repo):
        content = (eyrie_repo / "AGENTS.md").read_text()
        assert "**my-eyrie**" in content

    def test_contains_description(self, eyrie_repo):
        content = (eyrie_repo / "AGENTS.md").read_text()
        assert "A test eyrie" in content

    def test_read_only_warning(self, eyrie_repo):
        content = (eyrie_repo / "AGENTS.md").read_text()
        assert "READ-ONLY" in content

    def test_explains_what_eyrie_is(self, eyrie_repo):
        content = (eyrie_repo / "AGENTS.md").read_text()
        assert "meta-repo" in content


class TestEyrieToml:
    def test_contains_name_and_description(self, eyrie_repo):
        content = (eyrie_repo / "eyrie.toml").read_text()
        assert 'name = "my-eyrie"' in content
        assert 'description = "A test eyrie"' in content


class TestGitInit:
    def test_git_repo_created(self, eyrie_repo):
        assert (eyrie_repo / ".git").is_dir()

    def test_pre_commit_hook_exists(self, eyrie_repo):
        hook = eyrie_repo / ".git" / "hooks" / "pre-commit"
        assert hook.is_file()
        assert os.access(hook, os.X_OK)

    def test_eyrie_hook_script_exists(self, eyrie_repo):
        script = eyrie_repo / ".git" / "eyrie-pre-commit.sh"
        assert script.is_file()
        assert os.access(script, os.X_OK)
        content = script.read_text()
        assert "links" in content

    def test_pre_commit_calls_eyrie_script(self, eyrie_repo):
        content = (eyrie_repo / ".git" / "hooks" / "pre-commit").read_text()
        assert "eyrie-pre-commit.sh" in content


class TestPermissions:
    def test_opencode_denies_edit_links(self, eyrie_repo):
        config = json.loads((eyrie_repo / "opencode.json").read_text())
        assert config["permission"]["edit"]["links/**"] == "deny"

    def test_claude_denies_links(self, eyrie_repo):
        config = json.loads((eyrie_repo / ".claude" / "settings.json").read_text())
        deny = config["permissions"]["deny"]
        assert any("links/**" in rule for rule in deny)


class TestUvInit:
    def test_pyproject_toml_created(self, eyrie_repo):
        assert (eyrie_repo / "pyproject.toml").is_file()
        content = (eyrie_repo / "pyproject.toml").read_text()
        assert "[project]" in content


class TestErrorCases:
    def test_existing_directory_fails(self, tmp_path, runner):
        target = tmp_path / "existing"
        target.mkdir()
        result = runner.invoke(main, ["init", str(target)], input="desc\n")
        assert result.exit_code != 0
        assert "already exists" in result.output
