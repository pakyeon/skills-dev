---
name: kis-code-assistant
description: Search Korea Investment & Securities Open API entries, retrieve official example source code from the open-trading-api repository, and generate KIS Python snippets or implementation plans. Use this skill whenever the user wants KIS API discovery, example code lookup, category selection, or Python code generation for KIS Open API workflows.
---

# KIS Code Assistant Skill

This skill is the lightweight replacement for `KIS Code Assistant MCP`.

Use it for:

- Finding the right KIS Open API by natural-language intent
- Retrieving the official example source code behind a matched API
- Generating Python code that follows the KIS example layout
- Deciding when execution requires `Kis Trading MCP` instead of code generation alone

This file is only the entrypoint. Do not load every document by default.

## Navigation

- Read [`docs/overview.md`](docs/overview.md) first for capability boundaries and the relationship to `Kis Trading MCP`.
- Read [`docs/search-workflow.md`](docs/search-workflow.md) when the user needs API discovery or category selection.
- Read [`docs/code-generation.md`](docs/code-generation.md) when the user asks for code, a usage example, or an implementation plan.
- Read [`docs/standalone-projects.md`](docs/standalone-projects.md) when the user is not already working inside the upstream `open-trading-api` layout.
- Read [`docs/kis-trading-mcp-setup.md`](docs/kis-trading-mcp-setup.md) only if the user wants live execution through `Kis Trading MCP`.
- Read one category guide from `docs/categories/` only after the correct category has been chosen.

## Tools In This Skill

- `scripts/search_api.py`
  Search the bundled KIS API index and return MCP-like JSON.
- `scripts/read_source_code.py`
  Convert KIS GitHub URLs into raw example code fetches and return MCP-like JSON.

## Required Workflow

1. Determine whether the request is discovery, code generation, or live execution.
2. If the request is discovery or code generation, run `scripts/search_api.py` before answering.
3. If the selected API has `url_main` or `url_chk`, run `scripts/read_source_code.py` before writing code.
4. If the user wants discovery, example code, or generated code for live quotes or WebSocket use cases, stay in this skill and generate code first.
5. Only load the Trading MCP setup guide when the user needs actual runtime execution against a live or paper environment, account access, or order flow.

## Defaults

- Keep outputs concise and practical.
- Preserve Korean API names and subcategory labels when they come from the bundled dataset.
- Do not guess undocumented request parameters when the official example code can be fetched first.
