<div align="center">

# Shakti AI Agent

**A local AI workspace for code, documents, and persistent memory.**

Python 3.10+ · Local inference · Backend milestone · Desktop in development

[Get started](#get-started) · [Capabilities](#published-capabilities) · [Architecture](#how-it-works) · [Roadmap](#roadmap)

</div>

---

Shakti is being built as a Windows desktop assistant that helps you understand
code, propose fixes, and work with your own reference material. Its backend
connects to AI models running on your computer and stores conversation history,
explicit memories, and indexed documents locally.

> **Current public release:** the backend foundation and its tests. The desktop
> interface, mascots, launcher, and setup scripts are being developed locally
> and will be published in later milestones. This repository does not yet provide
> an installable desktop application.

## Published capabilities

| Area | Available in this milestone |
| --- | --- |
| Local AI connection | Chat and streamed responses through a loopback-only Ollama endpoint |
| Persistent memory | SQLite storage for conversations, explicit notes, and document chunks, separated by scope |
| Document extraction | Text-based PDF, DOCX, XLSX, UTF-8 text, CSV, and supported source files |
| Document retrieval | Chunking, embedding-based search, and source references in model context |
| Coding workflow | A bounded loop that reads files and proposes complete replacements for review |
| Reviewed writes | Diffs, stale-file detection, and backups of existing files before applying changes |
| Workspace boundaries | Project-relative paths; hidden, credential, runtime, and linked paths excluded |

These are backend APIs. A graphical workflow for using them is not included in
this public milestone.

## Get started

### Requirements

- Python **3.10 or later**; development currently targets Windows.
- Git to clone the repository.
- A local Ollama installation and downloaded weights **only for live AI use**.

### Install and test

Run these commands in PowerShell:

```powershell
git clone https://github.com/akshau094/Shakti-AI-Agent.git
cd Shakti-AI-Agent
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-core.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_core.py -v
```

The eight backend tests use a fake model provider and temporary files. They
exercise memory, document indexing, retrieval, file boundaries, reviewed writes,
and the agent loop without downloading weights or calling an AI service.

### Connect a local model

Install [Ollama](https://ollama.com/download), start its local server, and download
the models currently expected by the backend:

```powershell
ollama pull qwen2.5-coder:1.5b
ollama pull nomic-embed-text
```

The first model generates answers; the second creates document embeddings.
Downloads require internet access. The backend sends inference requests to
`http://127.0.0.1:11434` and bypasses system HTTP proxies.

Check the connection from the repository root:

```powershell
.\.venv\Scripts\python.exe -c "from shakti.core import LocalModel; print(LocalModel().models())"
```

This is a library connection check, not a desktop launch command. Model quality
and response speed depend on the selected weights, task, and available hardware.

## How it works

```text
Question or coding task
        |
        v
Conversation history + explicit memories + retrieved passages
        |
        v
Local model running through Ollama
        |
        +-- Answer with reference context
        |
        +-- Read project files -> propose a diff -> review -> apply with backup
```

Document ingestion extracts text, divides it into passages, and stores their
embeddings. Retrieval supplies relevant passages when answering a question.
Memory and retrieval provide context; saving information does not retrain model
weights. The coding agent cannot execute shell commands or automatically apply
its proposals.

## Repository layout

```text
shakti/
  __init__.py          Python package
  core.py              Inference, storage, ingestion, retrieval, and code proposals
tests/
  test_core.py         Backend behavior checks
requirements-core.txt  Document-processing dependencies
```

Local conversations, indexes, backups, downloaded runtimes, and model weights
are excluded from Git. The repository does not include private user data or
trained weights.

## Current limits

- Imports are limited to 20 MB per file and two million extracted characters.
- Scanned PDFs, images, audio, and video require OCR or transcription that is
  not included in this milestone.
- Coding tools work with text files up to 100 KB and have a ten-step agent limit.
- Proposed changes require review; model output can contain mistakes.
- Automatic training and self-improvement are not implemented in this release.
- OpenJarvis integration is under evaluation and is not part of this milestone.

## Roadmap

- [x] Local inference connection and streaming
- [x] Scoped conversation and explicit-memory storage
- [x] Document extraction, indexing, and retrieval
- [x] Reviewed file proposals and backend tests
- [ ] Publish the white desktop workspace and pixel mascots
- [ ] Publish local model setup, readiness checks, and launch scripts
- [ ] Publish real-model acceptance checks
- [ ] Evaluate stronger document processing and agent integrations
- [ ] Develop and evaluate a controlled learning workflow

The project is published in meaningful increments as development progresses.
Checked items refer to capabilities present in this repository; unchecked items
are not promises of a completed release.

## Feedback

Use [GitHub Issues](https://github.com/akshau094/Shakti-AI-Agent/issues) to report
bugs or suggest improvements. Include the steps to reproduce, Python version,
and a sanitised error message. Keep private documents, credentials, and personal
conversation history out of public reports.
