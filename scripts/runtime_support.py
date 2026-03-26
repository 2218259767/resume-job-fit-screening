#!/usr/bin/env python3
"""Shared helpers for the resume-job-fit-screening skill runtime."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


GENERIC_LABELS = {
    "career",
    "careers",
    "campus",
    "hire",
    "hiring",
    "hr",
    "job",
    "jobs",
    "joinus",
    "recruit",
    "recruitment",
    "talent",
    "work",
    "zhaopin",
}

ATS_LABELS = {
    "boards",
    "greenhouse",
    "jobvite",
    "lever",
    "myworkdayjobs",
    "smartrecruiters",
    "workable",
    "workday",
}

TLD_LABELS = {
    "ai",
    "cn",
    "co",
    "com",
    "dev",
    "edu",
    "gov",
    "hk",
    "info",
    "io",
    "me",
    "net",
    "org",
    "tv",
    "uk",
    "us",
    "www",
}

SKIP_LABELS = GENERIC_LABELS | ATS_LABELS | TLD_LABELS


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "job-site"


def candidate_slugs(host: str) -> list[str]:
    candidates: list[str] = []
    for label in reversed(host.lower().split(".")):
        cleaned = re.sub(r"[^a-z0-9-]+", "", label)
        if not cleaned or cleaned in SKIP_LABELS or cleaned.isdigit():
            continue
        slug = slugify(cleaned)
        if slug not in candidates:
            candidates.append(slug)
    return candidates


def infer_skill_root(script_path: str | Path) -> Path:
    return Path(script_path).resolve().parents[1]


def default_runtime_root() -> Path:
    return Path.home() / ".codex" / "data" / "resume-job-fit-screening"


def runtime_subpaths(runtime_root: Path) -> dict[str, Path]:
    return {
        "runtime_root": runtime_root,
        "config_path": runtime_root / "config.yaml",
        "account_root": runtime_root / "accounts",
        "registry_root": runtime_root / "registry",
        "registry_index_path": runtime_root / "registry" / "index.json",
        "registry_sync_state_path": runtime_root / "registry" / "last_sync.json",
        "site_notes_root": runtime_root / "site_notes",
        "local_note_root": runtime_root / "site_notes" / "local",
        "synced_note_root": runtime_root / "site_notes" / "synced",
        "conflict_root": runtime_root / "site_notes" / "conflicts",
        "publish_queue_root": runtime_root / "publish_queue",
    }


def ensure_runtime_layout(runtime_root: Path) -> dict[str, Path]:
    paths = runtime_subpaths(runtime_root)
    runtime_root.mkdir(parents=True, exist_ok=True)
    for key in (
        "account_root",
        "registry_root",
        "local_note_root",
        "synced_note_root",
        "conflict_root",
        "publish_queue_root",
    ):
        paths[key].mkdir(parents=True, exist_ok=True)
    return paths


def bundled_note_root(skill_root: Path) -> Path:
    bundled = skill_root / "references" / "bundled_site_notes"
    if bundled.exists():
        return bundled
    return skill_root / "references" / "site_notes"


def legacy_bundled_note_root(skill_root: Path) -> Path:
    return skill_root / "references" / "site_notes"


def default_config() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "registry_enabled": False,
        "registry_manifest_url": "",
        "registry_notes_base_url": "",
        "prompt_on_sync_update": True,
        "auto_sync_target_site": False,
        "default_account": "",
    }


def _parse_list(raw: str) -> list[str]:
    inner = raw[1:-1].strip()
    if not inner:
        return []
    return [item.strip().strip("'\"") for item in inner.split(",")]


def _parse_scalar(raw: str) -> Any:
    value = raw.strip()
    if value == "":
        return ""
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if value.lower() == "null":
        return None
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if value.startswith("[") and value.endswith("]"):
        return _parse_list(value)
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def load_simple_yaml_text(text: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in raw_line:
            continue
        key, raw_value = raw_line.split(":", 1)
        data[key.strip()] = _parse_scalar(raw_value)
    return data


def dump_simple_yaml(data: dict[str, Any]) -> str:
    lines: list[str] = []
    for key, value in data.items():
        if isinstance(value, bool):
            rendered = "true" if value else "false"
        elif isinstance(value, int):
            rendered = str(value)
        elif value is None:
            rendered = "null"
        elif isinstance(value, list):
            rendered = json.dumps(value, ensure_ascii=False)
        elif value == "":
            rendered = '""'
        else:
            rendered = json.dumps(str(value), ensure_ascii=False)
        lines.append(f"{key}: {rendered}")
    return "\n".join(lines) + "\n"


def load_simple_yaml_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return load_simple_yaml_text(path.read_text(encoding="utf-8"))


def save_simple_yaml_file(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_simple_yaml(data), encoding="utf-8")


def load_config(runtime_root: Path) -> dict[str, Any]:
    config = default_config()
    config.update(load_simple_yaml_file(runtime_subpaths(runtime_root)["config_path"]))
    return config


def save_config(runtime_root: Path, config: dict[str, Any]) -> Path:
    path = runtime_subpaths(runtime_root)["config_path"]
    merged = default_config()
    merged.update(config)
    save_simple_yaml_file(path, merged)
    return path


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    marker = "\n---\n"
    end = text.find(marker, 4)
    if end == -1:
        return {}, text
    raw_meta = text[4:end]
    body = text[end + len(marker) :]
    return load_simple_yaml_text(raw_meta), body


def render_frontmatter(metadata: dict[str, Any], body: str) -> str:
    normalized_body = body.lstrip("\n")
    return f"---\n{dump_simple_yaml(metadata)}---\n\n{normalized_body}"


def read_markdown_with_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    return parse_frontmatter(path.read_text(encoding="utf-8"))


def write_markdown_with_frontmatter(
    path: Path, metadata: dict[str, Any], body: str
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_frontmatter(metadata, body), encoding="utf-8")


def note_paths_for_slug(
    site_slug: str, skill_root: Path, runtime_root: Path
) -> dict[str, Path]:
    paths = runtime_subpaths(runtime_root)
    return {
        "bundled": bundled_note_root(skill_root) / f"{site_slug}.md",
        "legacy_bundled": legacy_bundled_note_root(skill_root) / f"{site_slug}.md",
        "synced": paths["synced_note_root"] / f"{site_slug}.md",
        "local": paths["local_note_root"] / f"{site_slug}.md",
    }


def select_note_for_slug(
    site_slug: str, skill_root: Path, runtime_root: Path
) -> dict[str, Any]:
    note_paths = note_paths_for_slug(site_slug, skill_root, runtime_root)
    for source in ("local", "synced", "bundled", "legacy_bundled"):
        path = note_paths[source]
        if path.exists():
            selected_source = "bundled" if source == "legacy_bundled" else source
            return {
                "selected_note_path": path,
                "selected_note_source": selected_source,
                "note_exists": True,
                "note_paths": note_paths,
            }
    return {
        "selected_note_path": note_paths["local"],
        "selected_note_source": "none",
        "note_exists": False,
        "note_paths": note_paths,
    }


def today_iso_date() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def timestamp_slug() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def account_path(account_root: Path, account_id: str) -> Path:
    return account_root / f"{slugify(account_id)}.md"


def set_default_account(runtime_root: Path, account_id: str) -> None:
    paths = ensure_runtime_layout(runtime_root)
    selected_path = account_path(paths["account_root"], account_id)
    if not selected_path.exists():
        raise FileNotFoundError(f"account not found: {selected_path}")

    for path in sorted(paths["account_root"].glob("*.md")):
        metadata, body = read_markdown_with_frontmatter(path)
        metadata["default_account"] = path == selected_path
        metadata["updated_at"] = today_iso_date()
        write_markdown_with_frontmatter(path, metadata, body)

    config = load_config(runtime_root)
    config["default_account"] = slugify(account_id)
    save_config(runtime_root, config)


def append_bullet_to_section(body: str, heading: str, line: str) -> str:
    heading_text = f"## {heading}"
    pattern = re.compile(
        rf"(?ms)^## {re.escape(heading)}\n\n(.*?)(?=^## |\Z)"
    )
    match = pattern.search(body)
    bullet = f"- {line.strip()}"

    if match:
        content = match.group(1).strip()
        if content == "-":
            content = ""
        updated = bullet if not content else f"{content}\n{bullet}"
        replacement = f"{heading_text}\n\n{updated}\n\n"
        return body[: match.start()] + replacement + body[match.end() :]

    suffix = f"\n\n{heading_text}\n\n{bullet}\n"
    return body.rstrip() + suffix + "\n"
