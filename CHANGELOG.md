# Changelog

이 파일은 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/) 형식을 따르며,
버전 표기는 [Semantic Versioning](https://semver.org/lang/ko/)을 따릅니다.

## [Unreleased]

### Added

- 루트 `AGENTS.md` 진입점 생성. 코딩 에이전트가 자동으로 읽는 상위 지시문 경로를 확보하기 위한
  변경입니다. `.codex/` 아래 문서는 자동 로드 대상이 아니므로 기존에는 `codex_start_prompt.txt`를
  사용자가 직접 붙여넣지 않으면 생성된 규칙이 적용되지 않았습니다. 상세 규칙을 복사하지 않고
  작업 유형별 라우팅 테이블, 타협 불가 경계, 완료 기준, 응답 형식만 담아 4 KiB 미만을 지킵니다.
- `--agents-md` / `--no-agents-md` 옵션. 기본은 생성이며 기존 `AGENTS.md`는 덮어쓰지 않습니다.
- 생성된 `AGENTS.md`에 `.codex/ref_docs`를 신뢰할 수 없는 참고 데이터로 취급하고 지시문을 덮어쓸
  수 없다는 prompt injection 방어 문구, secret 출력 금지 문구 포함.
- 대표 설정 5종에 대한 골든 스냅샷 테스트(`tests/test_snapshots.py`). 렌더러 리팩토링 시
  생성물이 바뀌지 않았음을 증명할 수 있습니다. 의도된 변경은
  `UPDATE_SNAPSHOTS=1 pytest tests/test_snapshots.py`로 갱신합니다.
- GitHub Actions CI(`.github/workflows/ci.yml`). Python 3.9~3.13에서 pytest와 CLI
  스모크 실행, 별도 job에서 `python -m build` 및 `twine check`를 수행합니다.
- 이 CHANGELOG.

### Removed

- 저장소에 커밋되어 있던 `release_0_3_0/` 빌드 산출물(`.whl`, `.tar.gz`). 배포 아티팩트는
  버전 관리 대상이 아니며 GitHub Releases 또는 PyPI에서 받을 수 있습니다.

## [0.4.0]

- `python`, `typescript-javascript` 프로필 추가.
- `docs/` 프로젝트 명세 템플릿 생성 및 기존 `docs/` 파일 미덮어쓰기 정책.
- `.codex/ref_docs`를 사용자 관리 참고자료 공간으로 분리.

## [0.3.0] 이전

이전 릴리스 내역은 [PyPI 릴리스 목록](https://pypi.org/project/codex-rule-maker/#history)을
참고하세요.
