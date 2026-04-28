# codex-folder-builder

`codex-folder-builder`는 프로젝트 루트에 `.codex` 폴더를 자동 구성하는 Python CLI 도구입니다. 사용자가 프로젝트 이름, 설명, 스택, DB, 인증 여부, 외부 API 여부, 문서화 수준, 문서 언어를 입력하면 Codex가 작업 전에 읽을 개발 규칙과 프로젝트 참고 문서 템플릿을 생성합니다.

이 도구는 `output_ex/.codex` 예시의 철학을 참고했습니다. 예시를 그대로 복사하지 않고, 규칙 문서와 참고 문서를 분리한 범용 템플릿으로 일반화했습니다.

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
프로젝트 이름 [sample]: pfm-lab
프로젝트 설명: 자연어 기반 PFM 시뮬레이션 플랫폼
지원 프로필:
- fastapi
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

프로젝트 이름: pfm-lab
설명: 자연어 기반 PFM 시뮬레이션 플랫폼
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
| `--target-dir` | `.codex`를 생성할 대상 디렉토리 | 현재 디렉토리 |

## 생성 구조

```text
.codex/
├── AI_RULE_DEVELOPER/
│   ├── GLOBAL_RULES.md
│   ├── ARCHITECTURE_RULES.md
│   ├── CODE_STYLE_RULES.md
│   ├── API_DESIGN_RULES.md
│   ├── DOCUMENT_RULE.md
│   ├── TEST_RULES.md
│   └── FRAMEWORK_RULES.md
├── REF_DOCS/
│   ├── PROJECT_OVERVIEW.md
│   ├── FEATURE_SPEC.md
│   ├── API_SPEC.md
│   └── DB_SPEC.md
└── codex_start_prompt.txt
```

`AI_RULE_DEVELOPER`는 코딩할 때 지켜야 하는 규칙입니다. `REF_DOCS`는 개발 시 참고할 프로젝트 명세입니다. `codex_start_prompt.txt`는 Codex가 작업 시작 전에 `.codex` 문서를 먼저 읽고 규칙 우선순위를 적용하도록 지시합니다.

## 지원 프레임워크 프로필

- `fastapi`: controller/service/repository/schema/entity 계층 분리
- `springboot`: controller/service/repository/entity/dto 계층 분리
- `react`: component/page/hook/service/store 분리
- `nextjs`: App Router, Server Component와 Client Component 구분
- `node-express`: route/controller/service/repository 분리
- `fullstack-fastapi-react`: FastAPI 백엔드와 React 프론트엔드 규칙 동시 적용

여러 프로필은 comma로 조합할 수 있습니다.

```bash
codex-init --stack fastapi,react
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

## 테스트

```bash
pip install -e ".[dev]"
pytest
```

검증 범위:

- 기본 생성 성공
- 옵션만으로 생성 가능
- 누락 값 prompt 보완
- 잘못된 stack/docs/language 검증
- FastAPI 프로필 생성
- React 프로필 생성
- Fullstack FastAPI React 프로필 생성
- 기존 `.codex`가 있을 때 prompt 중단
- `--force`가 있으면 기존 `.codex` 백업 후 재생성
- `--force --overwrite`가 있으면 기존 `.codex` 삭제 후 재생성
