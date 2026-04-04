<div align="center">
  <h1>Devloop</h1>
  <p>A tiny GitHub Issues bridge for Codex and coding agents.</p>
</div>

Devloop keeps a simple loop between your coding agent and GitHub Issues. I built this because I needed a reliable way to sync issues with Codex while staying fast and minimal.

## Demo
![Devloop Demo](./assets/demo.gif)

## What It Does
- GitHub OAuth device flow (no local web server required)
- Create, edit, list, and get issues from the CLI
- Compact `/d` command mode optimized for agent workflows

## Installation
1. Clone this repo.
2. Copy `.env.example` to `.env` and set your OAuth client id:

```
GITHUB_CLIENT_ID=your_oauth_client_id
```

3. Run the one-click installer (Windows PowerShell):

```
.\install.ps1
```

This will:
- Install `devloop.cmd` and `devloop.ps1` launchers
- Install the Codex skill entry
- Start GitHub device authorization (browser opens automatically)

## Quick Start
1. Authenticate (if you skipped the installer):

```
python cli.py auth
```

2. Create an issue:

```
python cli.py create owner/name "Title" "Body"
```

3. Use compact mode (agent-friendly):

```
python cli.py /d c k=b t="login fail" b="c=token expires;e=refresh works;a=retry ok,refresh ok"
```

## Commands
- `python cli.py auth`
- `python cli.py create owner/name "Title" "Body"`
- `python cli.py edit owner/name 123 "New title" "New body" "closed"`
- `python cli.py list owner/name`
- `python cli.py get owner/name 123`
- `python cli.py /d ...`
