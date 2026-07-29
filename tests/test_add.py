"""Tests for eyrie add."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from eyrie.cli import main


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def eyrie_repo(tmp_path, runner, monkeypatch):
    """Create an eyrie and chdir into it."""
    target = tmp_path / "my-eyrie"
    result = runner.invoke(main, ["init", str(target)], input="A test eyrie\n")
    assert result.exit_code == 0, result.output
    monkeypatch.chdir(target)
    return target


class TestAddRepo:
    def test_adds_repo_source(self, eyrie_repo, tmp_path, runner):
        repo = tmp_path / "my-repo"
        repo.mkdir()
        (repo / ".git").mkdir()
        result = runner.invoke(main, ["add", str(repo)], catch_exceptions=False)
        assert result.exit_code == 0, result.output
        assert "Added source: my-repo" in result.output
        toml = (eyrie_repo / "eyrie.toml").read_text()
        assert 'name = "my-repo"' in toml
        assert 'type = "repo"' in toml

    def test_infers_repo_type_from_git(self, eyrie_repo, tmp_path, runner):
        repo = tmp_path / "has-git"
        repo.mkdir()
        (repo / ".git").mkdir()
        runner.invoke(main, ["add", str(repo)], catch_exceptions=False)
        toml = (eyrie_repo / "eyrie.toml").read_text()
        assert 'type = "repo"' in toml

    def test_infers_folder_type_without_git(self, eyrie_repo, tmp_path, runner):
        folder = tmp_path / "notes"
        folder.mkdir()
        runner.invoke(main, ["add", str(folder)], catch_exceptions=False)
        toml = (eyrie_repo / "eyrie.toml").read_text()
        assert 'type = "folder"' in toml

    def test_custom_name(self, eyrie_repo, tmp_path, runner):
        folder = tmp_path / "some-long-name"
        folder.mkdir()
        runner.invoke(
            main, ["add", str(folder), "--name", "short"], catch_exceptions=False
        )
        toml = (eyrie_repo / "eyrie.toml").read_text()
        assert 'name = "short"' in toml

    def test_creates_symlink(self, eyrie_repo, tmp_path, runner):
        folder = tmp_path / "notes"
        folder.mkdir()
        runner.invoke(main, ["add", str(folder)], catch_exceptions=False)
        link = eyrie_repo / "links" / "sources" / "notes"
        assert link.is_symlink()


class TestAddRemote:
    def test_adds_remote_source(self, eyrie_repo, runner):
        result = runner.invoke(
            main,
            ["add", "--type", "remote", "--name", "jira", "-d", "Team Jira"],
            catch_exceptions=False,
        )
        assert result.exit_code == 0, result.output
        toml = (eyrie_repo / "eyrie.toml").read_text()
        assert 'name = "jira"' in toml
        assert 'type = "remote"' in toml
        assert 'description = "Team Jira"' in toml

    def test_remote_requires_name(self, eyrie_repo, runner):
        result = runner.invoke(main, ["add", "--type", "remote"])
        assert result.exit_code != 0


class TestAddSkills:
    def test_attaches_skills(self, eyrie_repo, tmp_path, runner):
        folder = tmp_path / "vault"
        folder.mkdir()
        runner.invoke(
            main,
            ["add", str(folder), "-s", "vercel-labs/agent-skills/obsidian-cli"],
            catch_exceptions=False,
        )
        toml = (eyrie_repo / "eyrie.toml").read_text()
        assert "obsidian-cli" in toml


class TestAddErrors:
    def test_duplicate_name_fails(self, eyrie_repo, tmp_path, runner):
        folder = tmp_path / "notes"
        folder.mkdir()
        runner.invoke(main, ["add", str(folder)], catch_exceptions=False)
        result = runner.invoke(main, ["add", str(folder)])
        assert result.exit_code != 0
        assert "already exists" in result.output

    def test_missing_path_fails(self, eyrie_repo, runner):
        result = runner.invoke(main, ["add", "/nonexistent/path"])
        assert result.exit_code != 0
        assert "does not exist" in result.output
