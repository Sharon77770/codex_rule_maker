"""Shared constants for generated .codex structures."""

from __future__ import annotations

CODEX_DIR_NAME = ".codex"
AI_RULE_DIR_NAME = "ai_rule_developer"
REF_DOCS_DIR_NAME = "ref_docs"
DOCS_DIR_NAME = "docs"
START_PROMPT_FILE_NAME = "codex_start_prompt.txt"

RULE_FILE_NAMES = (
    "GLOBAL_RULES.md",
    "ARCHITECTURE_RULES.md",
    "CODE_STYLE_RULES.md",
    "API_DESIGN_RULES.md",
    "DOCUMENT_RULE.md",
    "DOMAIN_MODEL_RULES.md",
    "EXTERNAL_INTEGRATION_RULES.md",
    "SERVICE_LAYER_RULES.md",
)

DOC_FILE_NAMES = (
    "architecture/directory.md",
    "architecture/architecture.md",
    "architecture/component.md",
    "architecture/state.md",
    "architecture/flow.md",
    "api/endpoints.md",
    "api/specification.md",
    "database/schema.md",
)

DEFAULT_LANGUAGE = "ko"
DEFAULT_DOCS_LEVEL = "standard"
DEFAULT_STACK = ("fastapi",)

SUPPORTED_LANGUAGES = ("ko", "en")
SUPPORTED_DOCS_LEVELS = ("light", "standard", "strict")
