"""Data models and value parsing helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, Union

from codex_builder.constants import (
    DEFAULT_DOCS_LEVEL,
    DEFAULT_LANGUAGE,
    DEFAULT_STACK,
    SUPPORTED_DOCS_LEVELS,
    SUPPORTED_LANGUAGES,
)


class ConfigError(ValueError):
    """Raised when a CLI or builder configuration is invalid."""


@dataclass(frozen=True)
class ProjectConfig:
    """Normalized user inputs used to render the .codex document set."""

    project_name: str
    description: str = ""
    stack: tuple[str, ...] = DEFAULT_STACK
    database: Optional[str] = None
    auth_enabled: bool = False
    external_api_enabled: bool = False
    docs_level: str = DEFAULT_DOCS_LEVEL
    language: str = DEFAULT_LANGUAGE

    def __post_init__(self) -> None:
        project_name = self.project_name.strip()
        if not project_name:
            raise ConfigError("project name is required")

        normalized_stack = normalize_stack(self.stack)
        if not normalized_stack:
            normalized_stack = DEFAULT_STACK

        docs_level = self.docs_level.strip().lower()
        if docs_level not in SUPPORTED_DOCS_LEVELS:
            allowed = ", ".join(SUPPORTED_DOCS_LEVELS)
            raise ConfigError(f"docs level must be one of: {allowed}")

        language = self.language.strip().lower()
        if language not in SUPPORTED_LANGUAGES:
            allowed = ", ".join(SUPPORTED_LANGUAGES)
            raise ConfigError(f"language must be one of: {allowed}")

        database = self.database.strip().lower() if self.database else None

        object.__setattr__(self, "project_name", project_name)
        object.__setattr__(self, "description", self.description.strip())
        object.__setattr__(self, "stack", normalized_stack)
        object.__setattr__(self, "database", database)
        object.__setattr__(self, "docs_level", docs_level)
        object.__setattr__(self, "language", language)


@dataclass(frozen=True)
class BuildResult:
    """Result returned after generating a .codex folder."""

    codex_dir: Path
    written_files: tuple[Path, ...]
    backup_dir: Optional[Path] = None


def normalize_stack(raw_stack: Optional[Union[str, Iterable[str]]]) -> tuple[str, ...]:
    """Normalize comma-separated or iterable stack values."""

    if raw_stack is None:
        return DEFAULT_STACK

    if isinstance(raw_stack, str):
        items = raw_stack.split(",")
    else:
        items = []
        for value in raw_stack:
            items.extend(str(value).split(","))

    normalized: list[str] = []
    for item in items:
        value = item.strip().lower()
        if value and value not in normalized:
            normalized.append(value)

    return tuple(normalized)


def parse_yes_no(value: Optional[Union[str, bool]], *, default: bool = False) -> bool:
    """Parse common yes/no CLI values into a bool."""

    if value is None:
        return default

    if isinstance(value, bool):
        return value

    normalized = value.strip().lower()
    if normalized in {"y", "yes", "true", "1", "on"}:
        return True
    if normalized in {"n", "no", "false", "0", "off"}:
        return False

    raise ConfigError(f"expected yes/no value, got: {value}")
