# Devloop Skill (Coding Agent)

This skill runs a **passive capture system** that turns natural language into GitHub issues.
It does **not** require explicit `/devloop` commands unless you want to toggle mode.

## Mode
- `/devloop on` → enable passive capture
- `/devloop off` → disable passive capture

When mode is ON, the agent detects intent and asks for confirmation before creating an issue.

## Intent detection (trigger phrases)
Auto-create suggestions when the user says phrases like:
- "this is a bug"
- "this needs to be fixed"
- "track this"
- "we should build this"
- "add this to roadmap"
- "this broke"
- "crash"
- "doesn't work"
- "investigate"
- "refactor"
- "create an issue for this in github"
- "create an issue"
- "remember this issue"

## Classification
Detected types:
- `bug`
- `feature`
- `task`
- `research`

Title format:
- `[BUG] ...`, `[FEATURE] ...`, `[TASK] ...`, `[RESEARCH] ...`

## Issue template
Body is deterministic:

```
## Context
<what is happening / requested>

## Expected
<what should happen>

## Scope
<what part of system>

## Acceptance Criteria
- [ ] Condition 1
- [ ] Condition 2
```

## Repo handling
- The first time a repo is needed, ask for `owner/name`.
- Store it as the active repo and reuse it for future issues.
- The user can override by explicitly providing a repo slug.

## Execution
When the user confirms, the agent runs:

```
python cli.py create <owner/name> "[TYPE] Title" "<templated body>"
```

## Examples
Mode ON:
- User: `/devloop on`
- Agent: "Devloop mode enabled. I'll suggest issues automatically."

Auto-detection:
- User: "this is a bug: token refresh fails"
- Agent: "Detected bug. Create issue?"
- User: "yes"
- Agent runs: `python cli.py create owner/name "[BUG] token refresh fails" "<templated body>"`

List:
- User: "/devloop show me what issue does this repo have"
- Agent runs: `python cli.py list owner/name`

Get:
- User: "pull up issue #1 for owner/name"
- Agent runs: `python cli.py get owner/name 1`

Mode and repo management:
- `python cli.py mode on`
- `python cli.py mode off`
- `python cli.py repo set owner/name`
- `python cli.py repo get`

Bridge usage (for integrators):
- Preview detection: `python bridge.py "this is a bug: token refresh fails"`
- Create after confirm: `python bridge.py "this is a bug: token refresh fails" --confirm --repo owner/name`
