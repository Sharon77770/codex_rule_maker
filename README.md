# codex-rule-maker

`codex-rule-maker`는 프로젝트 루트에 `.codex` 규칙 폴더와 `docs/` 프로젝트 문서 템플릿을 자동 구성하는 Python CLI 도구입니다. 사용자가 프로젝트 이름, 설명, 스택, DB, 인증 여부, 외부 API 여부, 문서화 수준, 문서 언어를 입력하면 Codex가 작업 전에 읽을 개발 규칙과 프로젝트 문서 구조를 생성합니다.

## 설치

요구 Python 버전은 3.9 이상입니다.

개발 환경에서 바로 실행:

```bash
python -m codex_builder.cli --help
```

패키지 명령으로 설치:

```bash
pip install -e .
codex-init --help
```

PyPI 설치:

```bash
pip install codex-rule-maker
codex-init --help
```

## 기본 대화형 실행

옵션 없이 실행하면 필요한 값을 순서대로 질문합니다.

```bash
codex-init
```

입력받는 항목:

- 프로젝트 이름
- 프로젝트 설명
- 사용 스택
- DB 사용 여부 및 DB 종류
- 인증 사용 여부
- 외부 API 연동 여부
- 문서화 수준
- 문서 언어
- 대상 디렉토리
- 기존 `.codex`가 있을 때 처리 방식
- 생성 전 최종 확인

`--interactive`도 같은 대화형 흐름을 사용합니다. 옵션 값을 일부 같이 넘기면 해당 값은 다시 묻지 않고, 누락된 값만 질문합니다. `--interactive`에서는 최종 확인 화면을 반드시 보여줍니다.

```bash
codex-init --interactive
codex-init --interactive --name pfm-lab --stack fastapi,react
```

## 옵션 기반 실행

필수 옵션을 모두 주면 누락 값 질문 없이 기본값을 사용합니다. 일반 터미널에서는 생성 전 최종 확인만 거치며, 파이프/테스트 같은 비대화형 실행에서는 자동화가 멈추지 않도록 바로 생성합니다.

```bash
codex-init --name pfm-lab --stack fastapi --db mysql --auth yes --external-api yes --docs strict
```

모듈 실행 방식도 동일하게 동작합니다.

```bash
python -m codex_builder.cli --name sample-api --stack fastapi --db mysql --auth yes --external-api yes --docs strict
```

부분 옵션만 주면 누락된 값은 prompt로 보완합니다.

```bash
codex-init --name sample-api
```

입력 우선순위는 `CLI 옵션 입력값 > prompt 입력값 > 기본값`입니다.

## 기존 .codex 충돌 처리

기존 `.codex`가 있고 `--force`가 없으면 다음 선택지를 보여줍니다.

```text
기존 .codex 폴더가 존재합니다.
1. 중단
2. 백업 후 재생성
3. 삭제 후 재생성
```

- `중단`: 아무것도 변경하지 않고 종료
- `백업 후 재생성`: 기존 `.codex`를 `.codex_backup_YYYYMMDD_HHMMSS`로 이동 후 새로 생성
- `삭제 후 재생성`: 기존 `.codex`를 삭제 후 새로 생성

옵션으로 동작을 고정할 수도 있습니다.

```bash
codex-init --force
```

`--force`만 사용하면 기존 `.codex`를 백업 후 재생성합니다.

```bash
codex-init --force --overwrite
```

`--force --overwrite`를 함께 사용하면 기존 `.codex`를 삭제 후 재생성합니다.

## 예시 실행 흐름

```text
프로젝트 이름 [sample]: 마리오
프로젝트 설명: 2D 플렛포머 게임
지원 프로필:
- fastapi
- python
- springboot
- react
- nextjs
- node-express
- fullstack-fastapi-react
사용 스택 [fastapi]: fastapi,react
DB를 사용하나요? [y/N]: y
DB 종류 [mysql]: mysql
인증 기능을 사용하나요? [y/N]: y
외부 API 연동이 있나요? [y/N]: y
문서화 수준 (light/standard/strict) [standard]: strict
문서 언어 (ko/en) [ko]: ko
대상 디렉토리 [C:\Users\User\Documents\GitHub\sample]:

생성 설정 확인

프로젝트 이름: 마리오
설명: 2D 플랫포머 게임
스택: fastapi,react
DB: mysql
인증: yes
외부 API: yes
문서화 수준: strict
언어: ko
대상 디렉토리: C:\Users\User\Documents\GitHub\sample

이 설정으로 .codex를 생성할까요? [Y/n]: y
```

## CLI 옵션

| 옵션 | 설명 | 기본값 |
| --- | --- | --- |
| `--name` | 프로젝트 이름 | 현재 디렉토리 이름 |
| `--description` | 프로젝트 설명 | 빈 값 |
| `--stack` | comma-separated framework profile | `fastapi` |
| `--db`, `--database` | DB 종류 | 미지정 |
| `--auth` | 인증 사용 여부: `yes` 또는 `no` | `no` |
| `--external-api` | 외부 API 사용 여부: `yes` 또는 `no` | `no` |
| `--docs` | 문서화 수준: `light`, `standard`, `strict` | `standard` |
| `--language` | 문서 언어: `ko`, `en` | `ko` |
| `--interactive` | 대화형 입력 사용 및 최종 확인 표시 | 비활성 |
| `--force` | 기존 `.codex`가 있으면 백업 후 재생성 | 비활성 |
| `--overwrite` | `--force`와 함께 기존 `.codex` 삭제 후 재생성 | 비활성 |
| `--target-dir` | `.codex`와 `docs/`를 생성할 대상 디렉토리 | 현재 디렉토리 |

## 생성 구조

```text
.codex/
├── ai_rule_developer/
│   ├── GLOBAL_RULES.md
│   ├── ARCHITECTURE_RULES.md
│   ├── CODE_STYLE_RULES.md
│   ├── API_DESIGN_RULES.md
│   ├── DOCUMENT_RULE.md
│   ├── DOMAIN_MODEL_RULES.md
│   ├── EXTERNAL_INTEGRATION_RULES.md
│   └── SERVICE_LAYER_RULES.md
├── ref_docs/
└── codex_start_prompt.txt

docs/
├── architecture/
│   ├── directory.md
│   ├── architecture.md
│   ├── component.md
│   ├── state.md
│   └── flow.md
├── api/
│   ├── endpoints.md
│   └── specification.md
└── database/
    └── schema.md
```

`ai_rule_developer`는 코딩할 때 지켜야 하는 규칙입니다. `ref_docs`는 외부 아키텍처 문서, PRD, 리서치, 벤더 문서처럼 사용자가 임의로 추가하는 참고자료 공간이므로 디렉토리만 생성합니다. 프로젝트 자체 명세는 루트 `docs/` 아래에 생성되며, 기존 `docs/` 파일이 있으면 덮어쓰지 않습니다. `codex_start_prompt.txt`는 Codex가 작업 시작 전에 `.codex` 문서를 먼저 읽고 규칙 우선순위를 적용하도록 지시합니다.

## 지원 프레임워크 프로필

- `fastapi`: controller/service/repository/schema/entity 계층 분리
- `python`: 일반 Python package/module/service/adapter/CLI 경계 분리
- `springboot`: controller/service/repository/entity/dto 계층 분리
- `react`: component/page/hook/service/store 분리
- `nextjs`: App Router, Server Component와 Client Component 구분
- `node-express`: route/controller/service/repository 분리
- `fullstack-fastapi-react`: FastAPI 백엔드와 React 프론트엔드 규칙 동시 적용

여러 프로필은 comma로 조합할 수 있습니다.

```bash
codex-init --stack fastapi,react
codex-init --stack python
codex-init --stack fullstack-fastapi-react
codex-init --stack nextjs
```

## 문서 생성 규칙

- 기본 문서 언어는 한국어입니다.
- `--language en`을 사용하면 영어 문서를 생성합니다.
- `--docs strict`는 코드 변경 후 문서 업데이트 필수 규칙을 포함합니다.
- `--auth yes`는 인증/권한 규칙을 포함합니다.
- `--external-api yes`는 외부 연동 계층 분리 규칙을 포함합니다.
- `--db mysql`처럼 DB를 지정하면 DB, Repository, Schema 관련 규칙을 포함합니다.
- 프로젝트 명세 템플릿은 `.codex/ref_docs`가 아니라 `docs/architecture`, `docs/api`, `docs/database`에 생성됩니다.

## 테스트

```bash
pip install -e ".[dev]"
pytest
```
