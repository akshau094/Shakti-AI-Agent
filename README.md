# Shakti AI Agent

A Windows desktop coding assistant in development, built around local inference,
persistent memory, and reviewed code changes.

## First milestone: backend foundation

This initial upload contains the Python backend and its tests. It supports a
loopback-only Ollama connection, SQLite conversation and memory storage, document
extraction and indexing, retrieval, and a bounded code-reading/change-proposal
loop. Existing files are backed up when a reviewed proposal is applied.

The desktop interface and installation scripts will be published in later
milestones. This commit is a backend library, not an installable desktop release.
Model weights and private conversations are not included.

## Check the backend

Requires Python 3.10 or later:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-core.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_core.py -v
```

These tests use a fake inference provider and temporary files; they do not need
downloaded model weights. Live inference requires a separately installed local
Ollama server and suitable chat/embedding weights.

## Upcoming milestones

- White desktop workspace and pixel mascots
- Local model setup, readiness checks and launch scripts
- Real-model acceptance checks
- Evaluation of document-processing and agent-framework integrations

Development will be published in meaningful increments as work is completed.
