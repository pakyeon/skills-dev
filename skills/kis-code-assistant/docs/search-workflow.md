# Search Workflow

Use this document when the user does not already know the exact KIS API.

## Search Principle

Always search the bundled API index before generating code.

The bundled search script preserves the same behavior as the original MCP:

- exact match for `category` and `subcategory`
- case-insensitive substring match for `api_name`, `function_name`, and `description`
- `query` is treated as a broad natural-language fallback across `api_name`, `function_name`, `description`, `args`, and `example`
- `response` is treated as a fallback against `returns`, `column_mapping`, `description`, and `example`
- maximum returned detailed results: 10

## Search Command

```bash
python3 scripts/search_api.py --category domestic_stock --api-name "주식현재가 시세"
```

The script returns MCP-like JSON with:

- `status`
- `message`
- `total_count`
- `results`

Detailed search results also expose:

- `description`
- `args`
- `returns`
- `example`
- `column_mapping`

## Routing Rules

1. Start with the most specific known category if the user already implies one.
2. If category is unclear, infer it from the task:
   - domestic equity trading or KRX tickers: `domestic_stock`
   - overseas equity or US ticker examples: `overseas_stock`
   - account auth or WebSocket key issuance: `auth`
   - bond workflows: `domestic_bond`
   - derivatives: `domestic_futureoption` or `overseas_futureoption`
   - ELW: `elw`
   - ETF or ETN pricing and NAV: `etfetn`
3. Prefer `function_name` or `api_name` when a stable keyword exists.
4. Use `subcategory` when the request is broad, such as “real-time quotes” or “order/account”.
5. If the first search fails, retry in this order:
   - only `category`
   - `function_name`
   - `api_name`
   - `subcategory`
   - broad `query`

## Result Handling

- If only `category` or only `subcategory` is supplied, treat the output as a compact browsing list.
- If multiple filters are supplied, treat the output as candidate selection and inspect `url_main` and `url_chk`.
- If multiple APIs match, use `description`, `args`, `returns`, and `example` to disambiguate before generating code.

## After Search

Once a candidate API is selected:

1. run `scripts/read_source_code.py`
2. inspect the official example code
3. only then generate Python code or implementation guidance
