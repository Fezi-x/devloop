# Devloop

Devloop is a lightweight GitHub Issues workflow intended for use with a Coding Agent.

## What it does
- OAuth device flow to get a GitHub token
- Create, edit, and list issues via a simple CLI

## Quick start
1) Create a `.env` file with your OAuth client id:

```
GITHUB_CLIENT_ID=your_oauth_client_id
```

2) Authenticate:

```
python cli.py auth
```

3) Create an issue:

```
python cli.py create owner/name "Title" "Body"
```

## Commands
- `python cli.py auth`
- `python cli.py create owner/name "Title" "Body"`
- `python cli.py edit owner/name 123 "New title" "New body" "closed"`
- `python cli.py list owner/name`
