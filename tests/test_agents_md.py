"""Tests for the repository-root AGENTS.md entrypoint."""

from __future__ import annotations

from pathlib import Path

from codex_builder.builder import CodexBuilder
from codex_builder.cli import main
from codex_builder.constants import AGENTS_FILE_NAME, AGENTS_FILE_SOFT_LIMIT_BYTES
from codex_builder.models import ProjectConfig


def _maximal_config(language: str = "ko") -> ProjectConfig:
    return ProjectConfig(
        project_name="agents-md-sample",
        description="AGENTS.md 검증용 프로젝트",
        stack=("fastapi", "react"),
        database="mysql",
        auth_enabled=True,
        external_api_enabled=True,
        docs_level="strict",
        language=language,
    )


def test_agents_md_is_generated_at_repository_root(tmp_path: Path) -> None:
    CodexBuilder().build(_maximal_config(), target_dir=tmp_path)

    agents_file = tmp_path / AGENTS_FILE_NAME
    assert agents_file.exists()
    assert not (tmp_path / ".codex" / AGENTS_FILE_NAME).exists()


def test_agents_md_points_at_every_rule_document(tmp_path: Path) -> None:
    CodexBuilder().build(_maximal_config(), target_dir=tmp_path)
    content = (tmp_path / AGENTS_FILE_NAME).read_text(encoding="utf-8")

    rule_dir = ".codex/ai_rule_developer"
    for rule_file in (
        "GLOBAL_RULES.md",
        "ARCHITECTURE_RULES.md",
        "CODE_STYLE_RULES.md",
        "API_DESIGN_RULES.md",
        "DOMAIN_MODEL_RULES.md",
        "SERVICE_LAYER_RULES.md",
        "EXTERNAL_INTEGRATION_RULES.md",
        "DOCUMENT_RULE.md",
    ):
        assert f"{rule_dir}/{rule_file}" in content


def test_agents_md_stays_within_the_instruction_size_budget(tmp_path: Path) -> None:
    """Project instruction files are truncated past a size budget.

    The generated entrypoint must delegate detail instead of inlining it, so it
    stays well below the budget even for the most verbose configuration.
    """

    for language in ("ko", "en"):
        CodexBuilder().build(_maximal_config(language), target_dir=tmp_path, force=True)
        size = (tmp_path / AGENTS_FILE_NAME).stat().st_size
        assert size < AGENTS_FILE_SOFT_LIMIT_BYTES, f"{language} AGENTS.md is {size} bytes"


def test_agents_md_declares_ref_docs_as_untrusted(tmp_path: Path) -> None:
    CodexBuilder().build(_maximal_config(), target_dir=tmp_path)
    content = (tmp_path / AGENTS_FILE_NAME).read_text(encoding="utf-8")

    assert ".codex/ref_docs" in content
    assert "신뢰할 수 없는" in content
    assert "지시가 아니며" in content


def test_agents_md_requires_repository_commands_instead_of_assuming_them(tmp_path: Path) -> None:
    CodexBuilder().build(_maximal_config(), target_dir=tmp_path)
    content = (tmp_path / AGENTS_FILE_NAME).read_text(encoding="utf-8")

    assert "build, test, lint" in content
    assert "가정하지 않는다" in content


def test_conditional_sections_follow_configuration(tmp_path: Path) -> None:
    minimal = ProjectConfig(project_name="minimal", docs_level="light")
    CodexBuilder().build(minimal, target_dir=tmp_path)
    content = (tmp_path / AGENTS_FILE_NAME).read_text(encoding="utf-8")

    assert "인증과 권한 검사는" not in content
    assert "client/adapter" not in content
    assert "데이터베이스:" not in content


def test_existing_agents_md_is_never_overwritten(tmp_path: Path) -> None:
    agents_file = tmp_path / AGENTS_FILE_NAME
    agents_file.write_text("# 사용자가 직접 관리하는 파일\n", encoding="utf-8")

    CodexBuilder().build(_maximal_config(), target_dir=tmp_path)

    assert agents_file.read_text(encoding="utf-8") == "# 사용자가 직접 관리하는 파일\n"


def test_no_agents_md_flag_skips_generation(tmp_path: Path) -> None:
    exit_code = main(
        [
            "--name",
            "no-agents",
            "--stack",
            "fastapi",
            "--auth",
            "no",
            "--external-api",
            "no",
            "--docs",
            "standard",
            "--no-agents-md",
            "--target-dir",
            str(tmp_path),
        ]
    )

    assert exit_code == 0
    assert not (tmp_path / AGENTS_FILE_NAME).exists()
    assert (tmp_path / ".codex" / "codex_start_prompt.txt").exists()


def test_agents_md_generated_by_default_from_cli(tmp_path: Path) -> None:
    exit_code = main(
        [
            "--name",
            "with-agents",
            "--stack",
            "fastapi",
            "--auth",
            "no",
            "--external-api",
            "no",
            "--docs",
            "standard",
            "--target-dir",
            str(tmp_path),
        ]
    )

    assert exit_code == 0
    assert (tmp_path / AGENTS_FILE_NAME).exists()
