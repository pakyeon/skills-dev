# Code Generation

Use this document after API discovery and source-code retrieval.

## Two Entry Paths

### Easy Path

Use when the user gives a natural-language task such as:

- “I want to check Samsung Electronics price”
- “Show me how to query my overseas stock balance”

Workflow:

1. infer category
2. search API index
3. fetch source code
4. generate Python code

### Detailed Path

Use when the user already provides:

- stock code
- task
- target category

Workflow:

1. search the chosen category
2. fetch source code for the selected API
3. generate complete Python code with the identified function

## KIS Python Conventions To Preserve

- import and reuse `kis_auth.py` as `import kis_auth as ka`
- use `ka.auth(svr="vps", product="01")` for paper trading examples
- leave the production auth variant commented when appropriate
- call `ka.smart_sleep()` before API calls when sample patterns require rate control
- note the WebSocket registration limit of 41 subscriptions per app key
- include basic logging and error handling
- keep the code runnable as a standalone Python script

## Project Layout Modes

### Repo-Compatible Mode

Use this when the user already works inside the upstream `open-trading-api` layout or a copied sample layout.

In this mode it is correct to:

- import `kis_auth.py`
- extend `sys.path`
- preserve the official KIS sample structure

### Standalone Project Mode

Use this when the user is outside the upstream sample layout.

In this mode:

- tell the user that `kis_auth.py` is not bundled with this skill
- load [`standalone-projects.md`](standalone-projects.md)
- either instruct the user to fetch the official `kis_auth.py` from upstream or generate code with an explicit dependency note
- do not pretend the snippet is fully self-contained if it still depends on `kis_auth.py`

If the user explicitly wants a minimal standalone pattern, provide:

- direct `requests` usage for auth bootstrap
- a local config object or environment-variable placeholders
- the verified API function name and parameter names from the official example
- a note that request signing/session helpers may still need to be aligned with upstream KIS conventions

## Default Output Shape

Prefer this structure unless the fetched example strongly suggests otherwise:

```python
import json
import logging
import sys

sys.path.extend(["..", "."])

import kis_auth as ka

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
```

Then:

- initialize auth
- apply rate control if needed
- call the selected KIS function with verified parameters
- print JSON output when possible

## Safety Rules

- Do not invent function names if the example code is available.
- Do not invent request parameters when the fetched example code or API metadata can confirm them.
- If Trading MCP is unavailable, do not claim that code has been executed against a live or paper account.
- If the generated code depends on upstream helper files, state that dependency explicitly.

## When To Mention Trading MCP

Mention `Kis Trading MCP` only if the user needs:

- live execution
- real account or paper account access
- runtime quote retrieval instead of sample code
- direct order flow
