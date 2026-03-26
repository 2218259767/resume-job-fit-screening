#!/usr/bin/env python3
"""Validate a v2 site note for public sharing."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from runtime_support import read_markdown_with_frontmatter


REQUIRED_METADATA_KEYS = (
    "site_slug",
    "schema_version",
    "content_version",
    "verified_at",
    "public_safe",
    "access_mode",
    "method_type",
    "maintainer",
    "example_search_url",
)

REQUIRED_SECTIONS = (
    "## 目标链接",
    "## 结论",
    "## 推荐做法",
    "## 成功请求样例",
    "## 已知问题",
    "## 更新规则",
)

SENSITIVE_PATTERNS = (
    re.compile(r"(?im)^authorization:\s*\S+"),
    re.compile(r"(?im)^cookie:\s*\S+"),
    re.compile(r"(?im)^set-cookie:\s*\S+"),
    re.compile(r"(?i)bearer\s+[a-z0-9._-]{8,}"),
    re.compile(r"sk-[a-z0-9]{10,}", re.IGNORECASE),
)


def validate_note(path: Path) -> dict[str, object]:
    metadata, body = read_markdown_with_frontmatter(path)
    errors: list[str] = []
    warnings: list[str] = []

    if not metadata:
        errors.append("missing YAML frontmatter")

    for key in REQUIRED_METADATA_KEYS:
        if key not in metadata:
            errors.append(f"missing metadata field: {key}")

    if metadata.get("site_slug") and metadata["site_slug"] != path.stem:
        errors.append("site_slug does not match filename stem")

    verified_at = str(metadata.get("verified_at", ""))
    if verified_at and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", verified_at):
        errors.append("verified_at must use YYYY-MM-DD")

    if metadata.get("public_safe") not in (True, False):
        errors.append("public_safe must be a boolean")

    for section in REQUIRED_SECTIONS:
        if section not in body:
            errors.append(f"missing section: {section}")

    if not body.lstrip().startswith("# "):
        errors.append("body must start with a level-1 title")

    for pattern in SENSITIVE_PATTERNS:
        if pattern.search(body):
            errors.append(f"sensitive content matched: {pattern.pattern}")

    if "```bash" not in body and "```http" not in body and "```json" not in body:
        warnings.append("note does not include an example code block")

    return {
        "path": str(path),
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "metadata": metadata,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a site note Markdown file.")
    parser.add_argument("note_path")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = validate_note(Path(args.note_path).expanduser().resolve())
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"path: {result['path']}")
        print(f"valid: {result['valid']}")
        if result["errors"]:
            print("errors:")
            for error in result["errors"]:
                print(f"- {error}")
        if result["warnings"]:
            print("warnings:")
            for warning in result["warnings"]:
                print(f"- {warning}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
