#!/usr/bin/env python3
"""Sync community site notes into the local runtime cache."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import urlopen

from runtime_support import (
    default_runtime_root,
    ensure_runtime_layout,
    load_config,
)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def fetch_text(url: str) -> str:
    with urlopen(url) as response:  # noqa: S310 - explicit user/config URL
        return response.read().decode("utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync community site notes into the local runtime cache."
    )
    parser.add_argument(
        "--runtime-root",
        default=None,
        help="Override runtime root. Defaults to ~/.codex/data/resume-job-fit-screening",
    )
    parser.add_argument("--manifest-url", default=None)
    parser.add_argument("--notes-base-url", default=None)
    parser.add_argument("--site-slug", default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    return parser.parse_args()


def note_url(base_url: str, relative_path: str) -> str:
    normalized = base_url.rstrip("/") + "/"
    return urljoin(normalized, relative_path)


def main() -> int:
    args = parse_args()
    runtime_root = (
        Path(args.runtime_root).expanduser().resolve()
        if args.runtime_root
        else default_runtime_root()
    )
    paths = ensure_runtime_layout(runtime_root)
    config = load_config(runtime_root)

    manifest_url = args.manifest_url or config.get("registry_manifest_url", "")
    notes_base_url = args.notes_base_url or config.get("registry_notes_base_url", "")
    if not manifest_url:
        raise SystemExit("registry manifest URL is empty; configure it first")

    manifest_text = fetch_text(manifest_url)
    manifest = json.loads(manifest_text)
    paths["registry_index_path"].write_text(manifest_text, encoding="utf-8")

    updated: list[str] = []
    skipped: list[str] = []
    downloaded: list[str] = []

    for note in manifest.get("notes", []):
        site_slug = note.get("site_slug", "")
        if args.site_slug and site_slug != args.site_slug:
            continue
        relative_path = note.get("path", "")
        if not relative_path:
            skipped.append(site_slug or "<missing-site-slug>")
            continue

        target_path = paths["synced_note_root"] / f"{site_slug}.md"
        current_hash = (
            sha256_text(target_path.read_text(encoding="utf-8"))
            if target_path.exists()
            else ""
        )
        remote_hash = note.get("sha256", "")

        if current_hash and current_hash == remote_hash:
            skipped.append(site_slug)
            continue

        if args.dry_run:
            updated.append(site_slug)
            continue

        source_url = note_url(notes_base_url, relative_path) if notes_base_url else relative_path
        note_text = fetch_text(source_url)
        downloaded_hash = sha256_text(note_text)
        if remote_hash and downloaded_hash != remote_hash:
            raise SystemExit(f"hash mismatch for {site_slug}: {downloaded_hash} != {remote_hash}")
        target_path.write_text(note_text, encoding="utf-8")
        updated.append(site_slug)
        downloaded.append(source_url)

    summary = {
        "manifest_url": manifest_url,
        "notes_base_url": notes_base_url,
        "updated": updated,
        "skipped": skipped,
        "downloaded": downloaded,
        "dry_run": args.dry_run,
        "registry_index_path": str(paths["registry_index_path"]),
    }
    if args.format == "json":
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"manifest_url: {manifest_url}")
        print(f"updated: {', '.join(updated) if updated else '(none)'}")
        print(f"skipped: {', '.join(skipped) if skipped else '(none)'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
