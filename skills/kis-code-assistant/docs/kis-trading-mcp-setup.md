# Kis Trading MCP Setup

Load this document only when the user wants live execution instead of discovery or code generation.

## Role Separation

- This skill: API discovery, source lookup, code generation
- `Kis Trading MCP`: actual execution against KIS brokerage APIs

## Important Constraint

`Kis Trading MCP` is maintained inside the upstream `open-trading-api` repository. This skill does not bundle or manage it.

If the user does not want to clone the entire repository, the practical fallback is to fetch only the Trading MCP subtree with sparse checkout.

## Sparse Checkout Fallback

```bash
git clone --filter=blob:none --sparse https://github.com/koreainvestment/open-trading-api.git
cd open-trading-api
git sparse-checkout set "MCP/Kis Trading MCP"
cd "MCP/Kis Trading MCP"
```

## Expected Runtime Setup

- Docker 20.10+
- KIS app key and app secret
- optional paper-trading key pair
- account identifiers

## High-Level Steps

1. fetch the Trading MCP directory
2. build or run it according to its README
3. configure Claude Desktop or Cursor to connect to that MCP
4. verify health before relying on live execution

## Notes For Answers

- Do not imply that this skill can execute orders by itself.
- If Trading MCP is missing, provide code or setup guidance only.
- When discussing Trading MCP setup, keep the explanation short and point to the upstream documentation if deeper operational details are needed.
