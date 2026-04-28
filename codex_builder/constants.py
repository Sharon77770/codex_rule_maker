"""Shared constants for generated .codex structures."""

from __future__ import annotations

CODEX_DIR_NAME = ".codex"
AI_RULE_DIR_NAME = "AI_RULE_DEVELOPER"
REF_DOCS_DIR_NAME = "REF_DOCS"
START_PROMPT_FILE_NAME = "codex_start_prompt.txt"

RULE_FILE_NAMES = (
    "GLOBAL_RULES.md",
    "ARCHITECTURE_RULES.md",
    "CODE_STYLE_RULES.md",
    "API_DESIGN_RULES.md",
    "DOCUMENT_RULE.md",
    "TEST_RULES.md",
    "FRAMEWORK_RULES.md",
)

REF_DOC_FILE_NAMES = (
    "PROJECT_OVERVIEW.md",
    "FEATURE_SPEC.md",
    "API_SPEC.md",
    "DB_SPEC.md",
)

DEFAULT_LANGUAGE = "ko"
DEFAULT_DOCS_LEVEL = "standard"
DEFAULT_STACK = ("fastapi",)

SUPPORTED_LANGUAGES = ("ko", "en")
SUPPORTED_DOCS_LEVELS = ("light", "standard", "strict")
