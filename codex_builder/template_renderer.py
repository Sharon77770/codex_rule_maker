"""Render generated .codex documents from project configuration."""

from __future__ import annotations

from pathlib import Path

from codex_builder.constants import (
    AI_RULE_DIR_NAME,
    CODEX_DIR_NAME,
    REF_DOCS_DIR_NAME,
    START_PROMPT_FILE_NAME,
)
from codex_builder.models import ProjectConfig
from codex_builder.profiles import FrameworkProfile, resolve_profiles


class TemplateRenderer:
    """Build markdown/text files for the generated .codex folder."""

    def render(self, config: ProjectConfig) -> dict[Path, str]:
        profiles = resolve_profiles(config.stack)
        base = Path(CODEX_DIR_NAME)
        ai_rules = base / AI_RULE_DIR_NAME
        ref_docs = base / REF_DOCS_DIR_NAME

        return {
            ai_rules / "GLOBAL_RULES.md": self._render_global_rules(config, profiles),
            ai_rules / "ARCHITECTURE_RULES.md": self._render_architecture_rules(config, profiles),
            ai_rules / "CODE_STYLE_RULES.md": self._render_code_style_rules(config, profiles),
            ai_rules / "API_DESIGN_RULES.md": self._render_api_design_rules(config, profiles),
            ai_rules / "DOCUMENT_RULE.md": self._render_document_rules(config),
            ai_rules / "TEST_RULES.md": self._render_test_rules(config, profiles),
            ai_rules / "FRAMEWORK_RULES.md": self._render_framework_rules(config, profiles),
            ref_docs / "PROJECT_OVERVIEW.md": self._render_project_overview(config, profiles),
            ref_docs / "FEATURE_SPEC.md": self._render_feature_spec(config),
            ref_docs / "API_SPEC.md": self._render_api_spec(config),
            ref_docs / "DB_SPEC.md": self._render_db_spec(config),
            base / START_PROMPT_FILE_NAME: self._render_start_prompt(config),
        }

    def _render_global_rules(self, config: ProjectConfig, profiles: tuple[FrameworkProfile, ...]) -> str:
        if config.language == "en":
            lines = [
                f"# Global Development Rules - {config.project_name}",
                "",
                "This file defines the highest-priority coding rules inside `.codex/AI_RULE_DEVELOPER`.",
                "The reference documents in `.codex/REF_DOCS` describe the project specification and must not replace these rules.",
                "",
                "## Core Principles",
                "- Keep code changes scoped to the current user request.",
                "- Preserve the existing architecture and naming style unless the request explicitly changes it.",
                "- Separate responsibilities by layer. Do not bypass a lower layer from a presentation or HTTP layer.",
                "- Keep request/response contracts, persistence models, and UI models separate.",
                "- Do not invent undocumented behavior when a reference document already defines the expected behavior.",
                "- When requirements are unclear, choose the smallest implementation that keeps the architecture coherent.",
            ]
            lines.extend(self._conditional_global_rules(config))
            lines.extend(["", "## Active Profiles"])
            lines.extend(f"- {profile.display_name}: {profile.philosophy(config.language)}" for profile in profiles)
            return "\n".join(lines)

        lines = [
            f"# 전역 개발 규칙 - {config.project_name}",
            "",
            "이 문서는 `.codex/AI_RULE_DEVELOPER` 내부에서 가장 우선되는 코딩 규칙을 정의한다.",
            "`.codex/REF_DOCS`의 문서는 프로젝트 명세이며, 이 규칙 문서를 대체하지 않는다.",
            "",
            "## 핵심 원칙",
            "- 코드 변경 범위는 사용자의 현재 요청에 필요한 부분으로 제한한다.",
            "- 명시적 요청이 없는 한 기존 아키텍처와 네이밍 스타일을 유지한다.",
            "- 계층별 책임을 분리한다. 표현 계층이나 HTTP 계층에서 하위 계층을 우회하지 않는다.",
            "- 요청/응답 계약, 저장 모델, UI 모델을 서로 혼용하지 않는다.",
            "- 참고 문서가 정의한 동작이 있으면 임의 기능을 추가하지 않는다.",
            "- 요구사항이 불명확하면 아키텍처 일관성을 해치지 않는 가장 작은 구현을 선택한다.",
        ]
        lines.extend(self._conditional_global_rules(config))
        lines.extend(["", "## 적용 프로필"])
        lines.extend(f"- {profile.display_name}: {profile.philosophy(config.language)}" for profile in profiles)
        return "\n".join(lines)

    def _conditional_global_rules(self, config: ProjectConfig) -> list[str]:
        if config.language == "en":
            lines: list[str] = []
            if config.auth_enabled:
                lines.extend(
                    [
                        "- Authentication and authorization checks must be explicit at the API/service boundary.",
                        "- Never expose tokens, password hashes, or secrets in logs, responses, or documentation examples.",
                    ]
                )
            if config.external_api_enabled:
                lines.extend(
                    [
                        "- External API calls must go through a dedicated client/adapter layer.",
                        "- Do not fake completed external integrations. Leave clear TODOs when credentials or contracts are missing.",
                    ]
                )
            if config.database:
                lines.append(f"- Database-related changes for `{config.database}` must update repository/schema documentation.")
            if config.docs_level == "strict":
                lines.append("- Code changes require matching documentation updates before the task is considered complete.")
            return lines

        lines = []
        if config.auth_enabled:
            lines.extend(
                [
                    "- 인증과 권한 검사는 API/service 경계에서 명시적으로 수행한다.",
                    "- 토큰, 비밀번호 해시, secret은 로그, 응답, 문서 예시에 노출하지 않는다.",
                ]
            )
        if config.external_api_enabled:
            lines.extend(
                [
                    "- 외부 API 호출은 반드시 전용 client/adapter 계층을 통해 수행한다.",
                    "- 계약이나 인증 정보가 없는 외부 연동은 완성된 것처럼 꾸미지 말고 명확한 TODO를 남긴다.",
                ]
            )
        if config.database:
            lines.append(f"- `{config.database}` 관련 DB 변경은 repository/schema 문서 갱신을 함께 수행한다.")
        if config.docs_level == "strict":
            lines.append("- 코드 변경 후 관련 문서 업데이트까지 완료해야 작업이 끝난 것으로 본다.")
        return lines

    def _render_architecture_rules(self, config: ProjectConfig, profiles: tuple[FrameworkProfile, ...]) -> str:
        if config.language == "en":
            lines = [
                f"# Architecture Rules - {config.project_name}",
                "",
                "## Layering Rules",
                "- Keep each layer focused on one responsibility.",
                "- Dependencies must flow from presentation/API layers toward domain, service, repository, and infrastructure layers.",
                "- Upper layers may call lower layers through explicit interfaces or narrow modules.",
                "- Lower layers must not import UI, HTTP response, or framework request objects from upper layers.",
                "",
                "## Profile-Specific Architecture",
            ]
        else:
            lines = [
                f"# 아키텍처 규칙 - {config.project_name}",
                "",
                "## 계층 규칙",
                "- 각 계층은 하나의 책임에 집중한다.",
                "- 의존성은 표현/API 계층에서 domain, service, repository, infrastructure 방향으로 흐른다.",
                "- 상위 계층은 명시적 인터페이스 또는 좁은 모듈을 통해 하위 계층을 호출한다.",
                "- 하위 계층은 UI, HTTP 응답, framework request 객체를 상위 계층에서 가져오지 않는다.",
                "",
                "## 프로필별 아키텍처",
            ]

        for profile in profiles:
            lines.extend(["", f"### {profile.display_name}"])
            lines.extend(self._bullets(profile.architecture(config.language)))
            if profile.directories:
                header = "Recommended Structure" if config.language == "en" else "권장 구조"
                lines.extend(["", f"{header}:"])
                lines.extend(f"- `{directory}`" for directory in profile.directories)

        if config.external_api_enabled:
            lines.extend(self._external_architecture_section(config.language))
        if config.database:
            lines.extend(self._database_architecture_section(config))
        if config.auth_enabled:
            lines.extend(self._auth_architecture_section(config.language))

        return "\n".join(lines)

    def _render_code_style_rules(self, config: ProjectConfig, profiles: tuple[FrameworkProfile, ...]) -> str:
        if config.language == "en":
            return "\n".join(
                [
                    f"# Code Style Rules - {config.project_name}",
                    "",
                    "## Naming",
                    "- Use names that describe domain meaning, not implementation shortcuts.",
                    "- Avoid unclear abbreviations in public types, functions, files, and API fields.",
                    "- Keep file names consistent with the conventions of the active framework profile.",
                    "",
                    "## Structure",
                    "- Prefer small functions and methods with one reason to change.",
                    "- Extract private helpers when a method mixes validation, transformation, persistence, and response mapping.",
                    "- Do not place unrelated classes or components in the same file when the framework convention expects separation.",
                    "",
                    "## Comments",
                    "- Add comments where they explain domain rules, non-obvious constraints, or integration assumptions.",
                    "- Do not add comments that merely repeat the code.",
                    "- Keep TODO comments actionable and include the missing contract, owner, or external dependency when known.",
                    "",
                    "## Formatting",
                    "- Follow the formatter and linter already used in the repository.",
                    "- If no formatter exists yet, keep formatting conservative and consistent with nearby code.",
                ]
            )

        return "\n".join(
            [
                f"# 코드 스타일 규칙 - {config.project_name}",
                "",
                "## 네이밍",
                "- 구현 편의가 아니라 도메인 의미를 설명하는 이름을 사용한다.",
                "- 공개 타입, 함수, 파일, API 필드에서는 불명확한 축약어를 피한다.",
                "- 파일명은 적용 중인 framework profile의 관례와 일관되게 유지한다.",
                "",
                "## 구조",
                "- 함수와 메서드는 변경 이유가 하나가 되도록 작게 유지한다.",
                "- validation, transformation, persistence, response mapping이 한 메서드에 섞이면 private helper로 분리한다.",
                "- 프레임워크 관례상 분리가 필요한 클래스나 컴포넌트를 한 파일에 몰아넣지 않는다.",
                "",
                "## 주석",
                "- 도메인 규칙, 비명시적 제약, 연동 가정을 설명해야 할 때 주석을 작성한다.",
                "- 코드를 그대로 반복하는 주석은 작성하지 않는다.",
                "- TODO는 실행 가능하게 작성하고, 가능한 경우 누락된 계약, 담당 계층, 외부 의존성을 함께 적는다.",
                "",
                "## 포맷팅",
                "- 저장소에 이미 적용된 formatter와 linter를 따른다.",
                "- formatter가 아직 없다면 주변 코드와 일관된 보수적 포맷을 유지한다.",
            ]
        )

    def _render_api_design_rules(self, config: ProjectConfig, profiles: tuple[FrameworkProfile, ...]) -> str:
        if config.language == "en":
            lines = [
                f"# API Design Rules - {config.project_name}",
                "",
                "## Base Rules",
                "- Design APIs around resources and use HTTP methods for actions.",
                "- Keep request DTO/schema, response DTO/schema, and persistence entity/model separate.",
                "- Document every public endpoint in `.codex/REF_DOCS/API_SPEC.md`.",
                "- Include method, path, request fields, response fields, status codes, and error cases for each endpoint.",
                "- Do not add undocumented response fields or hidden side effects.",
            ]
        else:
            lines = [
                f"# API 설계 규칙 - {config.project_name}",
                "",
                "## 기본 규칙",
                "- API는 리소스 중심으로 설계하고 동작은 HTTP method로 표현한다.",
                "- Request DTO/schema, Response DTO/schema, persistence entity/model을 분리한다.",
                "- 공개 엔드포인트는 모두 `.codex/REF_DOCS/API_SPEC.md`에 문서화한다.",
                "- 각 엔드포인트에는 method, path, request field, response field, status code, error case를 포함한다.",
                "- 문서화되지 않은 응답 필드나 숨은 부수효과를 추가하지 않는다.",
            ]

        for profile in profiles:
            rules = profile.api_rules(config.language)
            if rules:
                lines.extend(["", f"## {profile.display_name}"])
                lines.extend(self._bullets(rules))

        if config.auth_enabled:
            if config.language == "en":
                lines.extend(
                    [
                        "",
                        "## Authentication and Authorization",
                        "- Mark whether each endpoint is public, authenticated, or admin-only.",
                        "- Define token/session behavior, refresh behavior, and expiration behavior in API docs.",
                        "- Return 401 for unauthenticated requests and 403 for authenticated users without permission.",
                    ]
                )
            else:
                lines.extend(
                    [
                        "",
                        "## 인증 및 권한",
                        "- 각 엔드포인트가 public, authenticated, admin-only 중 무엇인지 명시한다.",
                        "- token/session 동작, refresh 동작, 만료 동작을 API 문서에 정의한다.",
                        "- 인증되지 않은 요청은 401, 권한이 부족한 인증 사용자는 403으로 구분한다.",
                    ]
                )

        if config.external_api_enabled:
            if config.language == "en":
                lines.extend(
                    [
                        "",
                        "## External API Boundaries",
                        "- Separate internal API contracts from third-party API contracts.",
                        "- Convert external response shapes into internal DTOs before returning them to callers.",
                        "- Document timeout, retry, fallback, and failure mapping rules when the contract is known.",
                    ]
                )
            else:
                lines.extend(
                    [
                        "",
                        "## 외부 API 경계",
                        "- 내부 API 계약과 외부 API 계약을 분리한다.",
                        "- 외부 응답 형태는 내부 DTO로 변환한 뒤 호출자에게 반환한다.",
                        "- 계약이 확인된 경우 timeout, retry, fallback, failure mapping 규칙을 문서화한다.",
                    ]
                )

        return "\n".join(lines)

    def _render_document_rules(self, config: ProjectConfig) -> str:
        if config.language == "en":
            lines = [
                f"# Documentation Rules - {config.project_name}",
                "",
                "Documents are split by purpose:",
                "- `.codex/AI_RULE_DEVELOPER`: rules to follow while coding.",
                "- `.codex/REF_DOCS`: project specifications to reference while developing.",
                "",
                f"## Documentation Level: {config.docs_level}",
            ]
            if config.docs_level == "light":
                lines.extend(
                    [
                        "- Update documents when behavior, API contracts, or setup instructions change.",
                        "- Keep reference docs concise and focused on decisions that affect implementation.",
                    ]
                )
            elif config.docs_level == "standard":
                lines.extend(
                    [
                        "- Update related reference docs when feature behavior, API contracts, DB schema, or architecture changes.",
                        "- Keep `PROJECT_OVERVIEW.md`, `FEATURE_SPEC.md`, `API_SPEC.md`, and `DB_SPEC.md` aligned with implemented behavior.",
                    ]
                )
            else:
                lines.extend(
                    [
                        "- Code changes require documentation updates when they affect behavior, API contracts, database schema, architecture, auth, or external integrations.",
                        "- API changes require updates to `.codex/REF_DOCS/API_SPEC.md`.",
                        "- DB changes require updates to `.codex/REF_DOCS/DB_SPEC.md`.",
                        "- Architecture changes require updates to `.codex/AI_RULE_DEVELOPER/ARCHITECTURE_RULES.md` and `.codex/REF_DOCS/PROJECT_OVERVIEW.md`.",
                        "- A task is incomplete if required documentation updates are omitted.",
                    ]
                )
            return "\n".join(lines)

        lines = [
            f"# 문서화 규칙 - {config.project_name}",
            "",
            "문서는 목적별로 분리한다.",
            "- `.codex/AI_RULE_DEVELOPER`: 코딩할 때 지켜야 하는 규칙.",
            "- `.codex/REF_DOCS`: 개발 시 참고할 프로젝트 명세.",
            "",
            f"## 문서화 수준: {config.docs_level}",
        ]
        if config.docs_level == "light":
            lines.extend(
                [
                    "- 동작, API 계약, 실행 방법이 바뀌면 관련 문서를 수정한다.",
                    "- 참고 문서는 구현에 영향을 주는 결정 중심으로 간결하게 유지한다.",
                ]
            )
        elif config.docs_level == "standard":
            lines.extend(
                [
                    "- 기능 동작, API 계약, DB schema, architecture가 바뀌면 관련 참고 문서를 수정한다.",
                    "- `PROJECT_OVERVIEW.md`, `FEATURE_SPEC.md`, `API_SPEC.md`, `DB_SPEC.md`는 실제 구현과 일치해야 한다.",
                ]
            )
        else:
            lines.extend(
                [
                    "- 코드 변경이 동작, API 계약, DB schema, architecture, auth, external integration에 영향을 주면 문서 업데이트가 필수다.",
                    "- API 변경 시 `.codex/REF_DOCS/API_SPEC.md`를 반드시 수정한다.",
                    "- DB 변경 시 `.codex/REF_DOCS/DB_SPEC.md`를 반드시 수정한다.",
                    "- Architecture 변경 시 `.codex/AI_RULE_DEVELOPER/ARCHITECTURE_RULES.md`와 `.codex/REF_DOCS/PROJECT_OVERVIEW.md`를 함께 검토한다.",
                    "- 필요한 문서 업데이트를 생략한 작업은 완료로 보지 않는다.",
                ]
            )
        return "\n".join(lines)

    def _render_test_rules(self, config: ProjectConfig, profiles: tuple[FrameworkProfile, ...]) -> str:
        if config.language == "en":
            lines = [
                f"# Test Rules - {config.project_name}",
                "",
                "## Base Rules",
                "- Add or update tests when behavior changes.",
                "- Cover success cases, validation failures, authorization failures, and important error paths.",
                "- Keep tests aligned with public contracts rather than implementation trivia.",
            ]
        else:
            lines = [
                f"# 테스트 규칙 - {config.project_name}",
                "",
                "## 기본 규칙",
                "- 동작이 바뀌면 테스트를 추가하거나 수정한다.",
                "- 성공 케이스, validation 실패, authorization 실패, 중요한 오류 경로를 검증한다.",
                "- 구현 세부사항보다 공개 계약과 사용자 관찰 가능 동작을 기준으로 테스트한다.",
            ]

        for profile in profiles:
            lines.extend(["", f"## {profile.display_name}"])
            lines.extend(self._bullets(profile.test_rules(config.language)))

        if config.database:
            if config.language == "en":
                lines.extend(["", "## Database Tests", f"- Verify repository behavior and migration/schema assumptions for `{config.database}`."])
            else:
                lines.extend(["", "## DB 테스트", f"- `{config.database}` repository 동작과 migration/schema 가정을 검증한다."])
        return "\n".join(lines)

    def _render_framework_rules(self, config: ProjectConfig, profiles: tuple[FrameworkProfile, ...]) -> str:
        if config.language == "en":
            lines = [f"# Framework Rules - {config.project_name}", "", "Apply the rules for every active stack profile."]
        else:
            lines = [f"# 프레임워크 규칙 - {config.project_name}", "", "활성화된 stack profile별 규칙을 모두 적용한다."]

        for profile in profiles:
            lines.extend(["", f"## {profile.display_name}", "", profile.philosophy(config.language)])
            lines.extend(self._bullets(profile.framework_rules(config.language)))

        return "\n".join(lines)

    def _render_project_overview(self, config: ProjectConfig, profiles: tuple[FrameworkProfile, ...]) -> str:
        stack_names = ", ".join(profile.display_name for profile in profiles)
        database = config.database or ("Not specified" if config.language == "en" else "미지정")
        auth = self._enabled_label(config.auth_enabled, config.language)
        external_api = self._enabled_label(config.external_api_enabled, config.language)

        if config.language == "en":
            return "\n".join(
                [
                    f"# Project Overview - {config.project_name}",
                    "",
                    "## Summary",
                    config.description or "Describe the project purpose, users, and core product value here.",
                    "",
                    "## Basic Information",
                    f"- Project name: {config.project_name}",
                    f"- Stack: {stack_names}",
                    f"- Database: {database}",
                    f"- Authentication: {auth}",
                    f"- External API integration: {external_api}",
                    f"- Documentation level: {config.docs_level}",
                    "",
                    "## Architecture Notes",
                    "- Keep this section updated with the actual directory structure and major module responsibilities.",
                    "- Record important decisions that affect implementation boundaries.",
                    "- Link detailed behavior to `FEATURE_SPEC.md`, API contracts to `API_SPEC.md`, and database details to `DB_SPEC.md`.",
                ]
            )

        return "\n".join(
            [
                f"# 프로젝트 개요 - {config.project_name}",
                "",
                "## 요약",
                config.description or "프로젝트 목적, 사용자, 핵심 제품 가치를 여기에 작성한다.",
                "",
                "## 기본 정보",
                f"- 프로젝트 이름: {config.project_name}",
                f"- 스택: {stack_names}",
                f"- 데이터베이스: {database}",
                f"- 인증 사용: {auth}",
                f"- 외부 API 연동: {external_api}",
                f"- 문서화 수준: {config.docs_level}",
                "",
                "## 아키텍처 메모",
                "- 실제 디렉토리 구조와 주요 모듈 책임을 최신 상태로 유지한다.",
                "- 구현 경계에 영향을 주는 중요한 결정을 기록한다.",
                "- 상세 기능은 `FEATURE_SPEC.md`, API 계약은 `API_SPEC.md`, DB 상세는 `DB_SPEC.md`에 연결한다.",
            ]
        )

    def _render_feature_spec(self, config: ProjectConfig) -> str:
        if config.language == "en":
            lines = [
                f"# Feature Specification - {config.project_name}",
                "",
                "Use this document as the implementation reference for product behavior.",
                "",
                "## Feature List",
                "| Feature | User | Behavior | Status | Notes |",
                "| --- | --- | --- | --- | --- |",
                "| Example feature | Example user | Describe expected behavior | planned | Replace this row |",
                "",
                "## User Flows",
                "- Describe the main user flow step by step.",
                "- Include validation, empty state, error state, and permission behavior.",
            ]
            if config.auth_enabled:
                lines.extend(["", "## Auth Requirements", "- Define roles, protected actions, session/token behavior, and permission errors."])
            if config.external_api_enabled:
                lines.extend(["", "## External Integration Requirements", "- Define upstream systems, input/output contracts, timeout behavior, and failure handling."])
            return "\n".join(lines)

        lines = [
            f"# 기능 명세 - {config.project_name}",
            "",
            "이 문서는 제품 동작 구현 시 참고하는 기능 명세다.",
            "",
            "## 기능 목록",
            "| 기능 | 사용자 | 동작 | 상태 | 메모 |",
            "| --- | --- | --- | --- | --- |",
            "| 예시 기능 | 예시 사용자 | 기대 동작을 작성 | planned | 이 행을 교체 |",
            "",
            "## 사용자 흐름",
            "- 주요 사용자 흐름을 단계별로 작성한다.",
            "- validation, empty state, error state, permission behavior를 포함한다.",
        ]
        if config.auth_enabled:
            lines.extend(["", "## 인증 요구사항", "- role, protected action, session/token 동작, permission error를 정의한다."])
        if config.external_api_enabled:
            lines.extend(["", "## 외부 연동 요구사항", "- upstream system, input/output contract, timeout behavior, failure handling을 정의한다."])
        return "\n".join(lines)

    def _render_api_spec(self, config: ProjectConfig) -> str:
        if config.language == "en":
            lines = [
                f"# API Specification - {config.project_name}",
                "",
                "Document every public API contract here.",
                "",
                "## Endpoint Index",
                "| Method | Path | Auth | Description |",
                "| --- | --- | --- | --- |",
                "| GET | /health | public | Health check |",
                "",
                "## Endpoint Detail Template",
                "### METHOD /path",
                "- Description:",
                "- Auth:",
                "- Path params:",
                "- Query params:",
                "- Request body:",
                "- Response body:",
                "- Status codes:",
                "- Error cases:",
            ]
            if config.auth_enabled:
                lines.extend(["", "## Auth Contract", "- Define token/session format, refresh rules, expiration, and required headers."])
            if config.external_api_enabled:
                lines.extend(["", "## External API Mapping", "- Map internal endpoints to external upstream calls only when the contract is known."])
            return "\n".join(lines)

        lines = [
            f"# API 명세 - {config.project_name}",
            "",
            "공개 API 계약을 이 문서에 모두 기록한다.",
            "",
            "## 엔드포인트 목록",
            "| Method | Path | Auth | 설명 |",
            "| --- | --- | --- | --- |",
            "| GET | /health | public | 상태 확인 |",
            "",
            "## 엔드포인트 상세 템플릿",
            "### METHOD /path",
            "- 설명:",
            "- 인증:",
            "- Path params:",
            "- Query params:",
            "- Request body:",
            "- Response body:",
            "- Status codes:",
            "- Error cases:",
        ]
        if config.auth_enabled:
            lines.extend(["", "## 인증 계약", "- token/session 형식, refresh 규칙, 만료, 필수 header를 정의한다."])
        if config.external_api_enabled:
            lines.extend(["", "## 외부 API 매핑", "- 계약이 확인된 경우 내부 endpoint와 외부 upstream 호출 관계를 기록한다."])
        return "\n".join(lines)

    def _render_db_spec(self, config: ProjectConfig) -> str:
        database = config.database or ("Not specified" if config.language == "en" else "미지정")
        if config.language == "en":
            lines = [
                f"# Database Specification - {config.project_name}",
                "",
                f"- Database: {database}",
                "",
                "## Table Template",
                "### table_name",
                "- Purpose:",
                "- Owner module:",
                "- Soft delete:",
                "",
                "| Column | Type | Required | Index | Description |",
                "| --- | --- | --- | --- | --- |",
                "| id | string/int | yes | primary | Primary identifier |",
                "",
                "## Relationship Template",
                "- `table.column` -> `other_table.column`: describe cardinality and delete behavior.",
            ]
            if config.auth_enabled:
                lines.extend(["", "## Auth Tables", "- Document users, roles, sessions, tokens, and audit-related tables when they exist."])
            return "\n".join(lines)

        lines = [
            f"# DB 명세 - {config.project_name}",
            "",
            f"- 데이터베이스: {database}",
            "",
            "## 테이블 템플릿",
            "### table_name",
            "- 목적:",
            "- 담당 모듈:",
            "- Soft delete:",
            "",
            "| Column | Type | Required | Index | 설명 |",
            "| --- | --- | --- | --- | --- |",
            "| id | string/int | yes | primary | 기본 식별자 |",
            "",
            "## 관계 템플릿",
            "- `table.column` -> `other_table.column`: cardinality와 delete behavior를 설명한다.",
        ]
        if config.auth_enabled:
            lines.extend(["", "## 인증 관련 테이블", "- users, roles, sessions, tokens, audit 관련 테이블이 있으면 문서화한다."])
        return "\n".join(lines)

    def _render_start_prompt(self, config: ProjectConfig) -> str:
        if config.language == "en":
            return "\n".join(
                [
                    "Before starting any task in this repository, read the `.codex` documents first.",
                    "",
                    "Use this priority order:",
                    "1. The user's current request",
                    "2. `.codex/AI_RULE_DEVELOPER/GLOBAL_RULES.md`",
                    "3. Task-specific rules inside `.codex/AI_RULE_DEVELOPER`",
                    "4. Project specifications inside `.codex/REF_DOCS`",
                    "5. Other code and documents",
                    "",
                    "First classify the task type, such as architecture, API design, database design, service logic, UI work, testing, refactoring, or documentation.",
                    "Then read and apply the relevant rule documents before changing files.",
                    "After code changes, update any required documentation as part of the same task.",
                    "If rules conflict, follow the priority order above and keep the final behavior aligned with the user's current request.",
                ]
            )

        return "\n".join(
            [
                "작업 시작 전 `.codex` 문서를 먼저 읽을 것.",
                "",
                "규칙 우선순위:",
                "1. 사용자의 현재 요청",
                "2. `.codex/AI_RULE_DEVELOPER/GLOBAL_RULES.md`",
                "3. `.codex/AI_RULE_DEVELOPER` 내부의 작업 유형별 규칙",
                "4. `.codex/REF_DOCS` 내부의 프로젝트 명세",
                "5. 기타 코드/문서",
                "",
                "작업 유형을 먼저 판단할 것. 예: 아키텍처 설계, API 설계, DB 설계, 서비스 로직, UI 작업, 테스트, 리팩토링, 문서화.",
                "파일을 수정하기 전에 관련 규칙 문서를 먼저 읽고 적용할 것.",
                "코드 수정 후 필요한 문서도 함께 수정할 것.",
                "규칙이 충돌하면 위 우선순위를 따르고, 최종 동작은 사용자의 현재 요청에 맞출 것.",
            ]
        )

    def _external_architecture_section(self, language: str) -> list[str]:
        if language == "en":
            return [
                "",
                "## External Integration Layer",
                "- Put external HTTP/SDK integrations behind client or adapter modules.",
                "- Services call adapters through narrow methods that describe business intent.",
                "- Keep upstream DTOs separate from internal DTOs.",
            ]
        return [
            "",
            "## 외부 연동 계층",
            "- 외부 HTTP/SDK 연동은 client 또는 adapter 모듈 뒤에 둔다.",
            "- Service는 비즈니스 의도를 드러내는 좁은 메서드로 adapter를 호출한다.",
            "- Upstream DTO와 내부 DTO를 분리한다.",
        ]

    def _database_architecture_section(self, config: ProjectConfig) -> list[str]:
        if config.language == "en":
            return [
                "",
                "## Database and Repository",
                f"- `{config.database}` access must be isolated in repository or persistence modules.",
                "- Schema/entity changes require reviewing migrations, repository methods, and DB documentation.",
                "- Do not leak persistence entities directly into external API responses.",
            ]
        return [
            "",
            "## DB 및 Repository",
            f"- `{config.database}` 접근은 repository 또는 persistence 모듈 안에 격리한다.",
            "- Schema/entity 변경 시 migration, repository method, DB 문서를 함께 검토한다.",
            "- Persistence entity를 외부 API 응답으로 직접 노출하지 않는다.",
        ]

    def _auth_architecture_section(self, language: str) -> list[str]:
        if language == "en":
            return [
                "",
                "## Auth Boundary",
                "- Authentication identifies the caller; authorization decides whether the caller may perform the action.",
                "- Keep password hashing, token handling, and session persistence inside dedicated modules.",
                "- Protected service methods must receive an explicit actor/user context when needed.",
            ]
        return [
            "",
            "## 인증 경계",
            "- Authentication은 호출자를 식별하고 authorization은 해당 동작 가능 여부를 결정한다.",
            "- Password hashing, token handling, session persistence는 전용 모듈에 둔다.",
            "- 보호된 service method는 필요한 경우 명시적 actor/user context를 전달받는다.",
        ]

    def _bullets(self, values: tuple[str, ...]) -> list[str]:
        return [f"- {value}" for value in values]

    def _enabled_label(self, enabled: bool, language: str) -> str:
        if language == "en":
            return "yes" if enabled else "no"
        return "사용" if enabled else "미사용"
