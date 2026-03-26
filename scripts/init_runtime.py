#!/usr/bin/env python3
"""Initialize runtime directories and config for the skill."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime_support import (
    default_runtime_root,
    ensure_runtime_layout,
    load_config,
    save_config,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Initialize runtime state for resume-job-fit-screening."
    )
    parser.add_argument(
        "--runtime-root",
        default=None,
        help="Override runtime root. Defaults to ~/.codex/data/resume-job-fit-screening",
    )
    parser.add_argument(
        "--registry-enabled",
        choices=("true", "false"),
        default=None,
        help="Whether community registry sync is enabled.",
    )
    parser.add_argument(
        "--registry-manifest-url",
        default=None,
        help="Manifest URL for the site note registry.",
    )
    parser.add_argument(
        "--registry-notes-base-url",
        default=None,
        help="Base URL for registry note files.",
    )
    parser.add_argument(
        "--default-account",
        default=None,
        help="Default account id to record in config.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    runtime_root = (
        Path(args.runtime_root).expanduser().resolve()
        if args.runtime_root
        else default_runtime_root()
    )
    paths = ensure_runtime_layout(runtime_root)

    config = load_config(runtime_root)
    if args.registry_enabled is not None:
        config["registry_enabled"] = args.registry_enabled == "true"
    if args.registry_manifest_url is not None:
        config["registry_manifest_url"] = args.registry_manifest_url
    if args.registry_notes_base_url is not None:
        config["registry_notes_base_url"] = args.registry_notes_base_url
    if args.default_account is not None:
        config["default_account"] = args.default_account

    config_path = save_config(runtime_root, config)
    summary = {
        "runtime_root": str(runtime_root),
        "config_path": str(config_path),
        "account_root": str(paths["account_root"]),
        "local_note_root": str(paths["local_note_root"]),
        "synced_note_root": str(paths["synced_note_root"]),
        "conflict_root": str(paths["conflict_root"]),
        "publish_queue_root": str(paths["publish_queue_root"]),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
