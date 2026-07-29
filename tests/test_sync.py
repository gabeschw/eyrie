"""Tests for eyrie sync."""

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from eyrie.cli import main


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def eyrie_repo(tmp_path, runner, monkeypatch):
    """Create an eyrie with sources declared in eyrie.toml."""
    target = tmp_path / "my-eyrie"
    result = runner.invoke(main, ["init", str(target)], input="A test eyrie\n")
    assert result.exit_code == 0, result.output

    # Create fake source directories
    (tmp_path / "repo-a").mkdir()
    (tmp_path / "notes").mkdir()

    # Add sources to eyrie.toml
    toml_content = (target / "eyrie.toml").read_text()
    toml_content += f"""
[[sources]]
name = "repo-a"
path = "{tmp_path / 'repo-a'}"
type = "repo"

[[sources]]
name = "notes"
path = "{tmp_path / 'notes'}"
type = "folder"

[[sources]]
name = "jira"
type = "remote"
description = "Team Jira"
"""
    (target / "eyrie.toml").write_text(toml_content)
    monkeypatch.chdir(target)
    return target


class TestSyncLinks:
    def test_creates_repo_symlink(self, eyrie_repo, runner):
        result = runner.invoke(main, ["sync"], catch_exceptions=False)
        assert result.exit_code == 0, result.output
        link = eyrie_repo / "links" / "repos" / "repo-a"
        assert link.is_symlink()

    def test_creates_folder_symlink(self, eyrie_repo, runner):
        result = runner.invoke(main, ["sync"], catch_exceptions=False)
        assert result.exit_code == 0, result.output
        link = eyrie_repo / "links" / "sources" / "notes"
        assert link.is_symlink()

    def test_skips_remote(self, eyrie_repo, runner):
        result = runner.invoke(main, ["sync"], catch_exceptions=False)
        assert "jira: remote" in result.output

    def test_idempotent(self, eyrie_repo, runner):
        runner.invoke(main, ["sync"], catch_exceptions=False)
        result = runner.invoke(main, ["sync"], catch_exceptions=False)
        assert "already linked" in result.output

    def test_warns_missing_path(self, eyrie_repo, runner):
        toml_content = (eyrie_repo / "eyrie.toml").read_text()
        toml_content += """
[[sources]]
name = "gone"
path = "/nonexistent/path"
type = "folder"
"""
        (eyrie_repo / "eyrie.toml").write_text(toml_content)
        result = runner.invoke(main, ["sync"], catch_exceptions=False)
        assert "WARNING" in result.output
        assert "gone" in result.output


class TestSyncDocs:
    def test_appends_repo_skeleton(self, eyrie_repo, runner):
        runner.invoke(main, ["sync"], catch_exceptions=False)
        content = (eyrie_repo / "docs" / "domain" / "repos.md").read_text()
        assert "## repo-a" in content
        assert "links/repos/repo-a" in content

    def test_appends_source_skeleton(self, eyrie_repo, runner):
        runner.invoke(main, ["sync"], catch_exceptions=False)
        content = (eyrie_repo / "docs" / "domain" / "sources.md").read_text()
        assert "## notes" in content
        assert "links/sources/notes" in content

    def test_skips_remote(self, eyrie_repo, runner):
        runner.invoke(main, ["sync"], catch_exceptions=False)
        repos = (eyrie_repo / "docs" / "domain" / "repos.md").read_text()
        sources = (eyrie_repo / "docs" / "domain" / "sources.md").read_text()
        assert "jira" not in repos
        assert "jira" not in sources

    def test_does_not_duplicate(self, eyrie_repo, runner):
        runner.invoke(main, ["sync"], catch_exceptions=False)
        runner.invoke(main, ["sync"], catch_exceptions=False)
        content = (eyrie_repo / "docs" / "domain" / "repos.md").read_text()
        assert content.count("## repo-a") == 1


class TestSyncSkills:
    def test_no_skills_declared(self, eyrie_repo, runner):
        result = runner.invoke(main, ["sync"], catch_exceptions=False)
        assert "No skills declared" in result.output

    def test_warns_no_npx(self, eyrie_repo, runner):
        toml_content = (eyrie_repo / "eyrie.toml").read_text()
        toml_content = toml_content.replace(
            '[eyrie]', '[eyrie]\nskills = ["vercel-labs/agent-skills/git"]'
        )
        (eyrie_repo / "eyrie.toml").write_text(toml_content)

        with patch("eyrie.sync.shutil.which", return_value=None):
            result = runner.invoke(main, ["sync"], catch_exceptions=False)
            assert "npx not found" in result.output


class TestFindEyrieRoot:
    def test_finds_root_from_subdirectory(self, eyrie_repo, monkeypatch):
        from eyrie.sync import find_eyrie_root

        monkeypatch.chdir(eyrie_repo / "docs" / "domain")
        root = find_eyrie_root()
        assert root == eyrie_repo
