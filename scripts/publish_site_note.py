#!/usr/bin/env python3
"""Queue a validated local site note for community publication."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from runtime_support import (
    default_runtime_root,
    ensure_runtime_layout,
    note_paths_for_slug,
    timestamp_slug,
)
from validate_site_note import validate_note


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Queue a local site note for manual publication or PR creation."
    )
    parser.add_argument(
        "--runtime-root",
        default=None,
        help="Override runtime root. Defaults to ~/.codex/data/resume-job-fit-screening",
    )
    parser.add_argument(
        "--skill-root",
        default=None,
        help="Required when using --site-slug to resolve note locations.",
    )
    parser.add_argument("--note-path", default=None)
    parser.add_argument("--site-slug", default=None)
    return parser.parse_args()


def resolve_note_path(args: argparse.Namespace, runtime_root: Path) -> Path:
    if args.note_path:
        return Path(args.note_path).expanduser().resolve()
    if args.site_slug and args.skill_root:
        paths = note_paths_for_slug(
            args.site_slug,
            Path(args.skill_root).expanduser().resolve(),
            runtime_root,
        )
        return paths["local"]
    raise SystemExit("provide --note-path or both --site-slug and --skill-root")


def main() -> int:
    args = parse_args()
    runtime_root = (
        Path(args.runtime_root).expanduser().resolve()
        if args.runtime_root
        else default_runtime_root()
    )
    paths = ensure_runtime_layout(runtime_root)
    note_path = resolve_note_path(args, runtime_root)
    if not note_path.exists():
        raise SystemExit(f"note not found: {note_path}")

    result = validate_note(note_path)
    if not result["valid"]:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1

    metadata = result["metadata"]
    if not metadata.get("public_safe", False):
        raise SystemExit("note is not marked public_safe=true and cannot be queued")

    queue_dir = paths["publish_queue_root"] / f"{timestamp_slug()}_{metadata['site_slug']}"
    queue_dir.mkdir(parents=True, exist_ok=True)
    queued_note = queue_dir / note_path.name
    shutil.copy2(note_path, queued_note)

    submission = {
        "site_slug": metadata["site_slug"],
        "source_note_path": str(note_path),
        "queued_note_path": str(queued_note),
        "maintainer": metadata.get("maintainer", ""),
        "verified_at": metadata.get("verified_at", ""),
        "recommended_next_step": "Open a PR to the community site-notes repo with the queued note file.",
    }
    (queue_dir / "submission.json").write_text(
        json.dumps(submission, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(submission, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
