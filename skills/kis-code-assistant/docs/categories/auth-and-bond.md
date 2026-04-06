# Auth And Bond Guide

Load this guide only after search results land in `auth` or `domestic_bond`.

## `auth`

Typical intents:

- access token issuance
- WebSocket access key issuance
- auth bootstrap questions

Common subcategory label in the dataset:

- `인증`

## `domestic_bond`

Typical intents:

- bond price inquiry
- bond asking price
- issuance info
- bond balance and order history

Common subcategories:

- `기본시세`
- `주문/계좌`
- `실시간시세`

When a bond request asks for execution or account access, remind the user that code generation is handled here and live execution belongs to Trading MCP.
