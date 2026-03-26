#!/usr/bin/env python3
"""Infer site slug, note sources, runtime paths, and report name from a search URL."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from runtime_support import (
    bundled_note_root,
    candidate_slugs,
    default_runtime_root,
    ensure_runtime_layout,
    infer_skill_root,
    note_paths_for_slug,
    runtime_subpaths,
    select_note_for_slug,
    slugify,
)


def infer_workspace_root() -> Path:
    return Path.cwd().resolve()


def resolve_site_slug(
    host: str, explicit_slug: str | None, candidate_roots: list[Path]
) -> tuple[str, list[str]]:
    if explicit_slug:
        slug = slugify(explicit_slug)
        return slug, [slug]

    candidates = candidate_slugs(host)
    for candidate in candidates:
        for root in candidate_roots:
            if (root / f"{candidate}.md").exists():
                return candidate, candidates

    if candidates:
        return candidates[0], candidates

    return slugify(host), []


def build_summary(
    url: str,
    site_slug: str,
    candidates: list[str],
    skill_root: Path,
    workspace_root: Path,
    runtime_root: Path,
    bundled_root: Path,
    report_root: Path,
    report_date: str,
) -> dict[str, object]:
    parsed = urlparse(url)
    runtime_paths = runtime_subpaths(runtime_root)
    selected = select_note_for_slug(site_slug, skill_root, runtime_root)
    note_paths = note_paths_for_slug(site_slug, skill_root, runtime_root)
    report_path = report_root / f"{site_slug}_resume_match_{report_date}.md"
    return {
        "input_url": url,
        "host": parsed.netloc.lower(),
        "site_slug": site_slug,
        "candidate_slugs": candidates,
        "skill_root": str(skill_root),
        "workspace_root": str(workspace_root),
        "runtime_root": str(runtime_root),
        "config_path": str(runtime_paths["config_path"]),
        "account_root": str(runtime_paths["account_root"]),
        "bundled_note_root": str(bundled_root),
        "local_note_root": str(runtime_paths["local_note_root"]),
        "synced_note_root": str(runtime_paths["synced_note_root"]),
        "bundled_note_path": str(note_paths["bundled"]),
        "legacy_bundled_note_path": str(note_paths["legacy_bundled"]),
        "local_note_path": str(note_paths["local"]),
        "synced_note_path": str(note_paths["synced"]),
        "bundled_note_exists": note_paths["bundled"].exists()
        or note_paths["legacy_bundled"].exists(),
        "local_note_exists": note_paths["local"].exists(),
        "synced_note_exists": note_paths["synced"].exists(),
        "selected_note_path": str(selected["selected_note_path"]),
        "selected_note_source": selected["selected_note_source"],
        "note_path": str(selected["selected_note_path"]),
        "note_exists": selected["note_exists"],
        "suggested_report_path": str(report_path),
    }


def validate_report_date(value: str | None) -> str:
    if value is None:
        return date.today().strftime("%Y%m%d")
    if not re.fullmatch(r"\d{8}", value):
        raise ValueError("report date must be in YYYYMMDD format")
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Infer a site slug, note path, and report file name from a job-search URL."
        )
    )
    parser.add_argument("url", help="Recruitment search-results URL")
    parser.add_argument(
        "--site-slug",
        help="Optional explicit slug override, for example 'meituan'",
    )
    parser.add_argument(
        "--runtime-root",
        default=None,
        help="Runtime root containing accounts and synced/local notes",
    )
    parser.add_argument(
        "--report-root",
        default=None,
        help="Directory where reports should be written",
    )
    parser.add_argument(
        "--report-date",
        default=None,
        help="Override report date in YYYYMMDD format",
    )
    parser.add_argument(
        "--bundled-root",
        default=None,
        help="Optional override for the bundled site note root inside the skill",
    )
    parser.add_argument(
        "--format",
        choices=("json", "text"),
        default="json",
        help="Output format",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    parsed = urlparse(args.url)
    if not parsed.scheme or not parsed.netloc:
        raise SystemExit("URL must include scheme and host, for example https://...")

    skill_root = infer_skill_root(__file__)
    workspace_root = infer_workspace_root()
    runtime_root = (
        Path(args.runtime_root).expanduser().resolve()
        if args.runtime_root
        else default_runtime_root()
    )
    ensure_runtime_layout(runtime_root)
    bundled_root = (
        Path(args.bundled_root).expanduser().resolve()
        if args.bundled_root
        else bundled_note_root(skill_root)
    )
    report_root = (
        Path(args.report_root).expanduser().resolve()
        if args.report_root
        else workspace_root
    )
    report_date = validate_report_date(args.report_date)
    site_slug, candidates = resolve_site_slug(
        parsed.netloc,
        args.site_slug,
        [
            runtime_subpaths(runtime_root)["local_note_root"],
            runtime_subpaths(runtime_root)["synced_note_root"],
            bundled_root,
        ],
    )

    summary = build_summary(
        args.url,
        site_slug,
        candidates,
        skill_root,
        workspace_root,
        runtime_root,
        bundled_root,
        report_root,
        report_date,
    )

    if args.format == "text":
        for key, value in summary.items():
            print(f"{key}: {value}")
        return 0

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
