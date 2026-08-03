# Changelog

이 파일은 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/) 형식을 따르며,
버전 표기는 [Semantic Versioning](https://semver.org/lang/ko/)을 따릅니다.

## [Unreleased]

### Added

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
