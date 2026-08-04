"""Tests for the verification and safety sections of GLOBAL_RULES.md."""

from __future__ import annotations

from pathlib import Path

from codex_builder.models import ProjectConfig
from codex_builder.template_renderer import TemplateRenderer

GLOBAL_RULES = Path(".codex/ai_rule_developer/GLOBAL_RULES.md")


def _global_rules(language: str = "ko", **kwargs) -> str:
    config = ProjectConfig(project_name="safety-sample", language=language, **kwargs)
    return TemplateRenderer().render(config)[GLOBAL_RULES]


def test_verification_section_exists_in_both_languages() -> None:
    assert "## 검증" in _global_rules("ko")
    assert "## Verification" in _global_rules("en")


def test_agent_is_told_to_run_repository_commands() -> None:
    content = _global_rules("ko")

    assert "build, test, lint" in content
    assert "CI 워크플로" in content


def test_agent_must_not_invent_commands_or_assume_success() -> None:
    """The generator never scans the target repo, so guessing must be forbidden."""

    ko = _global_rules("ko")
    en = _global_rules("en")

    assert "임의로 만들어내지 않는다" in ko
    assert "통과했다고 가정하지 말고" in ko
    assert "Do not invent a command that is not defined." in en
    assert "instead of assuming it passed" in en


def test_agent_may_not_weaken_tests_to_get_a_green_run() -> None:
    ko = _global_rules("ko")

    assert "단정을 약화시켜 통과시키지 않는다" in ko
    assert "skip 처리" in ko


def test_safety_section_covers_secrets() -> None:
    for language, needle in (("ko", "## 안전"), ("en", "## Safety")):
        content = _global_rules(language)
        assert needle in content

    ko = _global_rules("ko")
    assert "`.env`" in ko
    assert "커밋 메시지에 남기지 않는다" in ko
    assert "값 설정은 사람에게 맡긴다" in ko


def test_safety_section_covers_destructive_actions() -> None:
    ko = _global_rules("ko")

    for phrase in ("git history 재작성", "force push", "branch 삭제", "migration"):
        assert phrase in ko, phrase

    assert "실행 전에 확인을 받는다" in ko
    assert "lock 파일" in ko


def test_safety_rules_apply_even_without_auth_or_external_api() -> None:
    """Secret handling used to appear only when --auth was enabled."""

    content = _global_rules("ko", auth_enabled=False, external_api_enabled=False)

    assert "## 안전" in content
    assert "secret" in content
