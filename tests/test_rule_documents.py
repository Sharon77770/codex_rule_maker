"""Tests for rule document composition: no duplication, no missing documents."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from codex_builder.models import ProjectConfig
from codex_builder.template_renderer import TemplateRenderer

RULE_DIR = ".codex/ai_rule_developer"


def _render(**kwargs) -> dict[Path, str]:
    config = ProjectConfig(
        project_name="rule-doc-sample",
        stack=kwargs.pop("stack", ("fastapi", "react")),
        database="mysql",
        auth_enabled=True,
        external_api_enabled=True,
        docs_level="strict",
        **kwargs,
    )
    return TemplateRenderer().render(config)


def test_test_rules_document_is_generated() -> None:
    """`TEST_RULES.md` used to be rendered but never written to disk."""

    for language in ("ko", "en"):
        rendered = _render(language=language)
        content = rendered[Path(RULE_DIR) / "TEST_RULES.md"]

        assert "FastAPI" in content
        assert "React" in content
        assert "mysql" in content


def test_framework_rules_are_not_repeated_across_rule_documents() -> None:
    """Framework rules belong in GLOBAL_RULES.md only.

    They used to be inlined verbatim into CODE_STYLE_RULES.md and
    SERVICE_LAYER_RULES.md as well, which spent context budget without adding
    information.
    """

    rendered = _render()
    rule_docs = {path: text for path, text in rendered.items() if RULE_DIR in str(path)}

    counts: Counter[str] = Counter()
    for text in rule_docs.values():
        for line in text.splitlines():
            stripped = line.strip().lstrip("- ").strip()
            # The cross-reference line is meant to appear in several documents.
            if len(stripped) > 40 and "GLOBAL_RULES.md" not in stripped:
                counts[stripped] += 1

    repeated = sorted(line for line, count in counts.items() if count > 1)
    assert repeated == [], f"규칙 문서 간 중복된 문장: {repeated}"


def test_deduplicated_documents_still_point_at_framework_rules() -> None:
    rendered = _render()

    for name in ("CODE_STYLE_RULES.md", "SERVICE_LAYER_RULES.md"):
        content = rendered[Path(RULE_DIR) / name]
        assert "GLOBAL_RULES.md" in content, name


def test_every_rendered_document_is_reachable_from_agents_md() -> None:
    """A generated rule document nobody is told to read is dead weight."""

    rendered = _render()
    agents_md = rendered[Path("AGENTS.md")]

    for path in rendered:
        if RULE_DIR in str(path):
            assert path.name in agents_md, f"{path.name}가 AGENTS.md 라우팅 표에 없습니다"
