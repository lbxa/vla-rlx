---
name: gh-address-comments
description: Inspect or address GitHub pull request review comments. Use when asked to triage review threads, apply requested fixes, or summarize the disposition of feedback.
metadata:
  short-description: Address comments in a GitHub PR review
---

# PR Comment Handler

Use the PR the user names, or find the open PR for the current branch. Prefer the connected GitHub tools when they expose the relevant comments and thread state.

Use `scripts/fetch_comments.py` from this skill when the connected tools lack inline review details for the current branch's PR. Check `gh auth status` before using the helper. If authentication is missing, use an available connector or ask the user to authenticate with `gh auth login`.

## Review workflow

1. Read the requested threads and inspect the current code around each actionable comment. Check whether it has already been resolved or superseded by a later commit.
2. When the user requests changes, apply the in-scope fixes and run the relevant checks. Clarify ambiguous requests when their resolution would expand the task or materially change behavior.
3. Summarize each addressed or deferred item with its thread link and relevant verification. Post replies or resolve remote threads only when the user authorizes those actions.
