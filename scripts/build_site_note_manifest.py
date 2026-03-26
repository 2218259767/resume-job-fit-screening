#!/usr/bin/env python3
"""Build an index.json manifest for a directory of validated site notes."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from runtime_support import today_iso_date
from validate_site_note import validate_note


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a manifest for a site-notes repository."
    )
    parser.add_argument("notes_root", help="Directory containing *.md site notes")
    parser.add_argument(
        "--output",
        default=None,
        help="Manifest path. Defaults to <repo_root>/index.json",
    )
    parser.add_argument(
        "--path-prefix",
        default="site_notes",
        help="Relative path prefix used in manifest note paths",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    notes_root = Path(args.notes_root).expanduser().resolve()
    if not notes_root.exists():
        raise SystemExit(f"notes_root not found: {notes_root}")

    manifest_path = (
        Path(args.output).expanduser().resolve()
        if args.output
        else notes_root.parent / "index.json"
    )

    notes: list[dict[str, object]] = []
    for path in sorted(notes_root.glob("*.md")):
        result = validate_note(path)
        if not result["valid"]:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            raise SystemExit(f"invalid note: {path}")
        metadata = result["metadata"]
        notes.append(
            {
                "site_slug": metadata["site_slug"],
                "path": f"{args.path_prefix.rstrip('/')}/{path.name}",
                "sha256": sha256_file(path),
                "content_version": metadata["content_version"],
                "verified_at": metadata["verified_at"],
                "public_safe": metadata["public_safe"],
                "access_mode": metadata["access_mode"],
                "method_type": metadata["method_type"],
            }
        )

    manifest = {
        "schema_version": 1,
        "generated_at": today_iso_date(),
        "notes": notes,
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"manifest_path": str(manifest_path), "note_count": len(notes)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
