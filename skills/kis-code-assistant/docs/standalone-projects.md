# Standalone Projects

Load this document when the user is not already using the upstream `open-trading-api` sample layout.

## Problem

The official KIS examples often assume:

- `kis_auth.py` is present
- the file lives in a sample-project structure
- `sys.path` can be extended to reach shared helpers

This skill does not bundle `kis_auth.py`.

## Default Standalone Strategy

If the user wants code for a standalone project:

1. state clearly whether the generated code depends on `kis_auth.py`
2. prefer one of these two paths

### Path A: Official Helper Compatibility

Use this when the user wants the closest match to official examples.

Tell the user to fetch these upstream files into their project:

- `examples_llm/kis_auth.py`
- the relevant example API file
- any related check file only if they want a test harness

Then generate code in the official style.

### Path B: Minimal Standalone Skeleton

Use this when the user wants an architecture sketch or a cleaner standalone layout.

In that case:

- keep the official function name and request parameters
- explain that auth/session bootstrap must be implemented separately
- replace direct `kis_auth.py` reliance with a short placeholder note when necessary

Minimal auth bootstrap pattern:

```python
import json
import os
import requests

BASE_URL = os.environ["KIS_BASE_URL"]
APP_KEY = os.environ["KIS_APP_KEY"]
APP_SECRET = os.environ["KIS_APP_SECRET"]

def issue_access_token():
    response = requests.post(
        f"{BASE_URL}/oauth2/tokenP",
        headers={"content-type": "application/json"},
        data=json.dumps(
            {
                "grant_type": "client_credentials",
                "appkey": APP_KEY,
                "appsecret": APP_SECRET,
            }
        ),
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["access_token"]
```

Use this only as a bootstrap example. Keep the selected KIS function name, request fields, and endpoint-specific parameters aligned with the official example source.

## Answering Rule

Never present repo-dependent code as fully standalone unless all required helper dependencies are included in the answer.
