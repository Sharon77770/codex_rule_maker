"""Command line interface for codex-init."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

from codex_builder.builder import CodexBuilder, CodexBuildError, ExistingCodexError
from codex_builder.models import ConfigError
from codex_builder.prompt import PromptAbort, PromptSession
from codex_builder.profiles import UnknownProfileError, supported_profile_names


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codex-init",
        description="Generate a .codex folder with AI developer rules and project reference documents.",
    )
    parser.add_argument("--name", help="Project name. Defaults to the current directory name.")
    parser.add_argument("--description", help="Short project description.")
    parser.add_argument(
        "--stack",
        help=f"Comma-separated stack profiles. Supported: {', '.join(supported_profile_names())}.",
    )
    parser.add_argument("--db", "--database", dest="database", help="Database name, for example mysql or postgres.")
    parser.add_argument("--auth", help="Whether authentication is used: yes/no.")
    parser.add_argument("--external-api", dest="external_api", help="Whether external API integrations are used: yes/no.")
    parser.add_argument("--docs", dest="docs_level", help="Documentation strictness: light, standard, strict.")
    parser.add_argument("--language", help="Document language: ko or en.")
    parser.add_argument("--interactive", action="store_true", help="Prompt for missing values and always show final confirmation.")
    parser.add_argument("--force", action="store_true", help="Replace an existing .codex folder. Default force behavior creates a backup.")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="With --force, delete the existing .codex instead of backing it up.",
    )
    parser.add_argument(
        "--target-dir",
        type=Path,
        help="Directory where .codex will be created. Defaults to the current working directory.",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()
    args = parser.parse_args(raw_argv)

    try:
        prompt_for_missing = _should_prompt_for_missing(args, raw_argv)
        request = PromptSession().resolve_request(
            args,
            prompt_for_missing=prompt_for_missing,
            confirm_before_build=prompt_for_missing or (sys.stdin.isatty() and sys.stdout.isatty()),
        )
        result = CodexBuilder().build(
            request.config,
            target_dir=request.target_dir,
            force=request.force,
            backup_existing=request.backup_existing,
        )
    except PromptAbort as exc:
        print(f"codex-init: {exc}")
        return 0
    except (ConfigError, UnknownProfileError, ExistingCodexError, CodexBuildError) as exc:
        print(f"codex-init: error: {exc}", file=sys.stderr)
        return 1

    print(f"Generated: {result.codex_dir}")
    if result.backup_dir is not None:
        print(f"Backup: {result.backup_dir}")
    print(f"Files written: {len(result.written_files)}")
    return 0


def _should_prompt_for_missing(args: argparse.Namespace, raw_argv: list[str]) -> bool:
    if args.interactive:
        return True
    if not raw_argv:
        return True

    required_option_values = (
        args.name,
        args.stack,
        args.auth,
        args.external_api,
        args.docs_level,
    )
    return any(value is None for value in required_option_values)


if __name__ == "__main__":
    raise SystemExit(main())
