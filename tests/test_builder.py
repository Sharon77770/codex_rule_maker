from __future__ import annotations

import pytest

from codex_builder.builder import CodexBuilder, ExistingCodexError
from codex_builder.models import ProjectConfig


def test_default_generation_success(tmp_path):
    config = ProjectConfig(project_name="sample-api")

    result = CodexBuilder().build(config, target_dir=tmp_path)

    assert result.codex_dir == tmp_path / ".codex"
    assert (tmp_path / ".codex" / "AI_RULE_DEVELOPER" / "GLOBAL_RULES.md").exists()
    assert (tmp_path / ".codex" / "REF_DOCS" / "PROJECT_OVERVIEW.md").exists()
    assert (tmp_path / ".codex" / "codex_start_prompt.txt").exists()
    assert len(result.written_files) == 12

    start_prompt = (tmp_path / ".codex" / "codex_start_prompt.txt").read_text(encoding="utf-8")
    assert "작업 시작 전 `.codex` 문서를 먼저 읽을 것" in start_prompt
    assert "1. 사용자의 현재 요청" in start_prompt
    assert "코드 수정 후 필요한 문서도 함께 수정할 것" in start_prompt


def test_fastapi_profile_generation(tmp_path):
    config = ProjectConfig(
        project_name="sample-api",
        stack=("fastapi",),
        database="mysql",
        auth_enabled=True,
        external_api_enabled=True,
        docs_level="strict",
    )

    CodexBuilder().build(config, target_dir=tmp_path)

    framework_rules = (tmp_path / ".codex" / "AI_RULE_DEVELOPER" / "FRAMEWORK_RULES.md").read_text(encoding="utf-8")
    architecture_rules = (tmp_path / ".codex" / "AI_RULE_DEVELOPER" / "ARCHITECTURE_RULES.md").read_text(encoding="utf-8")
    document_rules = (tmp_path / ".codex" / "AI_RULE_DEVELOPER" / "DOCUMENT_RULE.md").read_text(encoding="utf-8")

    assert "FastAPI" in framework_rules
    assert "Controller -> Service -> Repository -> DB" in architecture_rules
    assert "`mysql` 접근" in architecture_rules
    assert "외부 연동 계층" in architecture_rules
    assert "문서 업데이트가 필수" in document_rules


def test_python_profile_generation(tmp_path):
    config = ProjectConfig(project_name="sample-python", stack=("python",))

    CodexBuilder().build(config, target_dir=tmp_path)

    architecture_rules = (tmp_path / ".codex" / "AI_RULE_DEVELOPER" / "ARCHITECTURE_RULES.md").read_text(encoding="utf-8")
    framework_rules = (tmp_path / ".codex" / "AI_RULE_DEVELOPER" / "FRAMEWORK_RULES.md").read_text(encoding="utf-8")
    test_rules = (tmp_path / ".codex" / "AI_RULE_DEVELOPER" / "TEST_RULES.md").read_text(encoding="utf-8")

    assert "Python" in framework_rules
    assert "Entrypoint/CLI -> Application Service -> Domain/Adapter -> External System" in architecture_rules
    assert "import 시점에 파일 생성" in framework_rules
    assert "CLI 인자, 설정 파싱, 오류 경로" in test_rules


def test_react_profile_generation(tmp_path):
    config = ProjectConfig(project_name="sample-web", stack=("react",))

    CodexBuilder().build(config, target_dir=tmp_path)

    architecture_rules = (tmp_path / ".codex" / "AI_RULE_DEVELOPER" / "ARCHITECTURE_RULES.md").read_text(encoding="utf-8")
    framework_rules = (tmp_path / ".codex" / "AI_RULE_DEVELOPER" / "FRAMEWORK_RULES.md").read_text(encoding="utf-8")

    assert "Page -> Hook/Store -> Service -> API" in architecture_rules
    assert "컴포넌트 안에서 fetch/axios 호출을 직접 수행하지 않는다" in framework_rules


def test_fullstack_fastapi_react_profile_generation(tmp_path):
    config = ProjectConfig(project_name="sample-fullstack", stack=("fullstack-fastapi-react",))

    CodexBuilder().build(config, target_dir=tmp_path)

    architecture_rules = (tmp_path / ".codex" / "AI_RULE_DEVELOPER" / "ARCHITECTURE_RULES.md").read_text(encoding="utf-8")
    api_spec = (tmp_path / ".codex" / "REF_DOCS" / "API_SPEC.md").read_text(encoding="utf-8")

    assert "backend는 Controller -> Service -> Repository -> DB" in architecture_rules
    assert "frontend는 Page -> Hook/Store -> Service -> API" in architecture_rules
    assert "공개 API 계약" in api_spec


def test_existing_codex_without_force_stops(tmp_path):
    (tmp_path / ".codex").mkdir()
    config = ProjectConfig(project_name="sample-api")

    with pytest.raises(ExistingCodexError):
        CodexBuilder().build(config, target_dir=tmp_path)


def test_force_regenerates_and_backs_up_existing_codex(tmp_path):
    existing = tmp_path / ".codex"
    existing.mkdir()
    (existing / "old.txt").write_text("old", encoding="utf-8")
    config = ProjectConfig(project_name="sample-api")

    result = CodexBuilder().build(config, target_dir=tmp_path, force=True)

    assert result.backup_dir is not None
    assert result.backup_dir.exists()
    assert (result.backup_dir / "old.txt").read_text(encoding="utf-8") == "old"
    assert (tmp_path / ".codex" / "AI_RULE_DEVELOPER" / "GLOBAL_RULES.md").exists()
