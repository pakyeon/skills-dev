# Domestic Stock Guide

Load this guide only after search results land in `domestic_stock`.

This is the largest KIS category in the bundled dataset.

## Typical Intents

- current price and asking price
- chart data
- rankings and market analysis
- stock metadata
- order and account workflows
- real-time quotes and notifications

## Common Subcategories

- `기본시세`
- `순위분석`
- `업종/기타`
- `주문/계좌`
- `시세분석`
- `종목정보`
- `실시간시세`

## Answering Pattern

1. narrow by subcategory if the user intent is broad
2. prefer `function_name` or `api_name` for exact price or balance requests
3. fetch source code before generating domestic stock examples

If the user asks for live quotes, subscriptions, or actual account reads, mention Trading MCP as the execution layer.
