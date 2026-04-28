from __future__ import annotations

import pytest

from codex_builder.builder import CodexBuilder, ExistingCodexError
from codex_builder.models import ProjectConfig


def test_default_generation_success(tmp_path):
    config = ProjectConfig(project_name="sample-api")

    result = CodexBuilder().build(config, target_dir=tmp_path)

    assert result.codex_dir == tmp_path / ".codex"
    assert (tmp_path / ".codex" / "ai_rule_developer" / "GLOBAL_RULES.md").exists()
    assert (tmp_path / ".codex" / "ai_rule_developer" / "SERVICE_LAYER_RULES.md").exists()
    assert (tmp_path / ".codex" / "ai_rule_developer" / "DOMAIN_MODEL_RULES.md").exists()
    assert (tmp_path / ".codex" / "ai_rule_developer" / "EXTERNAL_INTEGRATION_RULES.md").exists()
    assert (tmp_path / ".codex" / "ref_docs").is_dir()
    assert not any((tmp_path / ".codex" / "ref_docs").iterdir())
    assert (tmp_path / "docs" / "architecture" / "architecture.md").exists()
    assert (tmp_path / "docs" / "api" / "specification.md").exists()
    assert (tmp_path / "docs" / "database" / "schema.md").exists()
    assert (tmp_path / ".codex" / "codex_start_prompt.txt").exists()
    assert len(result.written_files) == 17

    start_prompt = (tmp_path / ".codex" / "codex_start_prompt.txt").read_text(encoding="utf-8")
    assert "지금부터 이 저장소의 작업을 시작한다" in start_prompt
    assert "프로젝트 루트 `docs/` 내부의 프로젝트 명세" in start_prompt
    assert "`.codex/ref_docs` 내부의 외부 아키텍처" in start_prompt
    assert "코드 수정 후 필요한 문서도 같은 작업 안에서 함께 수정한다" in start_prompt


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

    service_rules = (tmp_path / ".codex" / "ai_rule_developer" / "SERVICE_LAYER_RULES.md").read_text(encoding="utf-8")
    architecture_rules = (tmp_path / ".codex" / "ai_rule_developer" / "ARCHITECTURE_RULES.md").read_text(encoding="utf-8")
    document_rules = (tmp_path / ".codex" / "ai_rule_developer" / "DOCUMENT_RULE.md").read_text(encoding="utf-8")

    assert "FastAPI" in service_rules
    assert "Controller -> Service -> Repository -> DB" in architecture_rules
    assert "`mysql` 접근" in architecture_rules
    assert "외부 연동 계층" in architecture_rules
    assert "문서 업데이트가 필수" in document_rules
    assert "프로젝트 루트의 `docs/`" in document_rules
    assert "`.codex/ref_docs`: 외부/사용자 추가 참고자료 전용" in document_rules


def test_python_profile_generation(tmp_path):
    config = ProjectConfig(project_name="sample-python", stack=("python",))

    CodexBuilder().build(config, target_dir=tmp_path)

    architecture_rules = (tmp_path / ".codex" / "ai_rule_developer" / "ARCHITECTURE_RULES.md").read_text(encoding="utf-8")
    service_rules = (tmp_path / ".codex" / "ai_rule_developer" / "SERVICE_LAYER_RULES.md").read_text(encoding="utf-8")
    domain_rules = (tmp_path / ".codex" / "ai_rule_developer" / "DOMAIN_MODEL_RULES.md").read_text(encoding="utf-8")

    assert "Python" in service_rules
    assert "Entrypoint/CLI -> Application Service -> Domain/Adapter -> External System" in architecture_rules
    assert "import 시점에 파일 생성" in service_rules
    assert "상태값은 명시적 enum" in domain_rules
    assert "CLI 입력은 domain/service logic에 전달하기 전에 별도 input model로 변환한다" in domain_rules


def test_react_profile_generation(tmp_path):
    config = ProjectConfig(project_name="sample-web", stack=("react",))

    CodexBuilder().build(config, target_dir=tmp_path)

    architecture_rules = (tmp_path / ".codex" / "ai_rule_developer" / "ARCHITECTURE_RULES.md").read_text(encoding="utf-8")
    service_rules = (tmp_path / ".codex" / "ai_rule_developer" / "SERVICE_LAYER_RULES.md").read_text(encoding="utf-8")

    assert "Page -> Hook/Store -> Service -> API" in architecture_rules
    assert "컴포넌트 안에서 fetch/axios 호출을 직접 수행하지 않는다" in service_rules


def test_fullstack_fastapi_react_profile_generation(tmp_path):
    config = ProjectConfig(project_name="sample-fullstack", stack=("fullstack-fastapi-react",))

    CodexBuilder().build(config, target_dir=tmp_path)

    architecture_rules = (tmp_path / ".codex" / "ai_rule_developer" / "ARCHITECTURE_RULES.md").read_text(encoding="utf-8")
    api_spec = (tmp_path / "docs" / "api" / "specification.md").read_text(encoding="utf-8")

    assert "backend는 Controller -> Service -> Repository -> DB" in architecture_rules
    assert "frontend는 Page -> Hook/Store -> Service -> API" in architecture_rules
    assert "정확한 API 계약" in api_spec


def test_existing_project_docs_are_not_overwritten(tmp_path):
    docs_file = tmp_path / "docs" / "api" / "specification.md"
    docs_file.parent.mkdir(parents=True)
    docs_file.write_text("custom api spec", encoding="utf-8")
    config = ProjectConfig(project_name="sample-api")

    CodexBuilder().build(config, target_dir=tmp_path)

    assert docs_file.read_text(encoding="utf-8") == "custom api spec"


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
    assert (tmp_path / ".codex" / "ai_rule_developer" / "GLOBAL_RULES.md").exists()
