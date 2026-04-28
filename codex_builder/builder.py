"""Filesystem builder for generated .codex folders."""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

from codex_builder.constants import CODEX_DIR_NAME
from codex_builder.models import BuildResult, ProjectConfig
from codex_builder.template_renderer import TemplateRenderer


class ExistingCodexError(FileExistsError):
    """Raised when .codex already exists and force is not enabled."""


class CodexBuildError(RuntimeError):
    """Raised when the builder cannot write the generated files."""


class CodexBuilder:
    """Create a .codex directory from a ProjectConfig."""

    def __init__(self, renderer: Optional[TemplateRenderer] = None) -> None:
        self._renderer = renderer or TemplateRenderer()

    def build(
        self,
        config: ProjectConfig,
        *,
        target_dir: Optional[Union[Path, str]] = None,
        force: bool = False,
        backup_existing: bool = True,
    ) -> BuildResult:
        root = Path(target_dir or Path.cwd()).resolve()
        codex_dir = root / CODEX_DIR_NAME

        if codex_dir.exists() and not force:
            raise ExistingCodexError(f"{codex_dir} already exists. Re-run with --force to replace it.")

        rendered_files = self._renderer.render(config)

        backup_dir: Optional[Path] = None
        if codex_dir.exists():
            backup_dir = self._replace_existing_codex(codex_dir, backup_existing=backup_existing)

        try:
            for relative_dir in self._renderer.render_directories(config):
                (root / relative_dir).mkdir(parents=True, exist_ok=True)

            written_files: list[Path] = []
            for relative_path, content in rendered_files.items():
                destination = root / relative_path
                destination.parent.mkdir(parents=True, exist_ok=True)
                if destination.exists() and relative_path.parts[0] != CODEX_DIR_NAME:
                    continue
                destination.write_text(content.rstrip() + "\n", encoding="utf-8")
                written_files.append(destination)
        except OSError as exc:
            raise CodexBuildError(f"failed to write .codex files: {exc}") from exc

        return BuildResult(
            codex_dir=codex_dir,
            written_files=tuple(written_files),
            backup_dir=backup_dir,
        )

    def _replace_existing_codex(self, codex_dir: Path, *, backup_existing: bool) -> Optional[Path]:
        if backup_existing:
            backup_dir = self._next_backup_path(codex_dir)
            try:
                codex_dir.rename(backup_dir)
            except OSError as exc:
                raise CodexBuildError(f"failed to backup existing .codex folder: {exc}") from exc
            return backup_dir

        try:
            if codex_dir.is_dir():
                shutil.rmtree(codex_dir)
            else:
                codex_dir.unlink()
        except OSError as exc:
            raise CodexBuildError(f"failed to remove existing .codex path: {exc}") from exc
        return None

    def _next_backup_path(self, codex_dir: Path) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_backup = codex_dir.with_name(f"{CODEX_DIR_NAME}_backup_{timestamp}")
        candidate = base_backup
        index = 1
        while candidate.exists():
            candidate = codex_dir.with_name(f"{base_backup.name}.{index}")
            index += 1
        return candidate
