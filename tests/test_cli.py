from __future__ import annotations

from pathlib import Path
from typing import Optional

from codex_builder.cli import main


def test_cli_generates_with_options_only(tmp_path):
    result = main(
        [
            "--target-dir",
            str(tmp_path),
            "--name",
            "sample-api",
            "--stack",
            "fastapi",
            "--db",
            "mysql",
            "--auth",
            "yes",
            "--external-api",
            "yes",
            "--docs",
            "strict",
        ]
    )

    assert result == 0
    assert (tmp_path / ".codex" / "AI_RULE_DEVELOPER" / "GLOBAL_RULES.md").exists()


def test_cli_no_args_runs_interactive_flow(tmp_path, monkeypatch):
    answers = iter(
        [
            "sample-api",
            "Sample description",
            "fastapi",
            "n",
            "n",
            "n",
            "standard",
            "ko",
            str(tmp_path),
            "y",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    result = main([])

    assert result == 0
    assert (tmp_path / ".codex" / "codex_start_prompt.txt").exists()


def test_cli_prompt_completes_missing_values(tmp_path, monkeypatch):
    answers = iter(
        [
            "Prompt description",
            "fastapi,react",
            "y",
            "mysql",
            "y",
            "n",
            "strict",
            "ko",
            "y",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    result = main(["--target-dir", str(tmp_path), "--name", "prompt-api"])

    assert result == 0
    overview = (tmp_path / ".codex" / "REF_DOCS" / "PROJECT_OVERVIEW.md").read_text(encoding="utf-8")
    assert "prompt-api" in overview
    assert "Prompt description" in overview
    assert "FastAPI, React" in overview


def test_cli_interactive_with_options_shows_final_confirmation(tmp_path, monkeypatch):
    answers = iter(["y"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    args = _full_option_args(tmp_path, extra=["--description", "Configured by options", "--language", "ko", "--interactive"])
    result = main(args)

    assert result == 0
    overview = (tmp_path / ".codex" / "REF_DOCS" / "PROJECT_OVERVIEW.md").read_text(encoding="utf-8")
    assert "Configured by options" in overview


def test_cli_reprompts_invalid_stack_value(tmp_path, monkeypatch):
    answers = iter(
        [
            "Prompt description",
            "bad-stack",
            "nextjs",
            "n",
            "n",
            "n",
            "standard",
            "ko",
            "y",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    result = main(["--target-dir", str(tmp_path), "--name", "prompt-api"])

    assert result == 0
    framework_rules = (tmp_path / ".codex" / "AI_RULE_DEVELOPER" / "FRAMEWORK_RULES.md").read_text(encoding="utf-8")
    assert "Next.js" in framework_rules


def test_cli_rejects_invalid_stack_option(tmp_path):
    result = main(
        [
            "--target-dir",
            str(tmp_path),
            "--name",
            "sample-api",
            "--stack",
            "bad-stack",
            "--auth",
            "no",
            "--external-api",
            "no",
            "--docs",
            "standard",
        ]
    )

    assert result == 1
    assert not (tmp_path / ".codex").exists()


def test_cli_rejects_invalid_docs_level_option(tmp_path):
    result = main(
        [
            "--target-dir",
            str(tmp_path),
            "--name",
            "sample-api",
            "--stack",
            "fastapi",
            "--auth",
            "no",
            "--external-api",
            "no",
            "--docs",
            "heavy",
        ]
    )

    assert result == 1
    assert not (tmp_path / ".codex").exists()


def test_cli_rejects_invalid_language_option(tmp_path):
    result = main(
        [
            "--target-dir",
            str(tmp_path),
            "--name",
            "sample-api",
            "--stack",
            "fastapi",
            "--auth",
            "no",
            "--external-api",
            "no",
            "--docs",
            "standard",
            "--language",
            "jp",
        ]
    )

    assert result == 1
    assert not (tmp_path / ".codex").exists()


def test_cli_existing_codex_prompt_abort_keeps_folder(tmp_path, monkeypatch):
    existing = tmp_path / ".codex"
    existing.mkdir()
    (existing / "old.txt").write_text("old", encoding="utf-8")
    monkeypatch.setattr("builtins.input", lambda _: "1")

    result = main(
        [
            "--target-dir",
            str(tmp_path),
            "--name",
            "sample-api",
            "--stack",
            "fastapi",
            "--auth",
            "no",
            "--external-api",
            "no",
            "--docs",
            "standard",
        ]
    )

    assert result == 0
    assert (existing / "old.txt").read_text(encoding="utf-8") == "old"
    assert not (existing / "AI_RULE_DEVELOPER").exists()


def test_cli_force_backs_up_existing_codex(tmp_path):
    existing = tmp_path / ".codex"
    existing.mkdir()
    (existing / "old.txt").write_text("old", encoding="utf-8")

    result = main(_full_option_args(tmp_path, extra=["--force"]))

    assert result == 0
    backups = list(tmp_path.glob(".codex_backup_*"))
    assert len(backups) == 1
    assert (backups[0] / "old.txt").read_text(encoding="utf-8") == "old"
    assert (tmp_path / ".codex" / "AI_RULE_DEVELOPER" / "GLOBAL_RULES.md").exists()


def test_cli_force_overwrite_deletes_existing_codex(tmp_path):
    existing = tmp_path / ".codex"
    existing.mkdir()
    (existing / "old.txt").write_text("old", encoding="utf-8")

    result = main(_full_option_args(tmp_path, extra=["--force", "--overwrite"]))

    assert result == 0
    assert not list(tmp_path.glob(".codex_backup_*"))
    assert not (tmp_path / ".codex" / "old.txt").exists()
    assert (tmp_path / ".codex" / "AI_RULE_DEVELOPER" / "GLOBAL_RULES.md").exists()


def _full_option_args(target_dir: Path, *, extra: Optional[list[str]] = None) -> list[str]:
    args = [
        "--target-dir",
        str(target_dir),
        "--name",
        "sample-api",
        "--stack",
        "fastapi",
        "--db",
        "mysql",
        "--auth",
        "yes",
        "--external-api",
        "yes",
        "--docs",
        "strict",
    ]
    if extra:
        args.extend(extra)
    return args
