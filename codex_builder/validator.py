"""Validation helpers for CLI and prompt input."""

from __future__ import annotations

from pathlib import Path
from typing import Union

from codex_builder.constants import SUPPORTED_DOCS_LEVELS, SUPPORTED_LANGUAGES
from codex_builder.models import ConfigError, normalize_stack
from codex_builder.profiles import PROFILES, canonical_profile_name, supported_profile_names


def validate_stack(raw_stack: Union[str, tuple[str, ...]]) -> tuple[str, ...]:
    """Validate and canonicalize stack profile names."""

    normalized = normalize_stack(raw_stack)
    invalid: list[str] = []
    canonical: list[str] = []

    for value in normalized:
        profile_name = canonical_profile_name(value)
        if profile_name not in PROFILES:
            invalid.append(value)
            continue
        if profile_name not in canonical:
            canonical.append(profile_name)

    if invalid:
        invalid_text = ", ".join(invalid)
        supported_text = ", ".join(supported_profile_names())
        raise ConfigError(f"unsupported stack profile(s): {invalid_text}. Supported profiles: {supported_text}")

    if not canonical:
        raise ConfigError("at least one stack profile is required")

    return tuple(canonical)


def validate_docs_level(value: str) -> str:
    """Validate docs level input."""

    normalized = value.strip().lower()
    if normalized not in SUPPORTED_DOCS_LEVELS:
        allowed = ", ".join(SUPPORTED_DOCS_LEVELS)
        raise ConfigError(f"docs level must be one of: {allowed}")
    return normalized


def validate_language(value: str) -> str:
    """Validate document language input."""

    normalized = value.strip().lower()
    if normalized not in SUPPORTED_LANGUAGES:
        allowed = ", ".join(SUPPORTED_LANGUAGES)
        raise ConfigError(f"language must be one of: {allowed}")
    return normalized


def validate_existing_directory(value: Path) -> Path:
    """Resolve a target directory and ensure it exists."""

    target_dir = value.expanduser().resolve()
    if not target_dir.exists():
        raise ConfigError(f"target directory does not exist: {target_dir}")
    if not target_dir.is_dir():
        raise ConfigError(f"target path is not a directory: {target_dir}")
    return target_dir
