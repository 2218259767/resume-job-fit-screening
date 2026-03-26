# resume-job-fit-screening

`resume-job-fit-screening` is a Codex skill for screening and ranking jobs from a careers search-results URL against either:

- a local account with stored resume and long-term preferences
- a plain-text resume provided for the current run

It is designed to keep private user state local while allowing public job-site access notes to be shared from a separate repository.

## What This Skill Does

- resolves a stable site slug from a recruitment URL
- prefers site notes in this order: `local > synced > bundled`
- supports local runtime state for accounts, synced notes, local overrides, and publish queue
- applies strict rule-based screening plus a second-pass harsh JD review
- outputs evidence-backed Markdown shortlists

## Repository Layout

```text
.
├── SKILL.md
├── agents/openai.yaml
├── scripts/
├── references/
│   ├── bundled_site_notes/
│   ├── account_template.md
│   ├── site_note_template.md
│   ├── jd_matching_methodology.md
│   ├── strict_reviewer_prompt.md
│   └── output_format.md
├── README.md
├── LICENSE
└── .gitignore
```

## Install

Clone or copy this repository into your Codex skills directory as:

```text
~/.codex/skills/resume-job-fit-screening
```

The repository root is also the skill root. `SKILL.md` must stay at the root.

## Initialize Local Runtime

```bash
python ~/.codex/skills/resume-job-fit-screening/scripts/init_runtime.py
```

This creates runtime state under:

```text
~/.codex/data/resume-job-fit-screening/
```

That runtime directory is private and should not be committed or published.

## Optional Community Site Notes

This skill is intended to work with a separate public repository for site notes, for example:

```text
resume-job-fit-screening-site-notes
```

After that repository is public, point runtime config at its raw GitHub URLs:

```bash
python ~/.codex/skills/resume-job-fit-screening/scripts/init_runtime.py \
  --registry-enabled true \
  --registry-manifest-url https://raw.githubusercontent.com/<github-user>/resume-job-fit-screening-site-notes/main/index.json \
  --registry-notes-base-url https://raw.githubusercontent.com/<github-user>/resume-job-fit-screening-site-notes/main/
```

## Important Privacy Rules

- Do not commit `~/.codex/data/resume-job-fit-screening/`
- Do not publish personal accounts or local private notes
- Do not publish notes that contain cookies, tokens, or private headers

## Status

This repository is the v2 skill with:

- local accounts
- runtime separation
- bundled v2 site notes
- site note validation and sync helpers
- manifest builder for the separate site-notes repo
