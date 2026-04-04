# Devloop Skill (Compact Protocol)

This skill uses a **compact protocol** to minimize tokens between the user, agent, CLI, and GitHub.

## Global launcher (installed)
Launcher files:
- `C:\Users\Lenovo\.local\bin\devloop.cmd`
- `C:\Users\Lenovo\.local\bin\devloop.ps1`

How it resolves:
1) If `DEVLOOP_HOME` is set, it runs `python %DEVLOOP_HOME%\cli.py ...`
2) Otherwise, it walks up from the current directory until it finds `cli.py`

## Windows note (avoid drive-letter + pipe parsing)
On Windows shells, prefer `=` instead of `:` and `;` instead of `|`.
Both separators are supported, but `=` and `;` avoid parsing issues.

Example:
```
devloop /d c k=b t="login fail" b="c=token expires;e=refresh works"
```

## Core Commands (Ultra-Compressed)
Create:
- `/d c t="..." b="..." k=b`

List:
- `/d l`

Get:
- `/d g 12`

Edit:
- `/d e 12 t="..." b="..." s=d`

## Field Keys
- `t` title
- `b` body (compact schema allowed)
- `k` kind/type (`b` bug, `f` feature, `t` task, `r` research)
- `s` state (`o` open, `p` in_progress, `d` done)
- `r` repo override (`owner/name`)

## Defaults
- Repo: uses active repo from state (`devloop repo set owner/name`)
- Kind: task
- State: open

## Compact Body Schema
Use `b="c=...;e=...;s=...;a=..."` and CLI will expand it into the full issue template.

Keys:
- `c` context
- `e` expected
- `s` scope
- `a` acceptance criteria (comma-separated)

Example:
- `/d c k=b t="login fail" b="c=token expires;e=refresh works;a=retry ok,refresh ok"`

## Execution Mapping
Agent runs:
- `devloop /d ...`

Examples:
- User: `/d c k=b t="login fail" b="c=token expires;e=refresh works"`
- Agent: `devloop /d c k=b t="login fail" b="c=token expires;e=refresh works"`
