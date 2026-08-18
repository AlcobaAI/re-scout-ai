# re-scout-ai

A multi-agent research assistant for discovering, verifying, and storing datasets and academic papers.

## What it does

`re-scout-ai` runs a three-stage workflow:

1. **Planner** — refines an input topic into a structured, data-focused research plan.
2. **Scout** — searches the web, arXiv, and other sources to identify relevant papers and datasets.
3. **Engineer** — downloads or clones promising sources into a local research sandbox for verification.

The app stores findings in a local SQLite database and exposes a simple Gradio UI for launching research runs and browsing saved results.

## Key features

- Web and arXiv search for research leads
- Multi-agent orchestration with LangGraph
- Playwright-powered browser automation
- Local Python execution for downloads and cloning
- SQLite-backed archive for datasets and papers
- Gradio interface for running research sessions

## Project structure

- `main.py` — Gradio app entrypoint
- `graph.py` — LangGraph workflow wiring
- `agents/` — planner, scout, and engineer agents
- `tools/` — search, browser, code, database, and planning tools
- `database.py` — SQLite schema and persistence helpers
- `state.py` — shared graph state definition

## How it works

1. Enter a research topic in the UI.
2. The planner creates a sourcing plan and success criteria.
3. The scout searches for papers and datasets and saves promising leads.
4. The engineer attempts to download or clone those leads into `research_sandbox/`.
5. The app records datasets and papers in `research_archive.db`.

## Requirements

- Python 3.12+
- API keys / environment variables for the search and LLM tools used by the agents
  - `SERPAPI_API_KEY`
  - any OpenAI credentials required by `langchain_openai`

## Installation

```bash
uv sync
```

or, if you use pip:

```bash
pip install -e .
```

## Running the app

```bash
python main.py
```

This launches the Gradio interface and starts the research workflow.

## Data storage

The app creates these local artifacts:

- `research_archive.db` — SQLite database for papers, datasets, and links
- `research_sandbox/` — workspace for downloaded files and cloned repositories

These paths are ignored by git in `.gitignore`.

## Notes

- The planner, scout, and engineer are all tool-using LLM agents.
- GitHub sources are intended to be cloned with Python code rather than browser downloads.
- arXiv and paper sources may be discovered through search and then downloaded into the sandbox.
