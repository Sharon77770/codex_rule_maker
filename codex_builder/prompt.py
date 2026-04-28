"""Interactive prompt flow for codex-init."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional, TextIO

from codex_builder.constants import (
    CODEX_DIR_NAME,
    DEFAULT_DOCS_LEVEL,
    DEFAULT_LANGUAGE,
    DEFAULT_STACK,
)
from codex_builder.models import ConfigError, ProjectConfig, parse_yes_no
from codex_builder.profiles import supported_profile_names
from codex_builder.validator import (
    validate_docs_level,
    validate_existing_directory,
    validate_language,
    validate_stack,
)


InputFunc = Callable[[str], str]


class PromptAbort(Exception):
    """Raised when the user chooses not to generate .codex."""


@dataclass(frozen=True)
class PromptBuildRequest:
    """Resolved request data needed by the CLI entrypoint."""

    config: ProjectConfig
    target_dir: Path
    force: bool
    backup_existing: bool


class PromptSession:
    """Collect missing CLI values using plain input prompts."""

    def __init__(self, *, input_func: Optional[InputFunc] = None, output: Optional[TextIO] = None) -> None:
        self._input = input_func or input
        self._output = output

    def resolve_request(
        self,
        args: argparse.Namespace,
        *,
        prompt_for_missing: bool,
        confirm_before_build: bool,
    ) -> PromptBuildRequest:
        config = self._resolve_config(args, prompt_for_missing=prompt_for_missing)
        target_dir = self._resolve_target_dir(args.target_dir, prompt_for_missing=prompt_for_missing)
        force, backup_existing, conflict_prompted = self._resolve_existing_codex_policy(args, target_dir)

        if confirm_before_build or conflict_prompted:
            if not self.confirm_generation(config, target_dir):
                raise PromptAbort("cancelled by user")

        return PromptBuildRequest(
            config=config,
            target_dir=target_dir,
            force=force,
            backup_existing=backup_existing,
        )

    def _resolve_config(self, args: argparse.Namespace, *, prompt_for_missing: bool) -> ProjectConfig:
        cwd_name = Path.cwd().name

        if prompt_for_missing:
            project_name = args.name or self.prompt_text("프로젝트 이름", cwd_name)
            description = args.description if args.description is not None else self.prompt_text("프로젝트 설명", "")
            stack = validate_stack(args.stack) if args.stack else self.prompt_stack()
            database = args.database if args.database else self.prompt_database()
            auth_enabled = parse_yes_no(args.auth) if args.auth is not None else self.prompt_confirm("인증 기능을 사용하나요?", default=False)
            external_api_enabled = (
                parse_yes_no(args.external_api)
                if args.external_api is not None
                else self.prompt_confirm("외부 API 연동이 있나요?", default=False)
            )
            docs_level = validate_docs_level(args.docs_level) if args.docs_level else self.prompt_docs_level()
            language = validate_language(args.language) if args.language else self.prompt_language()
        else:
            project_name = args.name or cwd_name
            description = args.description or ""
            stack = validate_stack(args.stack or DEFAULT_STACK)
            database = args.database or None
            auth_enabled = parse_yes_no(args.auth, default=False)
            external_api_enabled = parse_yes_no(args.external_api, default=False)
            docs_level = validate_docs_level(args.docs_level or DEFAULT_DOCS_LEVEL)
            language = validate_language(args.language or DEFAULT_LANGUAGE)

        return ProjectConfig(
            project_name=project_name,
            description=description,
            stack=stack,
            database=database or None,
            auth_enabled=auth_enabled,
            external_api_enabled=external_api_enabled,
            docs_level=docs_level,
            language=language,
        )

    def _resolve_target_dir(self, target_dir: Optional[Path], *, prompt_for_missing: bool) -> Path:
        if target_dir is not None:
            return validate_existing_directory(target_dir)

        if prompt_for_missing:
            raw_target = self.prompt_text("대상 디렉토리", str(Path.cwd()))
            return validate_existing_directory(Path(raw_target))

        return validate_existing_directory(Path.cwd())

    def _resolve_existing_codex_policy(self, args: argparse.Namespace, target_dir: Path) -> tuple[bool, bool, bool]:
        codex_dir = target_dir / CODEX_DIR_NAME
        if args.force:
            return True, not args.overwrite, False
        if not codex_dir.exists():
            return False, True, False

        action = self.prompt_existing_codex_action()
        if action == "abort":
            raise PromptAbort("existing .codex kept unchanged")
        if action == "backup":
            return True, True, True
        return True, False, True

    def prompt_text(self, label: str, default: str) -> str:
        suffix = f" [{default}]" if default else ""
        value = self._input(f"{label}{suffix}: ").strip()
        return value or default

    def prompt_confirm(self, label: str, *, default: bool) -> bool:
        suffix = "[Y/n]" if default else "[y/N]"
        while True:
            value = self._input(f"{label} {suffix}: ").strip().lower()
            if not value:
                return default
            if value in {"y", "yes"}:
                return True
            if value in {"n", "no"}:
                return False
            self._write("y 또는 n으로 입력해 주세요.")

    def prompt_stack(self) -> tuple[str, ...]:
        self._write("지원 프로필:")
        for profile_name in supported_profile_names():
            self._write(f"- {profile_name}")

        while True:
            raw_stack = self.prompt_text("사용 스택", ",".join(DEFAULT_STACK))
            try:
                return validate_stack(raw_stack)
            except ConfigError as exc:
                self._write(f"잘못된 stack 값입니다. {exc}")

    def prompt_database(self) -> Optional[str]:
        if not self.prompt_confirm("DB를 사용하나요?", default=False):
            return None

        while True:
            database = self.prompt_text("DB 종류", "mysql").strip().lower()
            if database:
                return database
            self._write("DB 종류를 입력해 주세요.")

    def prompt_docs_level(self) -> str:
        return self._prompt_choice("문서화 수준", ("light", "standard", "strict"), DEFAULT_DOCS_LEVEL, validate_docs_level)

    def prompt_language(self) -> str:
        return self._prompt_choice("문서 언어", ("ko", "en"), DEFAULT_LANGUAGE, validate_language)

    def prompt_existing_codex_action(self) -> str:
        self._write("")
        self._write("기존 .codex 폴더가 존재합니다.")
        self._write("1. 중단")
        self._write("2. 백업 후 재생성")
        self._write("3. 삭제 후 재생성")

        while True:
            value = self.prompt_text("처리 방식 선택", "1").strip().lower()
            if value in {"1", "abort", "stop", "중단"}:
                return "abort"
            if value in {"2", "backup", "백업"}:
                return "backup"
            if value in {"3", "overwrite", "delete", "삭제"}:
                return "overwrite"
            self._write("1, 2, 3 중 하나를 입력해 주세요.")

    def confirm_generation(self, config: ProjectConfig, target_dir: Path) -> bool:
        self._write("")
        self._write("생성 설정 확인")
        self._write("")
        self._write(f"프로젝트 이름: {config.project_name}")
        self._write(f"설명: {config.description or '-'}")
        self._write(f"스택: {','.join(config.stack)}")
        self._write(f"DB: {config.database or 'no'}")
        self._write(f"인증: {self._yes_no(config.auth_enabled)}")
        self._write(f"외부 API: {self._yes_no(config.external_api_enabled)}")
        self._write(f"문서화 수준: {config.docs_level}")
        self._write(f"언어: {config.language}")
        self._write(f"대상 디렉토리: {target_dir}")
        self._write("")
        return self.prompt_confirm("이 설정으로 .codex를 생성할까요?", default=True)

    def _prompt_choice(
        self,
        label: str,
        choices: tuple[str, ...],
        default: str,
        validator: Callable[[str], str],
    ) -> str:
        choices_text = "/".join(choices)
        while True:
            value = self.prompt_text(f"{label} ({choices_text})", default)
            try:
                return validator(value)
            except ConfigError as exc:
                self._write(f"잘못된 입력입니다. {exc}")

    def _write(self, message: str) -> None:
        print(message, file=self._output)

    def _yes_no(self, value: bool) -> str:
        return "yes" if value else "no"
