#!/usr/bin/env python3
"""Manage local account files for the skill."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime_support import (
    account_path,
    append_bullet_to_section,
    default_runtime_root,
    ensure_runtime_layout,
    read_markdown_with_frontmatter,
    set_default_account,
    slugify,
    today_iso_date,
    write_markdown_with_frontmatter,
)


SECTION_NAMES = {
    "confirmed": "Confirmed Preferences",
    "constraints": "Hard Constraints",
    "pending": "Pending Preference Updates",
    "feedback": "Feedback Summary",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create and inspect local accounts for resume-job-fit-screening."
    )
    parser.add_argument(
        "--runtime-root",
        default=None,
        help="Override runtime root. Defaults to ~/.codex/data/resume-job-fit-screening",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List accounts")
    list_parser.add_argument("--format", choices=("json", "text"), default="text")

    show_parser = subparsers.add_parser("show", help="Show one account")
    show_parser.add_argument("account_id")

    create_parser = subparsers.add_parser("create", help="Create or replace an account")
    create_parser.add_argument("account_id")
    create_parser.add_argument("--display-name", default="")
    create_parser.add_argument("--resume-file", default=None)
    create_parser.add_argument("--resume-text", default=None)
    create_parser.add_argument(
        "--confirmed-preference", action="append", default=[]
    )
    create_parser.add_argument("--hard-constraint", action="append", default=[])
    create_parser.add_argument("--pending-update", action="append", default=[])
    create_parser.add_argument("--feedback-summary", action="append", default=[])
    create_parser.add_argument("--default", action="store_true")
    create_parser.add_argument("--force", action="store_true")

    default_parser = subparsers.add_parser("set-default", help="Set the default account")
    default_parser.add_argument("account_id")

    append_parser = subparsers.add_parser(
        "append-entry", help="Append one bullet to a section"
    )
    append_parser.add_argument("account_id")
    append_parser.add_argument(
        "--section", choices=tuple(SECTION_NAMES.keys()), required=True
    )
    append_parser.add_argument("--line", required=True)

    return parser.parse_args()


def render_section(title: str, lines: list[str]) -> str:
    if not lines:
        return f"## {title}\n"
    bullets = "\n".join(f"- {line}" for line in lines)
    return f"## {title}\n\n{bullets}\n"


def render_account_body(
    resume_text: str,
    confirmed: list[str],
    constraints: list[str],
    pending: list[str],
    feedback: list[str],
) -> str:
    sections = [
        "# Resume",
        "",
        resume_text.strip() or "<纯文本简历>",
        "",
        render_section("Confirmed Preferences", confirmed).rstrip(),
        "",
        render_section("Hard Constraints", constraints).rstrip(),
        "",
        render_section("Pending Preference Updates", pending).rstrip(),
        "",
        render_section("Feedback Summary", feedback).rstrip(),
        "",
    ]
    return "\n".join(sections).rstrip() + "\n"


def runtime_root_from_args(value: str | None) -> Path:
    return Path(value).expanduser().resolve() if value else default_runtime_root()


def command_list(runtime_root: Path, output_format: str) -> int:
    paths = ensure_runtime_layout(runtime_root)
    records = []
    for path in sorted(paths["account_root"].glob("*.md")):
        metadata, _ = read_markdown_with_frontmatter(path)
        records.append(
            {
                "account_id": metadata.get("account_id", path.stem),
                "display_name": metadata.get("display_name", ""),
                "default_account": bool(metadata.get("default_account", False)),
                "path": str(path),
            }
        )
    if output_format == "json":
        print(json.dumps(records, ensure_ascii=False, indent=2))
        return 0
    for record in records:
        marker = "*" if record["default_account"] else "-"
        print(
            f"{marker} {record['account_id']} | {record['display_name']} | {record['path']}"
        )
    return 0


def command_show(runtime_root: Path, account_id: str) -> int:
    paths = ensure_runtime_layout(runtime_root)
    path = account_path(paths["account_root"], account_id)
    if not path.exists():
        raise SystemExit(f"account not found: {path}")
    print(path.read_text(encoding="utf-8"))
    return 0


def load_resume_text(args: argparse.Namespace) -> str:
    if args.resume_text is not None:
        return args.resume_text
    if args.resume_file:
        return Path(args.resume_file).expanduser().read_text(encoding="utf-8")
    raise SystemExit("resume text is required via --resume-text or --resume-file")


def command_create(runtime_root: Path, args: argparse.Namespace) -> int:
    paths = ensure_runtime_layout(runtime_root)
    normalized_id = slugify(args.account_id)
    path = account_path(paths["account_root"], normalized_id)
    if path.exists() and not args.force:
        raise SystemExit(f"account already exists: {path}")

    metadata = {
        "account_id": normalized_id,
        "schema_version": 1,
        "display_name": args.display_name or normalized_id,
        "created_at": today_iso_date(),
        "updated_at": today_iso_date(),
        "default_topk": 5,
        "keyword_expansion": True,
        "default_account": False,
    }
    body = render_account_body(
        load_resume_text(args),
        args.confirmed_preference,
        args.hard_constraint,
        args.pending_update,
        args.feedback_summary,
    )
    write_markdown_with_frontmatter(path, metadata, body)

    if args.default:
        set_default_account(runtime_root, normalized_id)

    print(json.dumps({"account_path": str(path)}, ensure_ascii=False, indent=2))
    return 0


def command_set_default(runtime_root: Path, account_id: str) -> int:
    set_default_account(runtime_root, account_id)
    print(json.dumps({"default_account": slugify(account_id)}, ensure_ascii=False, indent=2))
    return 0


def command_append_entry(runtime_root: Path, args: argparse.Namespace) -> int:
    paths = ensure_runtime_layout(runtime_root)
    path = account_path(paths["account_root"], args.account_id)
    if not path.exists():
        raise SystemExit(f"account not found: {path}")

    metadata, body = read_markdown_with_frontmatter(path)
    metadata["updated_at"] = today_iso_date()
    updated_body = append_bullet_to_section(body, SECTION_NAMES[args.section], args.line)
    write_markdown_with_frontmatter(path, metadata, updated_body)
    print(json.dumps({"account_path": str(path)}, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    args = parse_args()
    runtime_root = runtime_root_from_args(args.runtime_root)

    if args.command == "list":
        return command_list(runtime_root, args.format)
    if args.command == "show":
        return command_show(runtime_root, args.account_id)
    if args.command == "create":
        return command_create(runtime_root, args)
    if args.command == "set-default":
        return command_set_default(runtime_root, args.account_id)
    if args.command == "append-entry":
        return command_append_entry(runtime_root, args)
    raise SystemExit(f"unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
