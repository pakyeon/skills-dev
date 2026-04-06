# Overview

`KIS Code Assistant MCP` had three main jobs:

- search the KIS API catalog
- fetch official example source code from `open-trading-api`
- guide the model toward code generation instead of blind guessing

This skill keeps those jobs, but moves them into a context-efficient structure:

- small entrypoint in `SKILL.md`
- linked guidance documents
- bundled scripts for deterministic search and source retrieval

## What This Skill Covers

- API discovery across 8 KIS API categories
- category and subcategory routing
- official example source lookup from GitHub
- Python code generation guidance based on the KIS sample layout

## What This Skill Does Not Cover

- direct brokerage execution
- live account access
- live market data retrieval
- order placement, cancellation, or account mutations
- long-running WebSocket execution

Those capabilities belong to `Kis Trading MCP`.

## Relationship To Kis Trading MCP

Use this skill alone when the user needs:

- “Which API should I use?”
- “Show me the example code”
- “Generate Python code for this KIS API task”
- “Show me how to subscribe to real-time data”

Use this skill plus `Kis Trading MCP` when the user needs:

- live quotes
- account balances
- order execution
- real or paper trading environment access
- runtime validation against the brokerage environment

Important distinction:

- requests for code or architecture for real-time data still belong here
- requests to actually run that code against KIS belong to `Kis Trading MCP`

If `Kis Trading MCP` is not installed, stop at code generation and explain the gap clearly.

## Supported Categories

- `auth`
- `domestic_stock`
- `domestic_bond`
- `domestic_futureoption`
- `overseas_stock`
- `overseas_futureoption`
- `elw`
- `etfetn`

Load one of the category guides only after search results point to the right category:

- [`categories/auth-and-bond.md`](categories/auth-and-bond.md)
- [`categories/domestic-stock.md`](categories/domestic-stock.md)
- [`categories/futures-and-overseas.md`](categories/futures-and-overseas.md)
- [`categories/elw-etf-etn.md`](categories/elw-etf-etn.md)
