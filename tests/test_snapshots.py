"""Golden snapshot tests for generated document content.

These tests freeze the full rendered output for a small set of representative
configurations. They exist so that refactors of `TemplateRenderer` (for example
moving hardcoded strings into template files) can prove output equivalence
instead of relying on substring assertions.

To refresh snapshots after an intentional content change:

    UPDATE_SNAPSHOTS=1 pytest tests/test_snapshots.py

Review the resulting diff carefully before committing it.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from codex_builder.models import ProjectConfig
from codex_builder.template_renderer import TemplateRenderer


SNAPSHOT_DIR = Path(__file__).parent / "snapshots"

# Representative configurations. Kept deliberately small so snapshot diffs stay
# reviewable: one default case, one maximal Korean case, one English case, one
# frontend-only case and one framework-free Python case.
CASES: dict[str, ProjectConfig] = {
    "default_ko": ProjectConfig(project_name="snapshot-default"),
    "fastapi_react_full_ko": ProjectConfig(
        project_name="snapshot-full",
        description="스냅샷 검증용 프로젝트",
        stack=("fastapi", "react"),
        database="mysql",
        auth_enabled=True,
        external_api_enabled=True,
        docs_level="strict",
        language="ko",
    ),
    "fastapi_full_en": ProjectConfig(
        project_name="snapshot-full-en",
        description="Snapshot verification project",
        stack=("fastapi",),
        database="postgres",
        auth_enabled=True,
        external_api_enabled=True,
        docs_level="strict",
        language="en",
    ),
    "nextjs_light_ko": ProjectConfig(
        project_name="snapshot-next",
        stack=("nextjs",),
        docs_level="light",
        language="ko",
    ),
    "python_standard_en": ProjectConfig(
        project_name="snapshot-python",
        stack=("python",),
        docs_level="standard",
        language="en",
    ),
}

SEPARATOR = "=" * 72


def _serialize(config: ProjectConfig) -> str:
    """Render a config into one stable, diff-friendly text blob."""

    rendered = TemplateRenderer().render(config)
    directories = TemplateRenderer().render_directories(config)

    parts: list[str] = ["# directories"]
    parts.extend(sorted(directory.as_posix() for directory in directories))
    parts.append("")

    for relative_path in sorted(rendered, key=lambda path: path.as_posix()):
        parts.append(SEPARATOR)
        parts.append(f"# file: {relative_path.as_posix()}")
        parts.append(SEPARATOR)
        parts.append(rendered[relative_path].rstrip())
        parts.append("")

    return "\n".join(parts) + "\n"


@pytest.mark.parametrize("case_name", sorted(CASES))
def test_rendered_output_matches_snapshot(case_name: str) -> None:
    actual = _serialize(CASES[case_name])
    snapshot_path = SNAPSHOT_DIR / f"{case_name}.txt"

    if os.environ.get("UPDATE_SNAPSHOTS"):
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        snapshot_path.write_text(actual, encoding="utf-8")
        pytest.skip(f"snapshot updated: {snapshot_path.name}")

    assert snapshot_path.exists(), (
        f"missing snapshot {snapshot_path}. "
        "Run `UPDATE_SNAPSHOTS=1 pytest tests/test_snapshots.py` to create it."
    )

    expected = snapshot_path.read_text(encoding="utf-8")
    assert actual == expected, (
        f"rendered output for '{case_name}' changed. If the change is intentional, run "
        "`UPDATE_SNAPSHOTS=1 pytest tests/test_snapshots.py` and review the diff."
    )


def test_every_case_has_a_snapshot_file() -> None:
    """Guard against snapshot files being deleted or orphaned."""

    if os.environ.get("UPDATE_SNAPSHOTS"):
        pytest.skip("snapshot refresh run")

    expected_names = {f"{name}.txt" for name in CASES}
    actual_names = {path.name for path in SNAPSHOT_DIR.glob("*.txt")}
    assert actual_names == expected_names
