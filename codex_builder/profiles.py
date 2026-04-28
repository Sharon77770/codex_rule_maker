"""Framework profile definitions used by the document renderer."""

from __future__ import annotations

from dataclasses import dataclass


class UnknownProfileError(ValueError):
    """Raised when a stack profile is not supported."""


@dataclass(frozen=True)
class FrameworkProfile:
    """Rules and notes for a supported framework or stack profile."""

    key: str
    display_name: str
    philosophy_ko: str
    philosophy_en: str
    architecture_ko: tuple[str, ...]
    architecture_en: tuple[str, ...]
    framework_rules_ko: tuple[str, ...]
    framework_rules_en: tuple[str, ...]
    api_rules_ko: tuple[str, ...]
    api_rules_en: tuple[str, ...]
    test_rules_ko: tuple[str, ...]
    test_rules_en: tuple[str, ...]
    directories: tuple[str, ...]

    def philosophy(self, language: str) -> str:
        return self.philosophy_en if language == "en" else self.philosophy_ko

    def architecture(self, language: str) -> tuple[str, ...]:
        return self.architecture_en if language == "en" else self.architecture_ko

    def framework_rules(self, language: str) -> tuple[str, ...]:
        return self.framework_rules_en if language == "en" else self.framework_rules_ko

    def api_rules(self, language: str) -> tuple[str, ...]:
        return self.api_rules_en if language == "en" else self.api_rules_ko

    def test_rules(self, language: str) -> tuple[str, ...]:
        return self.test_rules_en if language == "en" else self.test_rules_ko


PYTHON_PROFILE = FrameworkProfile(
    key="python",
    display_name="Python",
    philosophy_ko="일반 Python 프로젝트는 프레임워크 전제 없이 package/module, service, adapter, CLI 경계를 명확히 분리한다.",
    philosophy_en="General Python projects should separate package/module, service, adapter, and CLI boundaries without assuming a framework.",
    architecture_ko=(
        "패키지는 기능 또는 도메인 책임 기준으로 나누고 임시 script 모음처럼 방치하지 않는다.",
        "CLI 또는 실행 진입점은 입력 파싱과 출력 변환만 담당하고 실제 판단은 service/application 계층에 위임한다.",
        "핵심 도메인 함수와 클래스는 파일 시스템, 네트워크, 환경 변수, process args에 직접 의존하지 않게 한다.",
        "파일, DB, 외부 API, subprocess 연동은 adapter 또는 infrastructure 모듈 뒤에 둔다.",
        "권장 흐름: Entrypoint/CLI -> Application Service -> Domain/Adapter -> External System.",
    ),
    architecture_en=(
        "Split packages by feature or domain responsibility instead of leaving them as loose script collections.",
        "CLI or runtime entrypoints should only parse input and map output, then delegate decisions to service/application layers.",
        "Keep core domain functions and classes independent from filesystem, network, environment variables, and process args.",
        "Put filesystem, database, external API, and subprocess integrations behind adapter or infrastructure modules.",
        "Recommended flow: Entrypoint/CLI -> Application Service -> Domain/Adapter -> External System.",
    ),
    framework_rules_ko=(
        "import 시점에 파일 생성, 네트워크 호출, 프로세스 실행 같은 부수효과가 발생하지 않게 한다.",
        "실행 가능한 모듈은 `main()` 진입점을 제공하고 직접 실행 코드는 `if __name__ == \"__main__\"` 아래에 둔다.",
        "표준 라이브러리로 충분한 문제에 불필요한 dependency를 추가하지 않는다.",
        "공개 함수와 클래스에는 의미 있는 타입 힌트를 유지하고, 입력/출력 모델은 명확한 자료 구조로 표현한다.",
        "순수 계산 로직과 I/O 로직을 분리해 테스트와 재사용이 가능하게 한다.",
    ),
    framework_rules_en=(
        "Avoid import-time side effects such as file creation, network calls, or process execution.",
        "Runnable modules should expose a `main()` entrypoint and keep direct execution under `if __name__ == \"__main__\"`.",
        "Do not add dependencies when the standard library is enough for the problem.",
        "Keep meaningful type hints on public functions and classes, and represent input/output models with explicit data structures.",
        "Separate pure computation from I/O so logic stays testable and reusable.",
    ),
    api_rules_ko=(
        "공개 함수, 클래스, CLI 옵션은 외부 계약으로 보고 이름과 반환 형식을 안정적으로 관리한다.",
        "외부 입력은 진입점에서 검증하고 내부 모델로 변환한 뒤 service 계층에 전달한다.",
        "예외는 호출자가 처리할 수 있는 명확한 타입 또는 메시지로 표현한다.",
    ),
    api_rules_en=(
        "Treat public functions, classes, and CLI options as external contracts with stable names and return shapes.",
        "Validate external input at the entrypoint and convert it into internal models before passing it to services.",
        "Represent errors with clear exception types or messages that callers can handle.",
    ),
    test_rules_ko=(
        "순수 로직 테스트와 파일/네트워크/환경 변수 I/O 테스트를 분리한다.",
        "`tmp_path`, monkeypatch, test double을 사용해 파일 시스템과 외부 의존성을 격리한다.",
        "CLI 인자, 설정 파싱, 오류 경로는 회귀 테스트로 고정한다.",
    ),
    test_rules_en=(
        "Separate tests for pure logic from tests that cover filesystem, network, or environment I/O.",
        "Use `tmp_path`, monkeypatching, and test doubles to isolate filesystem and external dependencies.",
        "Lock down CLI arguments, configuration parsing, and error paths with regression tests.",
    ),
    directories=("src/<package_name>", "src/<package_name>/services", "src/<package_name>/adapters", "tests", "scripts"),
)


FASTAPI_PROFILE = FrameworkProfile(
    key="fastapi",
    display_name="FastAPI",
    philosophy_ko="FastAPI의 가벼운 실행 모델은 유지하되, 코드는 Controller, Service, Repository, Schema, Entity 계층으로 분리한다.",
    philosophy_en="Keep FastAPI's lightweight runtime model, but separate code into Controller, Service, Repository, Schema, and Entity layers.",
    architecture_ko=(
        "HTTP 엔드포인트는 controller/router 계층에 두고 비즈니스 판단은 service 계층으로 위임한다.",
        "service 계층은 유스케이스 단위 메서드를 제공하고 repository 또는 외부 연동 client를 조합한다.",
        "repository 계층은 DB 접근만 담당하며 HTTP 요청/응답 객체를 알지 못해야 한다.",
        "Pydantic schema는 요청/응답 계약이고 ORM entity는 저장 모델이다. 두 모델을 혼용하지 않는다.",
        "권장 흐름: Controller -> Service -> Repository -> DB.",
    ),
    architecture_en=(
        "Place HTTP endpoints in the controller/router layer and delegate business decisions to services.",
        "Services expose use-case methods and coordinate repositories or external clients.",
        "Repositories only handle database access and must not know HTTP request/response objects.",
        "Pydantic schemas are request/response contracts and ORM entities are persistence models. Do not mix them.",
        "Recommended flow: Controller -> Service -> Repository -> DB.",
    ),
    framework_rules_ko=(
        "APIRouter는 라우팅과 의존성 연결만 담당한다.",
        "Service가 FastAPI Response, Depends, Request에 직접 의존하지 않게 한다.",
        "Repository는 SQLAlchemy, SQLModel 등 실제 저장소 API를 감싸는 경계로 둔다.",
        "예외는 도메인/서비스 예외로 먼저 표현하고 controller에서 HTTP 상태로 변환한다.",
        "배경 작업, 외부 호출, 긴 작업은 service 하위의 명시적 adapter/client로 분리한다.",
    ),
    framework_rules_en=(
        "APIRouter should only handle routing and dependency wiring.",
        "Services should not directly depend on FastAPI Response, Depends, or Request.",
        "Repositories wrap storage APIs such as SQLAlchemy or SQLModel.",
        "Represent errors as domain/service exceptions first, then map them to HTTP statuses in controllers.",
        "Move background jobs, external calls, and long-running work into explicit adapters/clients below services.",
    ),
    api_rules_ko=(
        "응답 모델은 response_model 또는 명시적 schema로 고정한다.",
        "입력 검증은 schema에서 시작하고 유스케이스 검증은 service에서 수행한다.",
        "엔드포인트 경로는 리소스 명사 중심으로 작성한다.",
    ),
    api_rules_en=(
        "Pin response contracts with response_model or explicit schemas.",
        "Start input validation in schemas and perform use-case validation in services.",
        "Use resource nouns in endpoint paths.",
    ),
    test_rules_ko=(
        "Service 테스트는 repository/client를 대체 객체로 격리한다.",
        "API 테스트는 TestClient 또는 httpx 기반으로 요청/응답 계약을 검증한다.",
        "Repository 테스트는 DB 스키마와 쿼리 동작을 별도로 검증한다.",
    ),
    test_rules_en=(
        "Isolate service tests with repository/client doubles.",
        "Use TestClient or httpx-based API tests to verify request/response contracts.",
        "Verify repository tests against database schema and query behavior separately.",
    ),
    directories=("app/controllers", "app/services", "app/repositories", "app/schemas", "app/entities", "app/core"),
)

SPRINGBOOT_PROFILE = FrameworkProfile(
    key="springboot",
    display_name="Spring Boot",
    philosophy_ko="Spring Boot 프로젝트는 Controller, Service, Repository, Entity, DTO 계층과 명시적 의존성 주입을 기준으로 유지한다.",
    philosophy_en="Spring Boot projects should keep explicit Controller, Service, Repository, Entity, and DTO layers with dependency injection.",
    architecture_ko=(
        "Controller는 HTTP 요청/응답과 인증 컨텍스트 연결만 담당한다.",
        "Service는 트랜잭션 경계와 비즈니스 규칙의 중심이다.",
        "Repository는 JPA 또는 데이터 접근 인터페이스로 제한한다.",
        "Entity는 DB 영속성 모델이고 DTO는 API 계약이다. Entity를 외부 응답으로 직접 노출하지 않는다.",
        "권장 흐름: Controller -> Service -> Repository -> DB.",
    ),
    architecture_en=(
        "Controllers handle HTTP request/response mapping and security context wiring only.",
        "Services own transaction boundaries and business rules.",
        "Repositories are limited to JPA or data access interfaces.",
        "Entities are persistence models and DTOs are API contracts. Never expose entities directly in external responses.",
        "Recommended flow: Controller -> Service -> Repository -> DB.",
    ),
    framework_rules_ko=(
        "생성자 주입을 기본으로 사용한다.",
        "@Transactional은 비즈니스 유스케이스가 있는 service 계층에 둔다.",
        "ControllerAdvice 또는 공통 예외 처리기로 오류 응답을 일관화한다.",
        "Entity 변경은 migration과 DB 문서 변경을 함께 검토한다.",
    ),
    framework_rules_en=(
        "Prefer constructor injection.",
        "Place @Transactional on service-layer use cases.",
        "Use ControllerAdvice or a shared exception handler for consistent error responses.",
        "Review migrations and DB documentation together with entity changes.",
    ),
    api_rules_ko=(
        "Request DTO와 Response DTO를 분리한다.",
        "상태 코드는 Controller에서 명시적으로 결정한다.",
        "Bean Validation을 DTO 입력 계약에 적용한다.",
    ),
    api_rules_en=(
        "Separate request DTOs from response DTOs.",
        "Choose HTTP status codes explicitly in controllers.",
        "Apply Bean Validation to DTO input contracts.",
    ),
    test_rules_ko=(
        "Service는 단위 테스트로 비즈니스 규칙을 검증한다.",
        "Controller는 WebMvcTest 또는 통합 테스트로 API 계약을 검증한다.",
        "Repository는 필요한 경우 DataJpaTest로 쿼리와 매핑을 검증한다.",
    ),
    test_rules_en=(
        "Verify business rules with service unit tests.",
        "Verify API contracts with WebMvcTest or integration tests.",
        "Use DataJpaTest when repository queries and mappings need verification.",
    ),
    directories=("src/main/java/.../controller", "src/main/java/.../service", "src/main/java/.../repository", "src/main/java/.../entity", "src/main/java/.../dto"),
)

REACT_PROFILE = FrameworkProfile(
    key="react",
    display_name="React",
    philosophy_ko="React 코드는 화면, 컴포넌트, 훅, 서비스, 상태 저장소를 분리하고 UI와 데이터 접근을 섞지 않는다.",
    philosophy_en="React code should separate pages, components, hooks, services, and stores without mixing UI and data access.",
    architecture_ko=(
        "page는 라우팅 단위 화면 조립을 담당한다.",
        "component는 재사용 가능한 UI와 표시 책임을 담당한다.",
        "hook은 화면 상태, 비동기 흐름, UI 유스케이스를 캡슐화한다.",
        "service는 API 호출과 외부 클라이언트 경계만 담당한다.",
        "store는 전역 상태를 담당하고 서버 응답 원본을 무분별하게 복제하지 않는다.",
        "권장 흐름: Page -> Hook/Store -> Service -> API.",
    ),
    architecture_en=(
        "Pages compose route-level screens.",
        "Components own reusable UI and presentation.",
        "Hooks encapsulate screen state, async flow, and UI use cases.",
        "Services own API calls and external client boundaries only.",
        "Stores own global state and should not blindly duplicate raw server responses.",
        "Recommended flow: Page -> Hook/Store -> Service -> API.",
    ),
    framework_rules_ko=(
        "컴포넌트 안에서 fetch/axios 호출을 직접 수행하지 않는다.",
        "복잡한 상태 전이는 hook 또는 store action으로 분리한다.",
        "공통 UI 컴포넌트와 기능 전용 컴포넌트를 분리한다.",
        "API 타입과 UI view model의 변환 위치를 명확히 둔다.",
    ),
    framework_rules_en=(
        "Do not call fetch/axios directly inside components.",
        "Move complex state transitions into hooks or store actions.",
        "Separate shared UI components from feature-specific components.",
        "Keep API types and UI view-model mapping in an explicit location.",
    ),
    api_rules_ko=(
        "service 함수는 HTTP 세부사항을 감추고 typed result를 반환한다.",
        "API 오류는 화면에서 직접 문자열 조립하지 말고 공통 오류 모델로 변환한다.",
        "인증 토큰 저장, 갱신, 만료 처리는 한 계층에서 일관되게 관리한다.",
    ),
    api_rules_en=(
        "Service functions hide HTTP details and return typed results.",
        "Convert API errors to a shared error model instead of hand-building strings in screens.",
        "Manage auth token storage, refresh, and expiration consistently in one layer.",
    ),
    test_rules_ko=(
        "컴포넌트 테스트는 사용자 상호작용과 표시 결과를 검증한다.",
        "hook 테스트는 상태 전이와 비동기 흐름을 검증한다.",
        "service 테스트는 API client 경계와 오류 변환을 검증한다.",
    ),
    test_rules_en=(
        "Component tests verify user interactions and rendered results.",
        "Hook tests verify state transitions and async flow.",
        "Service tests verify API client boundaries and error mapping.",
    ),
    directories=("src/pages", "src/components", "src/hooks", "src/services", "src/stores", "src/types"),
)

NEXTJS_PROFILE = FrameworkProfile(
    key="nextjs",
    display_name="Next.js",
    philosophy_ko="Next.js는 App Router를 기본으로 하며 Server Component와 Client Component의 책임을 명확히 구분한다.",
    philosophy_en="Next.js should use the App Router by default and clearly separate Server Component and Client Component responsibilities.",
    architecture_ko=(
        "app 디렉토리는 라우트, 레이아웃, 서버 데이터 로딩의 기준 위치로 사용한다.",
        "Server Component는 데이터 조회와 정적/서버 렌더링 책임을 담당한다.",
        "Client Component는 브라우저 상태, 이벤트, 인터랙션이 필요한 경우에만 사용한다.",
        "route handler는 API boundary이며 복잡한 비즈니스 로직은 service 계층으로 분리한다.",
        "권장 흐름: Route/Page -> Server Action or Service -> Repository/External API.",
    ),
    architecture_en=(
        "Use the app directory as the place for routes, layouts, and server data loading.",
        "Server Components own data reads and static/server rendering.",
        "Client Components are only for browser state, events, and interactions.",
        "Route handlers are API boundaries; move complex business logic into services.",
        "Recommended flow: Route/Page -> Server Action or Service -> Repository/External API.",
    ),
    framework_rules_ko=(
        "'use client'는 필요한 파일에만 선언한다.",
        "서버 전용 비밀값과 브라우저 공개 환경 변수를 구분한다.",
        "데이터 변경은 server action 또는 route handler로 경계를 명확히 한다.",
        "캐시, revalidate, dynamic 설정은 데이터 신선도 요구사항과 함께 문서화한다.",
    ),
    framework_rules_en=(
        "Declare 'use client' only in files that need it.",
        "Separate server-only secrets from browser-exposed environment variables.",
        "Keep data mutations behind server actions or route handlers.",
        "Document cache, revalidate, and dynamic settings with freshness requirements.",
    ),
    api_rules_ko=(
        "route handler 응답은 명시적 JSON 계약을 유지한다.",
        "server action의 입력 검증과 권한 검사를 생략하지 않는다.",
        "프론트엔드 내부 호출과 외부 공개 API를 구분한다.",
    ),
    api_rules_en=(
        "Route handler responses should keep explicit JSON contracts.",
        "Do not skip input validation or authorization checks in server actions.",
        "Separate internal frontend calls from externally exposed APIs.",
    ),
    test_rules_ko=(
        "서버 로직은 service 단위 테스트로 우선 검증한다.",
        "클라이언트 컴포넌트는 사용자 상호작용 중심으로 검증한다.",
        "라우팅과 인증 흐름은 통합 테스트 또는 E2E 테스트로 검증한다.",
    ),
    test_rules_en=(
        "Verify server logic first with service unit tests.",
        "Verify Client Components around user interactions.",
        "Verify routing and auth flow with integration or E2E tests.",
    ),
    directories=("app", "components", "features", "services", "lib", "types"),
)

NODE_EXPRESS_PROFILE = FrameworkProfile(
    key="node-express",
    display_name="Node Express",
    philosophy_ko="Express는 얇은 HTTP 계층으로 유지하고 route, controller, service, repository를 분리한다.",
    philosophy_en="Keep Express as a thin HTTP layer and separate routes, controllers, services, and repositories.",
    architecture_ko=(
        "route는 URL과 middleware 연결만 담당한다.",
        "controller는 요청 파싱, 응답 변환, service 호출만 담당한다.",
        "service는 비즈니스 유스케이스와 트랜잭션 흐름을 담당한다.",
        "repository는 DB 접근을 담당하고 Express 객체를 알지 못해야 한다.",
        "권장 흐름: Route -> Controller -> Service -> Repository -> DB.",
    ),
    architecture_en=(
        "Routes only connect URLs and middleware.",
        "Controllers parse requests, map responses, and call services only.",
        "Services own business use cases and transaction flow.",
        "Repositories own database access and must not know Express objects.",
        "Recommended flow: Route -> Controller -> Service -> Repository -> DB.",
    ),
    framework_rules_ko=(
        "비동기 오류 처리는 공통 error middleware로 모은다.",
        "req/res 객체를 service 또는 repository로 넘기지 않는다.",
        "validation middleware와 service 검증의 책임을 구분한다.",
        "외부 API 호출은 client/adapter 계층으로 분리한다.",
    ),
    framework_rules_en=(
        "Centralize async error handling in shared error middleware.",
        "Do not pass req/res objects into services or repositories.",
        "Separate validation middleware responsibilities from service validation.",
        "Move external API calls into client/adapter layers.",
    ),
    api_rules_ko=(
        "JSON 응답 형식과 오류 응답 형식을 공통으로 유지한다.",
        "라우트 경로는 리소스 명사 중심으로 작성한다.",
        "입력 검증 실패, 인증 실패, 권한 실패를 구분한다.",
    ),
    api_rules_en=(
        "Keep JSON response and error response formats consistent.",
        "Use resource nouns for route paths.",
        "Distinguish validation, authentication, and authorization failures.",
    ),
    test_rules_ko=(
        "Service 테스트는 DB와 HTTP를 격리한다.",
        "Controller/route 테스트는 supertest 등으로 HTTP 계약을 검증한다.",
        "Repository 테스트는 실제 쿼리와 transaction 동작을 검증한다.",
    ),
    test_rules_en=(
        "Service tests isolate database and HTTP dependencies.",
        "Controller/route tests verify HTTP contracts with tools such as supertest.",
        "Repository tests verify real query and transaction behavior.",
    ),
    directories=("src/routes", "src/controllers", "src/services", "src/repositories", "src/middlewares", "src/types"),
)

FULLSTACK_FASTAPI_REACT_PROFILE = FrameworkProfile(
    key="fullstack-fastapi-react",
    display_name="Fullstack FastAPI + React",
    philosophy_ko="FastAPI 백엔드와 React 프론트엔드는 API 계약을 중심으로 분리하고, 각 영역의 계층 규칙을 동시에 지킨다.",
    philosophy_en="Separate the FastAPI backend and React frontend around the API contract while keeping both layer rules.",
    architecture_ko=(
        "backend는 Controller -> Service -> Repository -> DB 흐름을 따른다.",
        "frontend는 Page -> Hook/Store -> Service -> API 흐름을 따른다.",
        "docs/api/specification.md는 백엔드 response schema와 프론트엔드 service 타입의 공통 계약이다.",
        "백엔드 Entity를 프론트엔드 타입으로 직접 취급하지 않는다.",
        "인증, 오류, pagination, enum 값은 양쪽 구현과 문서를 함께 갱신한다.",
    ),
    architecture_en=(
        "Backend follows Controller -> Service -> Repository -> DB.",
        "Frontend follows Page -> Hook/Store -> Service -> API.",
        "docs/api/specification.md is the shared contract between backend response schemas and frontend service types.",
        "Do not treat backend entities as frontend types directly.",
        "Update auth, errors, pagination, and enum values in both implementations and docs.",
    ),
    framework_rules_ko=(
        "backend와 frontend 디렉토리 경계를 분명히 유지한다.",
        "API 변경은 backend schema, frontend service/type, docs/api/specification.md를 함께 수정한다.",
        "React 컴포넌트는 백엔드 엔드포인트를 직접 호출하지 않고 service 계층을 통한다.",
        "FastAPI service는 프론트엔드 화면 구조를 알지 못해야 한다.",
        "CORS, 인증 토큰, 오류 응답 형식은 공통 정책으로 문서화한다.",
    ),
    framework_rules_en=(
        "Keep backend and frontend directory boundaries clear.",
        "API changes must update backend schemas, frontend services/types, and docs/api/specification.md together.",
        "React components call backend endpoints through the service layer, not directly.",
        "FastAPI services must not know frontend screen structure.",
        "Document CORS, auth tokens, and error response format as shared policies.",
    ),
    api_rules_ko=(
        "OpenAPI 또는 명시적 docs/api/specification.md를 기준 계약으로 유지한다.",
        "Request/Response 필드명은 백엔드와 프론트엔드에서 동일하게 관리한다.",
        "인증이 필요한 API는 권한 요구사항과 실패 응답을 반드시 문서화한다.",
    ),
    api_rules_en=(
        "Keep OpenAPI or explicit docs/api/specification.md as the source contract.",
        "Maintain identical request/response field names across backend and frontend.",
        "Document authorization requirements and failure responses for protected APIs.",
    ),
    test_rules_ko=(
        "백엔드 API 테스트와 프론트엔드 service 테스트가 같은 계약을 검증하게 한다.",
        "주요 사용자 흐름은 E2E 또는 통합 테스트 대상으로 둔다.",
        "API mock은 실제 docs/api/specification.md와 불일치하지 않게 관리한다.",
    ),
    test_rules_en=(
        "Backend API tests and frontend service tests should verify the same contract.",
        "Cover major user flows with E2E or integration tests.",
        "Keep API mocks aligned with docs/api/specification.md.",
    ),
    directories=("backend/app/controllers", "backend/app/services", "backend/app/repositories", "frontend/src/pages", "frontend/src/components", "frontend/src/services", "frontend/src/stores"),
)

PROFILES: dict[str, FrameworkProfile] = {
    profile.key: profile
    for profile in (
        FASTAPI_PROFILE,
        PYTHON_PROFILE,
        SPRINGBOOT_PROFILE,
        REACT_PROFILE,
        NEXTJS_PROFILE,
        NODE_EXPRESS_PROFILE,
        FULLSTACK_FASTAPI_REACT_PROFILE,
    )
}

PROFILE_ALIASES: dict[str, str] = {
    "py": "python",
    "python3": "python",
    "plain-python": "python",
    "vanilla-python": "python",
    "general-python": "python",
    "fast-api": "fastapi",
    "spring": "springboot",
    "spring-boot": "springboot",
    "next": "nextjs",
    "next.js": "nextjs",
    "node": "node-express",
    "express": "node-express",
    "nodeexpress": "node-express",
    "fullstack": "fullstack-fastapi-react",
    "fastapi-react": "fullstack-fastapi-react",
}


def supported_profile_names() -> tuple[str, ...]:
    """Return supported canonical profile names."""

    return tuple(PROFILES)


def canonical_profile_name(name: str) -> str:
    """Normalize a user-provided stack name to a supported profile key."""

    normalized = name.strip().lower()
    return PROFILE_ALIASES.get(normalized, normalized)


def resolve_profiles(stack: tuple[str, ...]) -> tuple[FrameworkProfile, ...]:
    """Resolve stack names to framework profiles, preserving user order."""

    profiles: list[FrameworkProfile] = []
    unknown: list[str] = []
    seen: set[str] = set()

    for raw_name in stack:
        key = canonical_profile_name(raw_name)
        profile = PROFILES.get(key)
        if profile is None:
            unknown.append(raw_name)
            continue
        if key not in seen:
            profiles.append(profile)
            seen.add(key)

    if unknown:
        supported = ", ".join(supported_profile_names())
        invalid = ", ".join(unknown)
        raise UnknownProfileError(f"unsupported stack profile(s): {invalid}. Supported: {supported}")

    return tuple(profiles)
