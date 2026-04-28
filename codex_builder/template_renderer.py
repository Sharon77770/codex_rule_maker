"""Render generated .codex documents from project configuration."""

from __future__ import annotations

from pathlib import Path

from codex_builder.constants import (
    AI_RULE_DIR_NAME,
    CODEX_DIR_NAME,
    DOCS_DIR_NAME,
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
        docs = Path(DOCS_DIR_NAME)

        return {
            ai_rules / "GLOBAL_RULES.md": self._render_global_rules(config, profiles),
            ai_rules / "ARCHITECTURE_RULES.md": self._render_architecture_rules(config, profiles),
            ai_rules / "CODE_STYLE_RULES.md": self._render_code_style_rules(config, profiles),
            ai_rules / "API_DESIGN_RULES.md": self._render_api_design_rules(config, profiles),
            ai_rules / "DOCUMENT_RULE.md": self._render_document_rules(config),
            ai_rules / "DOMAIN_MODEL_RULES.md": self._render_domain_model_rules(config, profiles),
            ai_rules / "EXTERNAL_INTEGRATION_RULES.md": self._render_external_integration_rules(config, profiles),
            ai_rules / "SERVICE_LAYER_RULES.md": self._render_service_layer_rules(config, profiles),
            docs / "architecture" / "directory.md": self._render_docs_directory(config, profiles),
            docs / "architecture" / "architecture.md": self._render_docs_architecture(config, profiles),
            docs / "architecture" / "component.md": self._render_docs_component(config, profiles),
            docs / "architecture" / "state.md": self._render_docs_state(config),
            docs / "architecture" / "flow.md": self._render_docs_flow(config),
            docs / "api" / "endpoints.md": self._render_docs_api_endpoints(config),
            docs / "api" / "specification.md": self._render_docs_api_specification(config),
            docs / "database" / "schema.md": self._render_docs_database_schema(config),
            base / START_PROMPT_FILE_NAME: self._render_start_prompt(config),
        }

    def render_directories(self, config: ProjectConfig) -> tuple[Path, ...]:
        base = Path(CODEX_DIR_NAME)
        docs = Path(DOCS_DIR_NAME)
        return (
            base / AI_RULE_DIR_NAME,
            base / REF_DOCS_DIR_NAME,
            docs / "architecture",
            docs / "api",
            docs / "database",
        )

    def _render_global_rules(self, config: ProjectConfig, profiles: tuple[FrameworkProfile, ...]) -> str:
        if config.language == "en":
            lines = [
                f"# Global Rules - {config.project_name}",
                "",
                f"You are the senior developer responsible for `{config.project_name}`.",
                "Before changing files, read the `.codex` documents and treat them as repository-local rules.",
                "",
                "## Absolute Rules",
                "- The user's current request has the highest priority.",
                "- Use `.codex/ai_rule_developer` for coding rules, root `docs/` for project specifications, and `.codex/ref_docs` only for user-added external references.",
                "- Keep changes scoped to the current task and avoid unrelated refactors.",
                "- Preserve the existing architecture, naming style, and public contracts unless the request explicitly changes them.",
                "- Keep layers separated. Do not bypass service/application boundaries to reach persistence or external systems.",
                "- Do not mix request/response DTOs, persistence entities, domain models, and UI view models.",
                "- Do not invent undocumented behavior when a reference document defines the expected behavior.",
                "- When requirements are unclear, choose the smallest implementation that keeps the architecture coherent.",
            ]
            lines.extend(self._conditional_global_rules(config))
            lines.extend(["", "## Active Profiles"])
            for profile in profiles:
                lines.extend([f"- {profile.display_name}: {profile.philosophy(config.language)}"])
                lines.extend(f"  - {rule}" for rule in profile.framework_rules(config.language))
            lines.extend(
                [
                    "",
                    "## Prohibited",
                    "- Do not put all logic in one file for convenience.",
                    "- Do not place business logic in controllers, route handlers, or UI components.",
                    "- Do not return persistence entities directly from public APIs.",
                    "- Do not complete external integrations with fake implementations.",
                    "- Do not add core code without documenting the intent when the behavior is non-obvious.",
                ]
            )
            return "\n".join(lines)

        lines = [
            f"# 전역 규칙 - {config.project_name}",
            "",
            f"너는 `{config.project_name}` 프로젝트를 수행하는 시니어 개발자다.",
            "파일을 수정하기 전에 `.codex` 문서를 먼저 읽고, 이 저장소의 로컬 규칙으로 적용한다.",
            "",
            "## 절대 규칙",
            "- 사용자의 현재 요청을 최우선으로 둔다.",
            "- 코딩 규칙은 `.codex/ai_rule_developer`, 프로젝트 명세는 루트 `docs/`, 사용자 추가 외부 참고자료는 `.codex/ref_docs`를 기준으로 삼는다.",
            "- 코드 변경 범위는 현재 요청에 필요한 부분으로 제한하고 불필요한 리팩토링을 하지 않는다.",
            "- 명시적 요청이 없는 한 기존 아키텍처, 네이밍 스타일, 공개 계약을 유지한다.",
            "- 계층별 책임을 분리한다. 표현 계층이나 HTTP 계층에서 service/application 경계를 우회하지 않는다.",
            "- Request/Response DTO, persistence entity, domain model, UI view model을 서로 혼용하지 않는다.",
            "- 참고 문서가 정의한 동작이 있으면 임의 기능을 추가하지 않는다.",
            "- 요구사항이 불명확하면 아키텍처 일관성을 해치지 않는 가장 작은 구현을 선택한다.",
        ]
        lines.extend(self._conditional_global_rules(config))
        lines.extend(["", "## 적용 프로필"])
        for profile in profiles:
            lines.extend([f"- {profile.display_name}: {profile.philosophy(config.language)}"])
            lines.extend(f"  - {rule}" for rule in profile.framework_rules(config.language))
        lines.extend(
            [
                "",
                "## 금지 사항",
                "- 편의를 위해 모든 로직을 한 파일에 몰아넣지 않는다.",
                "- controller, route handler, UI component에 비즈니스 로직을 넣지 않는다.",
                "- persistence entity를 public API 응답으로 직접 반환하지 않는다.",
                "- 외부 연동을 가짜 구현으로 완성한 것처럼 만들지 않는다.",
                "- 동작이 비명시적인 핵심 코드에 의도 설명 없이 코드를 추가하지 않는다.",
            ]
        )
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
                "This project follows a layered architecture. Keep responsibilities explicit and directional.",
                "",
                "[Directory Structure]",
            ]
            for profile in profiles:
                if profile.directories:
                    lines.extend(f"- `{directory}`" for directory in profile.directories)
            lines.extend(
                [
                    "",
                    "[Layer Responsibilities]",
                    "- Presentation/API layers handle request parsing, response mapping, routing, and UI composition only.",
                    "- Service/application layers own use-case orchestration and business decisions.",
                    "- Repository/adapter/infrastructure layers own persistence and external system access.",
                    "- Entity/domain models represent stored or domain state and must not be used as public response objects.",
                    "- Schema/DTO/view models represent external contracts and must stay separate from persistence models.",
                    "",
                    "[Dependency Direction]",
                    "- Dependencies flow from presentation/API/UI layers toward service/application, repository/adapter, and infrastructure layers.",
                    "- Upper layers may call lower layers through explicit interfaces or narrow modules.",
                    "- Lower layers must not import UI, HTTP response, request, or framework objects from upper layers.",
                    "",
                    "[Profile-Specific Architecture]",
                ]
            )
        else:
            lines = [
                f"# 아키텍처 규칙 - {config.project_name}",
                "",
                "이 프로젝트는 명확한 계층형 아키텍처를 따른다. 책임과 의존성 방향을 반드시 분리한다.",
                "",
                "[디렉토리 구조]",
            ]
            for profile in profiles:
                if profile.directories:
                    lines.extend(f"- `{directory}`" for directory in profile.directories)
            lines.extend(
                [
                    "",
                    "[계층 책임]",
                    "- Presentation/API 계층은 요청 파싱, 응답 변환, 라우팅, 화면 조립만 담당한다.",
                    "- Service/Application 계층은 유스케이스 조합과 비즈니스 판단을 담당한다.",
                    "- Repository/Adapter/Infrastructure 계층은 DB 접근과 외부 시스템 접근을 담당한다.",
                    "- Entity/Domain model은 저장 또는 도메인 상태를 표현하며 public response 객체로 직접 사용하지 않는다.",
                    "- Schema/DTO/View model은 외부 계약을 표현하며 persistence model과 분리한다.",
                    "",
                    "[의존성 방향]",
                    "- 의존성은 Presentation/API/UI 계층에서 Service/Application, Repository/Adapter, Infrastructure 방향으로 흐른다.",
                    "- 상위 계층은 명시적 인터페이스 또는 좁은 모듈을 통해 하위 계층을 호출한다.",
                    "- 하위 계층은 UI, HTTP 응답, request, framework 객체를 상위 계층에서 가져오지 않는다.",
                    "",
                    "[프로필별 아키텍처]",
                ]
            )

        for profile in profiles:
            lines.extend(["", f"### {profile.display_name}"])
            lines.extend(self._bullets(profile.architecture(config.language)))

        if config.external_api_enabled:
            lines.extend(self._external_architecture_section(config.language))
        if config.database:
            lines.extend(self._database_architecture_section(config))
        if config.auth_enabled:
            lines.extend(self._auth_architecture_section(config.language))

        return "\n".join(lines)

    def _render_code_style_rules(self, config: ProjectConfig, profiles: tuple[FrameworkProfile, ...]) -> str:
        if config.language == "en":
            lines = [
                f"# Code Style Rules - {config.project_name}",
                "",
                "Code style is a core rule for this repository, not a cosmetic preference.",
                "Follow the existing formatter and linter first. When the formatter does not decide a point, apply this document.",
                "",
                "[Spacing Rules]",
                "- Keep method boundaries visually obvious. Use the repository's formatter when it enforces exact blank lines.",
                "- When the formatter allows manual spacing, keep five blank-line units between methods.",
                "- Inside a method, separate unrelated logic blocks with two blank-line units when the formatter allows it.",
                "- If a function signature, expression, query, JSX block, or builder chain spans multiple lines, leave a blank line before starting the next logic block.",
                "- Do not compress validation, transformation, persistence, and response mapping into one dense block.",
                "",
                "[Naming Rules]",
                "- Clear names are more important than short names.",
                "- Use names that describe domain meaning, user intent, or use-case responsibility.",
                "- Avoid unexplained abbreviations in variables, methods, classes, files, DTO fields, API fields, and database columns.",
                "- Boolean names must read as a true/false statement, such as `is_active`, `has_permission`, or `should_retry`.",
                "- Collection names must make cardinality clear, such as `simulation_jobs` instead of `job`.",
                "",
                "[Method and Function Rules]",
                "- One method should have one reason to change.",
                "- Split a method when it mixes validation, authorization, state transition, persistence, external calls, and response mapping.",
                "- Use private helpers for repeated or nested decisions, but do not hide business rules behind vague helper names.",
                "- Use use-case names for service methods and event/intent names for UI handlers.",
                "- Do not write catch-all methods such as `process`, `handle`, `do_work`, or `manage` unless the surrounding domain gives them precise meaning.",
                "",
                "[Typing and Contracts]",
                "- Public functions, service methods, DTOs, schemas, entities, domain models, and view models must have explicit types.",
                "- Do not rely on implicit or inferred types when they define a public contract.",
                "- Input and output models must be represented with explicit structures, not loose dictionaries or untyped objects unless the framework requires it.",
                "- Optional fields must be explicit and must document the meaning of missing values.",
                "",
                "[Comments]",
                "- Add meaningful comments for every core class and core method.",
                "- Use JavaDoc/docstring-style comments when the language convention allows it.",
                "- Comments should explain domain rules, non-obvious constraints, integration assumptions, state transitions, or failure behavior.",
                "- Private helpers need comments when their purpose is not immediately obvious from the name.",
                "- TODO comments must state the missing contract, upstream dependency, owner, or follow-up condition.",
                "- Do not add comments that merely repeat the code.",
                "",
                "[File Organization]",
                "- Keep one primary class, component, service, repository, or adapter per file when the active framework convention expects separation.",
                "- Do not place unrelated classes, components, hooks, controllers, services, repositories, and DTOs in the same file.",
                "- Keep imports grouped and remove unused imports as part of the same change.",
                "- Do not introduce new directories unless they match the active framework profile or remove meaningful duplication.",
                "",
                "[Prohibited]",
                "- Abbreviated variable names.",
                "- Meaningless method names.",
                "- Core code without intent comments.",
                "- Public contracts without explicit types.",
                "- Files that mix unrelated layers.",
                "- Formatting that fights the repository's configured formatter.",
            ]
            for profile in profiles:
                lines.extend(["", f"[{profile.display_name} Style Notes]"])
                lines.extend(self._bullets(profile.framework_rules(config.language)))
            return "\n".join(lines)

        lines = [
                f"# 코드 스타일 규칙 - {config.project_name}",
                "",
                "코드 스타일은 취향이 아니라 이 저장소의 핵심 규칙이다.",
                "저장소에 formatter와 linter가 있으면 그것을 우선한다. formatter가 결정하지 않는 영역은 이 문서를 따른다.",
                "",
                "[공백 규칙]",
                "- 메서드 경계는 눈으로 분명히 구분되어야 한다. 정확한 공백 수는 저장소 formatter가 강제하면 formatter를 따른다.",
                "- formatter가 수동 공백을 허용하면 메서드 간 5칸 공백을 둔다.",
                "- 메서드 내부의 연관 없는 로직 블록 간에는 formatter가 허용하는 범위에서 2칸 공백을 둔다.",
                "- 함수 시그니처, 표현식, 쿼리, JSX block, builder chain이 여러 줄에 걸쳐 작성되면 다음 로직 블록 전에는 반드시 공백을 둔다.",
                "- validation, transformation, persistence, response mapping을 하나의 빽빽한 블록으로 압축하지 않는다.",
                "",
                "[네이밍]",
                "- 짧은 이름보다 명확한 이름을 우선한다.",
                "- 도메인 의미, 사용자 의도, use-case 책임을 설명하는 이름을 사용한다.",
                "- 변수, 메서드, 클래스, 파일, DTO 필드, API 필드, DB 컬럼에서 설명 없는 축약어를 피한다.",
                "- boolean 이름은 `is_active`, `has_permission`, `should_retry`처럼 참/거짓 문장으로 읽혀야 한다.",
                "- collection 이름은 `simulation_jobs`처럼 복수성과 의미가 드러나야 한다.",
                "",
                "[메서드 규칙]",
                "- 하나의 메서드는 변경 이유가 하나여야 한다.",
                "- validation, authorization, state transition, persistence, external call, response mapping이 섞이면 메서드를 분리한다.",
                "- 반복되거나 중첩된 판단은 private helper로 분리하되, 모호한 helper 이름 뒤에 비즈니스 규칙을 숨기지 않는다.",
                "- Service method는 use-case 이름을 사용하고, UI handler는 event 또는 user intent 이름을 사용한다.",
                "- 주변 도메인이 의미를 명확히 만들지 않는 한 `process`, `handle`, `do_work`, `manage` 같은 포괄적 이름을 사용하지 않는다.",
                "",
                "[타입 및 계약]",
                "- 공개 함수, service method, DTO, schema, entity, domain model, view model에는 명시적 타입을 유지한다.",
                "- 공개 계약을 정의하는 위치에서는 추론형 또는 암시적 타입에 의존하지 않는다.",
                "- 입력/출력 모델은 loose dictionary나 untyped object가 아니라 명시적 구조로 표현한다. 단, 프레임워크가 요구하는 경우는 예외다.",
                "- optional field는 명시적으로 표시하고 값이 없을 때의 의미를 문서화한다.",
                "",
                "[주석]",
                "- 모든 핵심 클래스와 핵심 메서드에는 의미 있는 설명을 작성한다.",
                "- 언어 관례가 허용하면 JavaDoc/docstring 스타일 주석을 사용한다.",
                "- 주석은 도메인 규칙, 비명시적 제약, 연동 가정, 상태 전이, 실패 동작을 설명해야 한다.",
                "- private helper도 이름만으로 목적이 분명하지 않으면 주석으로 존재 이유를 설명한다.",
                "- TODO는 누락된 계약, upstream 의존성, 담당자, 후속 조건을 포함해야 한다.",
                "- 코드를 그대로 반복하는 주석은 작성하지 않는다.",
                "",
                "[파일 구성]",
                "- 활성 framework 관례가 분리를 요구하면 한 파일은 하나의 주요 class, component, service, repository, adapter를 책임진다.",
                "- 무관한 class, component, hook, controller, service, repository, DTO를 한 파일에 섞지 않는다.",
                "- import는 그룹화하고 사용하지 않는 import는 같은 변경에서 제거한다.",
                "- 활성 framework profile과 맞지 않거나 의미 있는 중복 제거가 아닌 새 directory를 만들지 않는다.",
                "",
                "[금지]",
                "- 축약된 변수명",
                "- 의미 없는 메서드명",
                "- 의도 설명 없는 핵심 코드",
                "- 명시적 타입 없는 공개 계약",
                "- 서로 다른 계층을 섞은 파일",
                "- 저장소 formatter와 충돌하는 포맷팅",
            ]
        for profile in profiles:
            lines.extend(["", f"[{profile.display_name} 스타일 메모]"])
            lines.extend(self._bullets(profile.framework_rules(config.language)))
        return "\n".join(lines)

    def _render_api_design_rules(self, config: ProjectConfig, profiles: tuple[FrameworkProfile, ...]) -> str:
        if config.language == "en":
            lines = [
                f"# API Design Rules - {config.project_name}",
                "",
                "All public APIs must follow resource-oriented REST design.",
                "",
                "[Base Rules]",
                "- Use `/api/v1` as the default API prefix unless the project already defines another versioning rule.",
                "- Use noun-based URLs and express actions with HTTP methods.",
                "- Design APIs around project domain resources, not implementation functions.",
                "- Keep request DTO/schema, response DTO/schema, and persistence entity/model separate.",
                "- Document every public endpoint in `docs/api/endpoints.md` and `docs/api/specification.md`.",
                "- Include method, path, request fields, response fields, status codes, and error cases for each endpoint.",
                "- Do not add undocumented response fields or hidden side effects.",
                "",
                "[Resource Flow]",
                "- Define the domain resource flow before adding endpoints.",
                "- Child resources must reflect real ownership or lifecycle relationships.",
                "- Do not expose internal pipeline, worker, or implementation names as public resources unless they are part of the product contract.",
            ]
        else:
            lines = [
                f"# API 설계 규칙 - {config.project_name}",
                "",
                "모든 공개 API는 리소스 중심 REST 설계를 따른다.",
                "",
                "[기본 규칙]",
                "- 프로젝트에 별도 버전 규칙이 없으면 기본 prefix는 `/api/v1`로 둔다.",
                "- URL은 명사형으로 작성하고 동작은 HTTP method로 표현한다.",
                "- 구현 함수가 아니라 프로젝트 도메인 리소스를 기준으로 API를 설계한다.",
                "- Request DTO/schema, Response DTO/schema, persistence entity/model을 분리한다.",
                "- 공개 엔드포인트는 모두 `docs/api/endpoints.md`와 `docs/api/specification.md`에 문서화한다.",
                "- 각 엔드포인트에는 method, path, request field, response field, status code, error case를 포함한다.",
                "- 문서화되지 않은 응답 필드나 숨은 부수효과를 추가하지 않는다.",
                "",
                "[리소스 흐름]",
                "- 엔드포인트를 추가하기 전에 도메인 리소스 흐름을 먼저 정의한다.",
                "- 하위 리소스는 실제 소유 관계나 생명주기 관계가 있을 때만 사용한다.",
                "- pipeline, worker 같은 내부 구현 이름은 제품 계약이 아닌 한 public resource로 노출하지 않는다.",
            ]

        for profile in profiles:
            rules = profile.api_rules(config.language)
            if rules:
                lines.extend(["", f"[{profile.display_name}]"])
                lines.extend(self._bullets(rules))

        if config.auth_enabled:
            if config.language == "en":
                lines.extend(
                    [
                        "",
                        "[Authentication and Authorization]",
                        "- Mark whether each endpoint is public, authenticated, or admin-only.",
                        "- Define token/session behavior, refresh behavior, and expiration behavior in API docs.",
                        "- Return 401 for unauthenticated requests and 403 for authenticated users without permission.",
                    ]
                )
            else:
                lines.extend(
                    [
                        "",
                        "[인증 및 권한]",
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
                        "[External API Boundaries]",
                        "- Separate internal API contracts from third-party API contracts.",
                        "- Convert external response shapes into internal DTOs before returning them to callers.",
                        "- Document timeout, retry, fallback, and failure mapping rules when the contract is known.",
                    ]
                )
            else:
                lines.extend(
                    [
                        "",
                        "[외부 API 경계]",
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
                "This project treats documentation as part of the implementation.",
                "Project specifications belong in the repository root `docs/` directory.",
                "The `.codex/ref_docs` directory is only a user-managed space for external architecture notes, PRDs, research, vendor documents, or other reference material.",
                "",
                "[Document Locations]",
                "- `.codex/ai_rule_developer`: rules to follow while coding.",
                "- `.codex/ref_docs`: external/user-added reference documents only. Generate the directory, but do not generate project specs inside it.",
                "- `docs/architecture`: project architecture and flow documentation.",
                "- `docs/api`: endpoint index and API contract documentation.",
                "- `docs/database`: database schema documentation.",
                "",
                f"[Documentation Level: {config.docs_level}]",
            ]
            if config.docs_level == "light":
                lines.extend(
                    [
                        "- Update docs when behavior, API contracts, DB schema, architecture, auth, or external integration behavior changes.",
                        "- Keep each changed document focused on the part of the implementation that actually changed.",
                    ]
                )
            elif config.docs_level == "standard":
                lines.extend(
                    [
                        "- Code changes that affect behavior, API contracts, DB schema, architecture, auth, or external integrations require matching docs changes.",
                        "- Keep `docs/architecture`, `docs/api`, and `docs/database` aligned with implemented behavior.",
                        "- Review docs before marking a task complete.",
                    ]
                )
            else:
                lines.extend(
                    [
                        "- Every code change that affects behavior, API contracts, database schema, architecture, auth, or external integrations requires documentation updates.",
                        "- API changes require endpoint index and API specification updates.",
                        "- DB changes require database schema documentation updates.",
                        "- Architecture changes require architecture and directory documentation review.",
                        "- A task is incomplete if required documentation updates are omitted.",
                    ]
                )
            lines.extend(
                [
                    "",
                    "[docs/architecture/directory.md]",
                    "- Keep the full major directory structure current.",
                    "- Explain the role of every major directory and major file.",
                    "- Add or update entries when files move, modules split, or new layers are introduced.",
                    "- Do not describe files that do not exist.",
                    "",
                    "[docs/architecture/architecture.md]",
                    "- Explain the overall system structure.",
                    "- Include the dependency direction between layers.",
                    "- Include data flow, auth flow, API flow, persistence flow, and external integration flow when applicable.",
                    "- Record important architecture decisions that affect implementation boundaries.",
                    "",
                    "[docs/architecture/component.md]",
                    "- Describe component/module/service separation criteria.",
                    "- Distinguish shared components/modules from feature-specific components/modules.",
                    "- Explain props, DTO, service result, or module contract principles when applicable.",
                    "- State reuse criteria and ownership boundaries.",
                    "",
                    "[docs/architecture/state.md]",
                    "- Describe state/store/domain state structure.",
                    "- Define state categories such as server state, UI state, form state, auth state, job state, or domain status.",
                    "- Document state transition rules and validation ownership.",
                    "- List enum values and explain when each value is used.",
                    "",
                    "[docs/architecture/flow.md]",
                    "- Document major feature flows step by step.",
                    "- Include validation, empty state, error state, permission behavior, retry behavior, and side effects.",
                    "- Update this file when user-visible behavior or internal orchestration changes.",
                    "",
                    "[docs/api/endpoints.md]",
                    "- This file is only an endpoint index.",
                    "- Include HTTP method, URL, auth requirement, and one-line description.",
                    "- Do not write request bodies, response bodies, status code details, or long explanations here.",
                    "- Every public controller/route/API handler must appear here.",
                    "",
                    "[docs/api/specification.md]",
                    "- This file is the API contract.",
                    "- For every endpoint, include method, URL, description, auth, path params, query params, request body, response body, status codes, and error cases.",
                    "- Every request and response field must be documented with type, required/optional status, meaning, enum values, and nullability when applicable.",
                    "- Error cases must include error code, message, and occurrence condition.",
                    "- `endpoints.md` and `specification.md` must describe the same endpoint set.",
                    "",
                    "[docs/database/schema.md]",
                    "- For each table, document table name, purpose, role, owner module, and soft-delete policy.",
                    "- For each column, document name, type, description, purpose, required status, default value, index, uniqueness, and enum values when applicable.",
                    "- Document primary keys, foreign keys, relations, cardinality, delete behavior, and migration notes.",
                    "- Auth/session/token/audit tables must be explicit when authentication exists.",
                    "",
                    "[Required Update Cases]",
                    "- New API or API change.",
                    "- Request/response field change.",
                    "- Status code, error code, or auth behavior change.",
                    "- DB table, column, relation, index, enum, or migration change.",
                    "- Directory, module boundary, service flow, state model, or feature flow change.",
                    "- External integration contract, timeout, retry, fallback, or failure mapping change.",
                    "",
                    "[Prohibited]",
                    "- Omitting required documentation updates.",
                    "- Writing docs that do not match implemented behavior.",
                    "- Documenting APIs or tables that do not exist.",
                    "- Writing project specs in `.codex/ref_docs`.",
                    "- Adding endpoint details to `docs/api/endpoints.md`.",
                    "- Leaving enum values or optional/null behavior undocumented.",
                ]
            )
            return "\n".join(lines)

        lines = [
            f"# 문서화 규칙 - {config.project_name}",
            "",
            "이 프로젝트는 문서를 구현의 일부로 간주한다.",
            "프로젝트 자체에 대한 명세는 반드시 프로젝트 루트의 `docs/` 아래에 둔다.",
            "`.codex/ref_docs`는 외부 아키텍처 문서, PRD, 리서치, 벤더 문서 등 사용자가 임의로 추가하는 참고자료 공간일 뿐이다.",
            "",
            "[문서 위치]",
            "- `.codex/ai_rule_developer`: 코딩할 때 지켜야 하는 규칙.",
            "- `.codex/ref_docs`: 외부/사용자 추가 참고자료 전용. 디렉토리만 생성하고 프로젝트 명세 파일은 생성하지 않는다.",
            "- `docs/architecture`: 프로젝트 아키텍처와 흐름 문서.",
            "- `docs/api`: 엔드포인트 목록과 API 계약 문서.",
            "- `docs/database`: DB schema 문서.",
            "",
            f"[문서화 수준: {config.docs_level}]",
        ]
        if config.docs_level == "light":
            lines.extend(
                [
                    "- 동작, API 계약, DB schema, architecture, auth, external integration 동작이 바뀌면 관련 문서를 수정한다.",
                    "- 변경된 구현과 직접 관련 있는 부분 중심으로 문서를 간결하게 유지한다.",
                ]
            )
        elif config.docs_level == "standard":
            lines.extend(
                [
                    "- 코드 변경이 동작, API 계약, DB schema, architecture, auth, external integration에 영향을 주면 관련 문서를 함께 수정한다.",
                    "- `docs/architecture`, `docs/api`, `docs/database`는 실제 구현과 일치해야 한다.",
                    "- 작업 완료 전 문서 변경 필요 여부를 반드시 검토한다.",
                ]
            )
        else:
            lines.extend(
                [
                    "- 코드 변경이 동작, API 계약, DB schema, architecture, auth, external integration에 영향을 주면 문서 업데이트가 필수다.",
                    "- API 변경 시 endpoint index와 API specification을 함께 수정한다.",
                    "- DB 변경 시 database schema 문서를 반드시 수정한다.",
                    "- Architecture 변경 시 architecture 문서와 directory 문서를 함께 검토한다.",
                    "- 필요한 문서 업데이트를 생략한 작업은 완료로 보지 않는다.",
                ]
            )
        lines.extend(
            [
                "",
                "[docs/architecture/directory.md]",
                "- 전체 주요 디렉토리 구조를 최신 상태로 유지한다.",
                "- 주요 디렉토리와 주요 파일의 역할을 설명한다.",
                "- 파일 이동, 모듈 분리, 새 계층 추가 시 반드시 갱신한다.",
                "- 존재하지 않는 파일을 문서화하지 않는다.",
                "",
                "[docs/architecture/architecture.md]",
                "- 전체 시스템 구조를 설명한다.",
                "- 계층 간 의존성 방향을 포함한다.",
                "- 해당되는 경우 데이터 흐름, 인증 흐름, API 흐름, 저장 흐름, 외부 연동 흐름을 포함한다.",
                "- 구현 경계에 영향을 주는 중요한 아키텍처 결정을 기록한다.",
                "",
                "[docs/architecture/component.md]",
                "- component/module/service 분리 기준을 설명한다.",
                "- 공통 component/module과 기능 전용 component/module을 구분한다.",
                "- 해당되는 경우 props, DTO, service result, module contract 설계 원칙을 설명한다.",
                "- 재사용 기준과 소유 경계를 명확히 한다.",
                "",
                "[docs/architecture/state.md]",
                "- state/store/domain state 구조를 설명한다.",
                "- server state, UI state, form state, auth state, job state, domain status 같은 상태 종류를 정의한다.",
                "- 상태 전이 규칙과 validation 책임 위치를 문서화한다.",
                "- enum 값은 모두 나열하고 각 값이 언제 사용되는지 설명한다.",
                "",
                "[docs/architecture/flow.md]",
                "- 주요 기능 흐름을 단계별로 설명한다.",
                "- validation, empty state, error state, permission behavior, retry behavior, side effect를 포함한다.",
                "- 사용자 관찰 가능 동작이나 내부 orchestration이 바뀌면 갱신한다.",
                "",
                "[docs/api/endpoints.md]",
                "- 이 문서는 endpoint index 역할만 한다.",
                "- HTTP method, URL, auth 요구사항, 한 줄 설명만 작성한다.",
                "- request body, response body, status code 상세, 긴 설명을 작성하지 않는다.",
                "- public controller/route/API handler에 존재하는 모든 엔드포인트는 여기에 있어야 한다.",
                "",
                "[docs/api/specification.md]",
                "- 이 문서는 API 계약서 역할을 한다.",
                "- 모든 endpoint에 대해 method, URL, 설명, auth, path params, query params, request body, response body, status code, error case를 포함한다.",
                "- request/response의 모든 field는 type, 필수/선택 여부, 의미, enum 값, null 허용 여부를 명시한다.",
                "- error case는 error code, message, 발생 조건을 포함한다.",
                "- `endpoints.md`와 `specification.md`는 반드시 동일한 endpoint set을 가져야 한다.",
                "",
                "[docs/database/schema.md]",
                "- 각 table에 대해 table name, 목적, 역할, owner module, soft delete 여부를 기록한다.",
                "- 각 column에 대해 name, type, description, purpose, required 여부, default value, index, unique 여부, enum 값을 기록한다.",
                "- primary key, foreign key, relation, cardinality, delete behavior, migration note를 기록한다.",
                "- 인증이 있으면 user/session/token/audit 관련 table을 명확히 설명한다.",
                "",
                "[반드시 문서를 수정해야 하는 경우]",
                "- 새로운 API 추가 또는 기존 API 수정",
                "- Request/Response field 변경",
                "- Status code, error code, auth behavior 변경",
                "- DB table, column, relation, index, enum, migration 변경",
                "- Directory, module boundary, service flow, state model, feature flow 변경",
                "- 외부 연동 contract, timeout, retry, fallback, failure mapping 변경",
                "",
                "[금지 사항]",
                "- 필요한 문서 업데이트 생략",
                "- 실제 구현과 불일치하는 문서 작성",
                "- 존재하지 않는 API나 테이블 문서화",
                "- 프로젝트 명세를 `.codex/ref_docs`에 작성",
                "- `docs/api/endpoints.md`에 endpoint 상세 내용 작성",
                "- enum 값이나 optional/null 동작을 문서에서 생략",
            ]
        )
        return "\n".join(lines)

    def _render_domain_model_rules(self, config: ProjectConfig, profiles: tuple[FrameworkProfile, ...]) -> str:
        if config.language == "en":
            lines = [
                f"# Domain Model Rules - {config.project_name}",
                "",
                "Design domain models around explicit state and clear boundaries.",
                "",
                "[Entity Rules]",
                "- Entities represent persisted state and database mapping.",
                "- Entities must stay separate from request DTOs, response DTOs, schemas, and view models.",
                "- Do not expose entities directly through public APIs or UI-facing service results.",
                "- Entity changes require reviewing migrations, repositories, and database documentation.",
                "",
                "[DTO and Schema Rules]",
                "- Request DTOs describe input contracts.",
                "- Response DTOs describe output contracts.",
                "- DTOs may be shaped for API contracts, but entities must remain persistence-oriented.",
                "",
                "[Enum and State Rules]",
                "- Use explicit enums or constants for state values.",
                "- Do not write state strings directly in business logic.",
                "- Validate state transitions in the service/application layer before persistence.",
                "- Document allowed states and transitions in feature or database specs.",
                "",
                "[State Transition Template]",
                "- DRAFT -> READY -> QUEUED -> RUNNING -> COMPLETED",
                "- FAILED and CANCELLED must be handled as explicit terminal or recovery states when the domain uses them.",
            ]
            if config.auth_enabled:
                lines.extend(
                    [
                        "",
                        "[Auth Domain]",
                        "- Model users, roles, sessions, tokens, and audit state explicitly.",
                        "- Do not mix authentication state with unrelated domain entities.",
                    ]
                )
            for profile in profiles:
                lines.extend(["", f"[{profile.display_name} Domain Notes]"])
                lines.extend(self._bullets(self._profile_domain_rules(profile, config.language)))
            return "\n".join(lines)

        lines = [
            f"# 도메인 모델 규칙 - {config.project_name}",
            "",
            "도메인 모델은 명확한 상태와 경계를 기준으로 설계한다.",
            "",
            "[Entity 규칙]",
            "- Entity는 저장 상태와 DB 매핑을 표현한다.",
            "- Entity는 Request DTO, Response DTO, Schema, View model과 분리한다.",
            "- Entity를 public API나 UI-facing service 결과로 직접 노출하지 않는다.",
            "- Entity 변경 시 migration, repository, DB 문서를 함께 검토한다.",
            "",
            "[DTO 및 Schema 규칙]",
            "- Request DTO는 입력 계약을 표현한다.",
            "- Response DTO는 출력 계약을 표현한다.",
            "- DTO는 API 계약에 맞게 설계할 수 있지만 Entity는 persistence 중심으로 유지한다.",
            "",
            "[Enum 및 상태 규칙]",
            "- 상태값은 명시적 enum 또는 상수로 관리한다.",
            "- 비즈니스 로직에서 상태 문자열을 직접 사용하지 않는다.",
            "- 상태 전이는 Service/Application 계층에서 검증한 뒤 저장한다.",
            "- 허용 상태와 상태 전이는 기능 명세 또는 DB 명세에 문서화한다.",
            "",
            "[상태 전이 템플릿]",
            "- DRAFT -> READY -> QUEUED -> RUNNING -> COMPLETED",
            "- FAILED와 CANCELLED는 도메인에서 사용할 경우 명시적 종료 상태 또는 복구 상태로 처리한다.",
        ]
        if config.auth_enabled:
            lines.extend(
                [
                    "",
                    "[인증 도메인]",
                    "- 사용자, role, session, token, audit 상태를 명확한 모델로 표현한다.",
                    "- 인증 상태를 무관한 도메인 entity에 섞지 않는다.",
                ]
            )
        for profile in profiles:
            lines.extend(["", f"[{profile.display_name} 도메인 메모]"])
            lines.extend(self._bullets(self._profile_domain_rules(profile, config.language)))
        return "\n".join(lines)

    def _render_external_integration_rules(self, config: ProjectConfig, profiles: tuple[FrameworkProfile, ...]) -> str:
        if config.language == "en":
            lines = [
                f"# External Integration Rules - {config.project_name}",
                "",
                "External system integrations must stay behind explicit client or adapter boundaries.",
                "",
                "[Targets]",
                "- LLM APIs",
                "- Lab, simulation, batch, or worker servers",
                "- Third-party HTTP APIs or SDKs",
                "- Any system outside the current repository process",
                "",
                "[Rules]",
                "- Do not implement an integration as complete unless credentials, contract, timeout behavior, and failure mapping are known.",
                "- When the contract is missing, write only the class/method boundary and leave the body as `pass` or the language equivalent.",
                "- Add TODO comments that state required input, expected output, upstream endpoint or SDK method, timeout, retry, and error mapping.",
                "- Services call integrations through narrow methods that describe business intent.",
                "- Convert upstream DTOs into internal DTOs before returning data to callers.",
                "",
                "[Python Skeleton]",
                "```python",
                "def request_external_job(self, request_dto: ExternalJobRequestDto) -> ExternalJobResponseDto:",
                '    """Request a job from the external system."""',
                "    # TODO: define upstream endpoint, request fields, response fields, timeout, retry, and failure mapping.",
                "    pass",
                "```",
                "",
                "[Prohibited]",
                "- Fake API implementations.",
                "- Random sample data that pretends to be upstream data.",
                "- Calling external HTTP or SDK code directly from controllers or UI components.",
            ]
            if not config.external_api_enabled:
                lines.extend(
                    [
                        "",
                        "[When External APIs Are Added Later]",
                        "- Update project configuration and docs before introducing the integration.",
                    ]
                )
            for profile in profiles:
                lines.extend(["", f"[{profile.display_name} Integration Notes]"])
                lines.extend(self._bullets(self._profile_external_rules(profile, config.language)))
            return "\n".join(lines)

        lines = [
            f"# 외부 연동 규칙 - {config.project_name}",
            "",
            "외부 시스템 연동은 반드시 명시적인 client 또는 adapter 경계 뒤에 둔다.",
            "",
            "[대상]",
            "- LLM API",
            "- Lab, simulation, batch, worker server",
            "- Third-party HTTP API 또는 SDK",
            "- 현재 저장소 프로세스 밖의 모든 시스템",
            "",
            "[규칙]",
            "- 인증 정보, 계약, timeout, 실패 매핑이 확인되지 않은 연동은 완성 구현으로 작성하지 않는다.",
            "- 계약이 없으면 class/method 경계만 작성하고 본문은 `pass` 또는 해당 언어의 미구현 표현으로 둔다.",
            "- TODO 주석에는 필요한 입력, 기대 출력, upstream endpoint 또는 SDK method, timeout, retry, error mapping을 명확히 적는다.",
            "- Service는 비즈니스 의도를 드러내는 좁은 메서드로 외부 연동을 호출한다.",
            "- Upstream DTO는 내부 DTO로 변환한 뒤 호출자에게 반환한다.",
            "",
            "[Python 뼈대]",
            "```python",
            "def request_external_job(self, request_dto: ExternalJobRequestDto) -> ExternalJobResponseDto:",
            '    """외부 시스템에 작업 생성을 요청한다."""',
            "    # TODO: upstream endpoint, request field, response field, timeout, retry, failure mapping 정의 필요.",
            "    pass",
            "```",
            "",
            "[금지]",
            "- 외부 API fake 구현",
            "- upstream 데이터처럼 보이는 임의 샘플 데이터 생성",
            "- controller 또는 UI component에서 외부 HTTP/SDK 직접 호출",
        ]
        if not config.external_api_enabled:
            lines.extend(
                [
                    "",
                    "[나중에 외부 API가 추가되는 경우]",
                    "- 연동을 도입하기 전에 프로젝트 설정과 문서를 먼저 갱신한다.",
                ]
            )
        for profile in profiles:
            lines.extend(["", f"[{profile.display_name} 연동 메모]"])
            lines.extend(self._bullets(self._profile_external_rules(profile, config.language)))
        return "\n".join(lines)

    def _render_service_layer_rules(self, config: ProjectConfig, profiles: tuple[FrameworkProfile, ...]) -> str:
        if config.language == "en":
            lines = [
                f"# Service Layer Rules - {config.project_name}",
                "",
                "The service/application layer is the center of business logic.",
                "",
                "[Class and Module Rules]",
                "- Keep service classes or modules focused on one use-case area.",
                "- Prefer one primary service class per file when the framework and language conventions support it.",
                "- Inject repositories, clients, adapters, or stores through explicit constructors, factories, or narrow module boundaries.",
                "",
                "[Method Rules]",
                "- Use use-case-based method names such as `create_simulation`, `update_profile`, or `request_job`.",
                "- One method must have one responsibility.",
                "- Split logic longer than roughly ten meaningful lines into private helpers when it improves readability.",
                "",
                "[Required Flow]",
                "- Validate input and permissions.",
                "- Load or create domain/entity state.",
                "- Apply business rules and state transitions.",
                "- Persist through repository/adapter boundaries when needed.",
                "- Convert results to response DTOs, view models, or service result objects.",
                "",
                "[Prohibited]",
                "- Performing controller, route handler, or UI component responsibilities in services.",
                "- Returning repository entities directly to public callers.",
                "- Building HTTP responses inside service methods.",
                "- Mixing external API calls directly into unrelated business logic.",
                "- Cramming complex branching into one method.",
            ]
            for profile in profiles:
                lines.extend(["", f"[{profile.display_name} Service Notes]"])
                lines.extend(self._bullets(profile.framework_rules(config.language)))
            return "\n".join(lines)

        lines = [
            f"# 서비스 계층 규칙 - {config.project_name}",
            "",
            "Service/Application 계층은 비즈니스 로직의 중심이다.",
            "",
            "[클래스 및 모듈 규칙]",
            "- Service class 또는 module은 하나의 use-case 영역에 집중한다.",
            "- 언어와 프레임워크 관례가 허용하면 한 파일은 하나의 주요 service class를 책임진다.",
            "- Repository, client, adapter, store는 constructor, factory, 좁은 module boundary를 통해 명시적으로 주입한다.",
            "",
            "[메서드 규칙]",
            "- `create_simulation`, `update_profile`, `request_job`처럼 use-case 기반 네이밍을 사용한다.",
            "- 하나의 메서드는 하나의 책임만 가진다.",
            "- 의미 있는 로직이 10줄 이상 길어지면 가독성이 좋아지는 경우 private helper로 분리한다.",
            "",
            "[필수 흐름]",
            "- 입력과 권한을 검증한다.",
            "- domain/entity 상태를 조회하거나 생성한다.",
            "- 비즈니스 규칙과 상태 전이를 적용한다.",
            "- 필요한 경우 repository/adapter 경계를 통해 저장한다.",
            "- 결과를 response DTO, view model, service result 객체로 변환한다.",
            "",
            "[금지]",
            "- Service에서 controller, route handler, UI component 역할 수행",
            "- Repository entity를 public caller에게 직접 반환",
            "- Service method 내부에서 HTTP 응답 생성",
            "- 외부 API 호출을 무관한 비즈니스 로직에 직접 섞기",
            "- 복잡한 분기 로직을 하나의 메서드에 몰아넣기",
        ]
        for profile in profiles:
            lines.extend(["", f"[{profile.display_name} Service Notes]"])
            lines.extend(self._bullets(profile.framework_rules(config.language)))
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

    def _render_docs_directory(self, config: ProjectConfig, profiles: tuple[FrameworkProfile, ...]) -> str:
        if config.language == "en":
            lines = [
                f"# Directory Documentation - {config.project_name}",
                "",
                "Maintain this file as the current map of the project structure.",
                "",
                "## Required Entries",
                "- Directory path",
                "- Major file path",
                "- Responsibility",
                "- Owner layer or feature",
                "- Notes about important dependencies",
                "",
                "## Current Structure",
                "| Path | Type | Responsibility | Owner | Notes |",
                "| --- | --- | --- | --- | --- |",
            ]
            for profile in profiles:
                for directory in profile.directories:
                    lines.append(f"| `{directory}` | directory | {profile.display_name} structure placeholder | TBD | Replace with actual project role |")
            return "\n".join(lines)

        lines = [
            f"# 디렉토리 문서 - {config.project_name}",
            "",
            "이 파일은 현재 프로젝트 구조를 설명하는 기준 문서다.",
            "",
            "## 필수 작성 항목",
            "- 디렉토리 경로",
            "- 주요 파일 경로",
            "- 책임",
            "- 담당 계층 또는 기능",
            "- 중요한 의존성 메모",
            "",
            "## 현재 구조",
            "| Path | Type | Responsibility | Owner | Notes |",
            "| --- | --- | --- | --- | --- |",
        ]
        for profile in profiles:
            for directory in profile.directories:
                lines.append(f"| `{directory}` | directory | {profile.display_name} 구조 placeholder | TBD | 실제 프로젝트 역할로 교체 |")
        return "\n".join(lines)

    def _render_docs_architecture(self, config: ProjectConfig, profiles: tuple[FrameworkProfile, ...]) -> str:
        stack_names = ", ".join(profile.display_name for profile in profiles)
        database = config.database or ("Not specified" if config.language == "en" else "미지정")
        auth = self._enabled_label(config.auth_enabled, config.language)
        external_api = self._enabled_label(config.external_api_enabled, config.language)

        if config.language == "en":
            lines = [
                f"# Architecture - {config.project_name}",
                "",
                "## Summary",
                config.description or "Describe the project purpose, users, and core product value here.",
                "",
                "## Basic Information",
                f"- Stack: {stack_names}",
                f"- Database: {database}",
                f"- Authentication: {auth}",
                f"- External API integration: {external_api}",
                "",
                "## Layer Direction",
                "- Document the real dependency direction used by this project.",
                "- Explain what each layer may import and what it must not import.",
                "",
                "## Profile Architecture Notes",
            ]
            for profile in profiles:
                lines.extend(["", f"### {profile.display_name}"])
                lines.extend(self._bullets(profile.architecture(config.language)))
            lines.extend(
                [
                    "",
                    "## Flow Notes",
                    "- Data flow:",
                    "- Auth flow:",
                    "- API flow:",
                    "- Persistence flow:",
                    "- External integration flow:",
                    "",
                    "## Architecture Decisions",
                    "| Date | Decision | Reason | Impact |",
                    "| --- | --- | --- | --- |",
                ]
            )
            return "\n".join(lines)

        lines = [
            f"# 아키텍처 문서 - {config.project_name}",
            "",
            "## 요약",
            config.description or "프로젝트 목적, 사용자, 핵심 제품 가치를 여기에 작성한다.",
            "",
            "## 기본 정보",
            f"- 스택: {stack_names}",
            f"- 데이터베이스: {database}",
            f"- 인증 사용: {auth}",
            f"- 외부 API 연동: {external_api}",
            "",
            "## 계층 방향",
            "- 이 프로젝트가 실제로 사용하는 의존성 방향을 기록한다.",
            "- 각 계층이 import할 수 있는 대상과 금지 대상을 설명한다.",
            "",
            "## 프로필별 아키텍처 메모",
        ]
        for profile in profiles:
            lines.extend(["", f"### {profile.display_name}"])
            lines.extend(self._bullets(profile.architecture(config.language)))
        lines.extend(
            [
                "",
                "## 흐름 메모",
                "- 데이터 흐름:",
                "- 인증 흐름:",
                "- API 흐름:",
                "- 저장 흐름:",
                "- 외부 연동 흐름:",
                "",
                "## 아키텍처 결정",
                "| Date | Decision | Reason | Impact |",
                "| --- | --- | --- | --- |",
            ]
        )
        return "\n".join(lines)

    def _render_docs_component(self, config: ProjectConfig, profiles: tuple[FrameworkProfile, ...]) -> str:
        if config.language == "en":
            lines = [
                f"# Component and Module Documentation - {config.project_name}",
                "",
                "Use this file to document how project units are separated and reused.",
                "",
                "## Separation Criteria",
                "- Shared units:",
                "- Feature-specific units:",
                "- Service/application units:",
                "- Repository/adapter units:",
                "- UI or presentation units:",
                "",
                "## Contract Rules",
                "- Props or input model rules:",
                "- Output/result model rules:",
                "- Reuse criteria:",
                "- Ownership boundary:",
                "",
                "## Profile Notes",
            ]
        else:
            lines = [
                f"# 컴포넌트 및 모듈 문서 - {config.project_name}",
                "",
                "프로젝트 단위를 어떻게 분리하고 재사용하는지 기록한다.",
                "",
                "## 분리 기준",
                "- 공통 단위:",
                "- 기능 전용 단위:",
                "- Service/Application 단위:",
                "- Repository/Adapter 단위:",
                "- UI 또는 Presentation 단위:",
                "",
                "## 계약 규칙",
                "- Props 또는 입력 모델 규칙:",
                "- 출력/result 모델 규칙:",
                "- 재사용 기준:",
                "- 소유 경계:",
                "",
                "## 프로필 메모",
            ]
        for profile in profiles:
            lines.extend(["", f"### {profile.display_name}"])
            lines.extend(self._bullets(profile.framework_rules(config.language)))
        return "\n".join(lines)

    def _render_docs_state(self, config: ProjectConfig) -> str:
        if config.language == "en":
            lines = [
                f"# State Documentation - {config.project_name}",
                "",
                "Document all important state models and state transitions here.",
                "",
                "## State Categories",
                "| State | Owner | Source of Truth | Persisted | Notes |",
                "| --- | --- | --- | --- | --- |",
                "",
                "## Enum Values",
                "| Enum | Value | Meaning | Terminal | Notes |",
                "| --- | --- | --- | --- | --- |",
                "",
                "## Transition Rules",
                "| From | To | Trigger | Validator | Side Effects |",
                "| --- | --- | --- | --- | --- |",
            ]
            if config.auth_enabled:
                lines.extend(["", "## Auth State", "- Document session, token, role, and permission state here."])
            return "\n".join(lines)

        lines = [
            f"# 상태 문서 - {config.project_name}",
            "",
            "중요한 상태 모델과 상태 전이를 이 문서에 기록한다.",
            "",
            "## 상태 종류",
            "| State | Owner | Source of Truth | Persisted | Notes |",
            "| --- | --- | --- | --- | --- |",
            "",
            "## Enum 값",
            "| Enum | Value | Meaning | Terminal | Notes |",
            "| --- | --- | --- | --- | --- |",
            "",
            "## 상태 전이 규칙",
            "| From | To | Trigger | Validator | Side Effects |",
            "| --- | --- | --- | --- | --- |",
        ]
        if config.auth_enabled:
            lines.extend(["", "## 인증 상태", "- session, token, role, permission 상태를 여기에 기록한다."])
        return "\n".join(lines)

    def _render_docs_flow(self, config: ProjectConfig) -> str:
        if config.language == "en":
            return "\n".join(
                [
                    f"# Flow Documentation - {config.project_name}",
                    "",
                    "Document major feature flows step by step.",
                    "",
                    "## Flow Template",
                    "### Flow Name",
                    "- Actor:",
                    "- Entry point:",
                    "- Preconditions:",
                    "- Steps:",
                    "- Validation:",
                    "- Empty state:",
                    "- Error state:",
                    "- Permission behavior:",
                    "- Retry or recovery:",
                    "- Side effects:",
                    "- Related API:",
                    "- Related DB tables:",
                ]
            )

        return "\n".join(
            [
                f"# 흐름 문서 - {config.project_name}",
                "",
                "주요 기능 흐름을 단계별로 기록한다.",
                "",
                "## 흐름 템플릿",
                "### Flow Name",
                "- Actor:",
                "- Entry point:",
                "- Preconditions:",
                "- Steps:",
                "- Validation:",
                "- Empty state:",
                "- Error state:",
                "- Permission behavior:",
                "- Retry or recovery:",
                "- Side effects:",
                "- Related API:",
                "- Related DB tables:",
            ]
        )

    def _render_docs_api_endpoints(self, config: ProjectConfig) -> str:
        if config.language == "en":
            return "\n".join(
                [
                    f"# Endpoint Index - {config.project_name}",
                    "",
                    "This file is an index only. Do not write request/response details here.",
                    "",
                    "| Method | URL | Auth | Description |",
                    "| --- | --- | --- | --- |",
                    "| GET | /health | public | Health check |",
                ]
            )

        return "\n".join(
            [
                f"# 엔드포인트 목록 - {config.project_name}",
                "",
                "이 문서는 목록 전용이다. Request/Response 상세를 작성하지 않는다.",
                "",
                "| Method | URL | Auth | 설명 |",
                "| --- | --- | --- | --- |",
                "| GET | /health | public | 상태 확인 |",
            ]
        )

    def _render_docs_api_specification(self, config: ProjectConfig) -> str:
        if config.language == "en":
            lines = [
                f"# API Specification - {config.project_name}",
                "",
                "Document the exact API contract here.",
                "",
                "## Endpoint Template",
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
                lines.extend(["", "## Auth Contract", "- Document token/session format, refresh rules, expiration, and required headers."])
            if config.external_api_enabled:
                lines.extend(["", "## External API Mapping", "- Document internal endpoint to upstream call mapping only when the upstream contract is known."])
            return "\n".join(lines)

        lines = [
            f"# API 명세 - {config.project_name}",
            "",
            "정확한 API 계약을 이 문서에 기록한다.",
            "",
            "## 엔드포인트 템플릿",
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
            lines.extend(["", "## 인증 계약", "- token/session 형식, refresh 규칙, 만료, 필수 header를 기록한다."])
        if config.external_api_enabled:
            lines.extend(["", "## 외부 API 매핑", "- upstream 계약이 확인된 경우에만 내부 endpoint와 upstream 호출 관계를 기록한다."])
        return "\n".join(lines)

    def _render_docs_database_schema(self, config: ProjectConfig) -> str:
        database = config.database or ("Not specified" if config.language == "en" else "미지정")
        if config.language == "en":
            lines = [
                f"# Database Schema - {config.project_name}",
                "",
                f"- Database: {database}",
                "",
                "## Table Template",
                "### table_name",
                "- Purpose:",
                "- Owner module:",
                "- Soft delete:",
                "- Migration:",
                "",
                "| Column | Type | Required | Default | Index | Unique | Description |",
                "| --- | --- | --- | --- | --- | --- | --- |",
                "",
                "## Relationships",
                "| From | To | Cardinality | Delete Behavior | Notes |",
                "| --- | --- | --- | --- | --- |",
                "",
                "## Enum Values",
                "| Table | Column | Value | Meaning |",
                "| --- | --- | --- | --- |",
            ]
            if config.auth_enabled:
                lines.extend(["", "## Auth Tables", "- Document users, roles, sessions, tokens, and audit-related tables when they exist."])
            return "\n".join(lines)

        lines = [
            f"# DB Schema - {config.project_name}",
            "",
            f"- 데이터베이스: {database}",
            "",
            "## 테이블 템플릿",
            "### table_name",
            "- 목적:",
            "- 담당 모듈:",
            "- Soft delete:",
            "- Migration:",
            "",
            "| Column | Type | Required | Default | Index | Unique | Description |",
            "| --- | --- | --- | --- | --- | --- | --- |",
            "",
            "## 관계",
            "| From | To | Cardinality | Delete Behavior | Notes |",
            "| --- | --- | --- | --- | --- |",
            "",
            "## Enum 값",
            "| Table | Column | Value | Meaning |",
            "| --- | --- | --- | --- |",
        ]
        if config.auth_enabled:
            lines.extend(["", "## 인증 관련 테이블", "- users, roles, sessions, tokens, audit 관련 테이블이 있으면 문서화한다."])
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
                    "You are starting work in this repository.",
                    "",
                    "Before doing any task, follow this order.",
                    "",
                    "1. Read the `.codex` folder and its child documents first, and use them as the highest-priority repository rules.",
                    "2. Prioritize these document types:",
                    "   - Global coding rules",
                    "   - Architecture rules",
                    "   - Service layer rules",
                    "   - External integration rules",
                    "   - API design rules",
                    "   - Domain/DB model rules",
                    "   - Project specifications inside root `docs/`",
                    "   - External architecture notes, PRDs, and user-added reference documents inside `.codex/ref_docs`",
                    "3. If documents conflict, use this priority order:",
                    "   - The user's current request",
                    "   - `.codex/ai_rule_developer/GLOBAL_RULES.md`",
                    "   - Task-specific rules inside `.codex/ai_rule_developer`",
                    "   - Project specifications inside root `docs/`",
                    "   - External architecture notes, PRDs, and user-added reference documents inside `.codex/ref_docs`",
                    "   - Other supporting documents",
                    "4. Before working, classify the current request as one of these task types:",
                    "   - Architecture design",
                    "   - Entity/schema design",
                    "   - API design",
                    "   - Service logic",
                    "   - Controller/route/UI boundary work",
                    "   - External integration skeleton",
                    "   - Refactoring",
                    "   - Documentation",
                    "5. Apply the `.codex` rules that match the task type before editing files.",
                    "",
                    "Core principles for this repository:",
                    f"- Project name: {config.project_name}",
                    f"- Stack: {', '.join(config.stack)}",
                    "- Keep responsibilities separated by layer.",
                    "- Do not put business logic in presentation, controller, route, or UI boundaries.",
                    "- Do not mix entities, DTOs, schemas, domain models, and view models.",
                    "- Do not invent behavior that is not defined by the request or reference documents.",
                    "- Do not treat `.codex/ref_docs` as generated project documentation; it is a user-managed reference space.",
                    "- Keep project specs in root `docs/`.",
                    "- For external integrations without a confirmed contract, write only class/method boundaries and TODOs; leave the body unimplemented.",
                    "- After code changes, update required documentation in the same task.",
                    "",
                    "Response behavior:",
                    "- First state the task type you selected.",
                    "- Then state which `.codex` rules you applied.",
                    "- Then provide the result, organized by file path when files changed.",
                ]
            )

        return "\n".join(
            [
                "지금부터 이 저장소의 작업을 시작한다.",
                "",
                "작업을 시작하기 전에 반드시 아래 순서대로 동작하라.",
                "",
                "1. `.codex` 폴더와 그 하위 문서들을 먼저 확인하고, 그 문서들을 이번 작업의 최우선 저장소 규칙으로 사용하라.",
                "2. 특히 다음 종류의 문서를 우선적으로 읽고 반영하라.",
                "   - 전역 코딩 규칙",
                "   - 아키텍처 규칙",
                "   - 서비스 계층 규칙",
                "   - 외부 연동 규칙",
                "   - API 설계 규칙",
                "   - 도메인/DB 모델 규칙",
                "   - 프로젝트 루트 `docs/` 내부의 프로젝트 명세",
                "   - `.codex/ref_docs` 내부의 외부 아키텍처, PRD, 사용자 추가 참고자료",
                "3. 문서 간 충돌이 있으면 다음 우선순위로 판단하라.",
                "   - 사용자의 현재 요청",
                "   - `.codex/ai_rule_developer/GLOBAL_RULES.md`",
                "   - `.codex/ai_rule_developer` 내부의 작업 유형별 규칙",
                "   - 프로젝트 루트 `docs/` 내부의 프로젝트 명세",
                "   - `.codex/ref_docs` 내부의 외부 아키텍처, PRD, 사용자 추가 참고자료",
                "   - 기타 보조 문서",
                "4. 작업 전에 반드시 현재 요청이 아래 중 무엇인지 스스로 판단하라.",
                "   - 아키텍처 설계",
                "   - 엔티티/스키마 설계",
                "   - API 설계",
                "   - 서비스 로직 작성",
                "   - 컨트롤러/라우트/UI 경계 작업",
                "   - 외부 연동 메서드 뼈대 작성",
                "   - 리팩토링",
                "   - 문서화",
                "5. 판단한 작업 유형에 맞는 `.codex` 규칙을 우선 적용하라.",
                "",
                "이번 저장소에서 반드시 지켜야 하는 핵심 원칙은 다음과 같다.",
                "",
                f"- 프로젝트 이름: {config.project_name}",
                f"- 스택: {', '.join(config.stack)}",
                "- 계층별 책임을 반드시 분리한다.",
                "- Presentation, Controller, Route, UI 경계에 비즈니스 로직을 넣지 않는다.",
                "- Entity, DTO, Schema, Domain model, View model을 혼용하지 않는다.",
                "- 요청이나 참고 문서에 없는 기능을 임의로 추가하지 않는다.",
                "- `.codex/ref_docs`를 생성된 프로젝트 명세 위치로 취급하지 않는다. 이 위치는 사용자 관리 참고자료 공간이다.",
                "- 프로젝트 명세는 프로젝트 루트의 `docs/`에 유지한다.",
                "- 계약이 확인되지 않은 외부 연동은 class/method 경계와 TODO만 작성하고 본문은 미구현으로 둔다.",
                "- 코드 수정 후 필요한 문서도 같은 작업 안에서 함께 수정한다.",
                "",
                "응답 방식도 아래를 따라라.",
                "",
                "- 먼저 현재 작업을 어떤 유형으로 판단했는지 짧게 정리한다.",
                "- 그 다음 어떤 `.codex` 규칙을 우선 적용했는지 짧게 정리한다.",
                "- 이후 결과물을 작성한다.",
                "- 파일 변경이 있으면 파일 경로 단위로 구분해서 보여준다.",
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

    def _profile_domain_rules(self, profile: FrameworkProfile, language: str) -> tuple[str, ...]:
        if language == "en":
            rules: dict[str, tuple[str, ...]] = {
                "fastapi": (
                    "Keep SQLAlchemy/SQLModel entities separate from Pydantic request and response schemas.",
                    "Validate use-case state transitions in services, not in routers.",
                    "Repository methods return persistence models or repository result objects; controllers receive response schemas only after mapping.",
                ),
                "python": (
                    "Use dataclasses, typed dicts, or explicit classes for domain models instead of loose dictionaries.",
                    "Keep pure domain objects independent from filesystem, environment, network, and process args.",
                    "Represent CLI input as a separate input model before passing it to domain or service logic.",
                ),
                "springboot": (
                    "Keep JPA entities separate from request and response DTOs.",
                    "Use enum types for persistent state and document database column values.",
                    "Apply transaction-sensitive state transitions in service methods.",
                ),
                "react": (
                    "Separate API response types from UI view models.",
                    "Keep form state, server state, and global UI state distinct.",
                    "Do not mutate domain-like state directly inside presentational components.",
                ),
                "nextjs": (
                    "Separate server data models from client component view models.",
                    "Keep server action inputs validated before changing state.",
                    "Document cache and revalidation assumptions for state derived from server data.",
                ),
                "node-express": (
                    "Keep database records separate from request/response DTOs.",
                    "Validate state transitions in services before repository writes.",
                    "Use explicit error/result models for domain failures.",
                ),
                "fullstack-fastapi-react": (
                    "Keep backend entities, backend schemas, frontend API types, and frontend view models separate.",
                    "Document shared enum values in backend, frontend, and docs together.",
                    "API contract changes must update both backend schema mapping and frontend service types.",
                ),
            }
            return rules.get(profile.key, ("Keep framework domain models separate from external contracts.",))

        rules = {
            "fastapi": (
                "SQLAlchemy/SQLModel Entity와 Pydantic Request/Response Schema를 분리한다.",
                "유스케이스 상태 전이는 router가 아니라 service에서 검증한다.",
                "Repository method는 persistence model 또는 repository result 객체를 반환하고, controller는 mapping 이후 response schema만 받는다.",
            ),
            "python": (
                "느슨한 dictionary 대신 dataclass, typed dict, 명시적 class로 domain model을 표현한다.",
                "순수 domain object는 filesystem, environment, network, process args에 의존하지 않는다.",
                "CLI 입력은 domain/service logic에 전달하기 전에 별도 input model로 변환한다.",
            ),
            "springboot": (
                "JPA Entity와 Request/Response DTO를 분리한다.",
                "영속 상태는 enum type으로 관리하고 DB column 값을 문서화한다.",
                "transaction이 필요한 상태 전이는 service method에서 적용한다.",
            ),
            "react": (
                "API response type과 UI view model을 분리한다.",
                "form state, server state, global UI state를 구분한다.",
                "presentational component 내부에서 domain-like state를 직접 변경하지 않는다.",
            ),
            "nextjs": (
                "server data model과 client component view model을 분리한다.",
                "server action 입력은 상태 변경 전에 검증한다.",
                "server data에서 파생되는 상태는 cache와 revalidation 가정을 문서화한다.",
            ),
            "node-express": (
                "DB record와 Request/Response DTO를 분리한다.",
                "Repository write 전에 service에서 상태 전이를 검증한다.",
                "Domain failure는 명시적 error/result model로 표현한다.",
            ),
            "fullstack-fastapi-react": (
                "Backend Entity, Backend Schema, Frontend API Type, Frontend View Model을 분리한다.",
                "공유 enum 값은 backend, frontend, docs를 함께 갱신한다.",
                "API contract 변경은 backend schema mapping과 frontend service type을 함께 수정한다.",
            ),
        }
        return rules.get(profile.key, ("Framework domain model과 외부 계약을 분리한다.",))

    def _profile_external_rules(self, profile: FrameworkProfile, language: str) -> tuple[str, ...]:
        if language == "en":
            rules: dict[str, tuple[str, ...]] = {
                "fastapi": (
                    "Routers must not call external HTTP clients directly.",
                    "Put upstream calls in client/adapter classes below the service layer.",
                    "Map upstream failures to service exceptions before converting them to HTTP responses.",
                ),
                "python": (
                    "Keep filesystem, subprocess, network, and environment integrations behind adapter modules.",
                    "Use typed request/result objects for adapter boundaries.",
                    "Do not run external calls at import time.",
                ),
                "springboot": (
                    "Use dedicated client beans for upstream HTTP/SDK calls.",
                    "Keep retry, timeout, and circuit behavior outside controllers.",
                    "Map external failures to service/domain exceptions before ControllerAdvice handles them.",
                ),
                "react": (
                    "Components must call local services/hooks, not raw external APIs.",
                    "Normalize API errors in the service layer before they reach screens.",
                    "Keep browser token handling in one explicit auth service/store boundary.",
                ),
                "nextjs": (
                    "Server actions and route handlers own external calls; client components must not call private upstream systems.",
                    "Separate server-only secrets from public environment variables.",
                    "Document cache/revalidate behavior for external data.",
                ),
                "node-express": (
                    "Controllers call services, and services call dedicated upstream clients.",
                    "Centralize timeout, retry, and failure mapping in adapter/client modules.",
                    "Do not pass Express req/res objects into external clients.",
                ),
                "fullstack-fastapi-react": (
                    "Backend owns private upstream integrations; frontend calls backend services only.",
                    "Document any backend-to-upstream mapping in docs/api/specification.md when it affects public behavior.",
                    "Keep frontend mocks aligned with backend API contracts.",
                ),
            }
            return rules.get(profile.key, ("Keep external integrations behind framework-appropriate adapter boundaries.",))

        rules = {
            "fastapi": (
                "Router는 외부 HTTP client를 직접 호출하지 않는다.",
                "Upstream 호출은 service 하위의 client/adapter class에 둔다.",
                "Upstream 실패는 HTTP 응답으로 바꾸기 전에 service exception으로 매핑한다.",
            ),
            "python": (
                "Filesystem, subprocess, network, environment 연동은 adapter module 뒤에 둔다.",
                "Adapter 경계에는 typed request/result object를 사용한다.",
                "import 시점에 외부 호출을 실행하지 않는다.",
            ),
            "springboot": (
                "Upstream HTTP/SDK 호출은 전용 client bean으로 분리한다.",
                "Retry, timeout, circuit 동작은 controller 밖에서 관리한다.",
                "외부 실패는 ControllerAdvice가 처리하기 전에 service/domain exception으로 매핑한다.",
            ),
            "react": (
                "Component는 raw external API가 아니라 local service/hook을 호출한다.",
                "API error는 화면에 도달하기 전에 service layer에서 정규화한다.",
                "브라우저 token 처리는 명시적 auth service/store 경계 한 곳에서 관리한다.",
            ),
            "nextjs": (
                "Server action과 route handler가 외부 호출을 담당하며 client component는 private upstream system을 직접 호출하지 않는다.",
                "Server-only secret과 public environment variable을 분리한다.",
                "External data의 cache/revalidate 동작을 문서화한다.",
            ),
            "node-express": (
                "Controller는 service를 호출하고 service는 전용 upstream client를 호출한다.",
                "Timeout, retry, failure mapping은 adapter/client module에 모은다.",
                "Express req/res 객체를 external client로 넘기지 않는다.",
            ),
            "fullstack-fastapi-react": (
                "Private upstream integration은 backend가 소유하고 frontend는 backend service만 호출한다.",
                "공개 동작에 영향을 주는 backend-to-upstream mapping은 docs/api/specification.md에 문서화한다.",
                "Frontend mock은 backend API contract와 불일치하지 않게 관리한다.",
            ),
        }
        return rules.get(profile.key, ("외부 연동은 framework에 맞는 adapter 경계 뒤에 둔다.",))

    def _bullets(self, values: tuple[str, ...]) -> list[str]:
        return [f"- {value}" for value in values]

    def _enabled_label(self, enabled: bool, language: str) -> str:
        if language == "en":
            return "yes" if enabled else "no"
        return "사용" if enabled else "미사용"
