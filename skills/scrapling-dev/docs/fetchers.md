# Scrapling Fetchers Reference

This document covers all of Scrapling's Fetchers (`Fetcher`, `DynamicFetcher`, `StealthyFetcher`), Session Management, and Proxy Rotation.

---

## 1. Static Fetching (`Fetcher` & `AsyncFetcher`)

Best for fast, lightweight HTTP requests where JavaScript execution is not needed.

### Basic Usage

```python
from scrapling import Fetcher, AsyncFetcher

url = "https://example.com"
# Synchronous
page = Fetcher.get(url) 

# Asynchronous
page = await AsyncFetcher.get(url)
```

Both `Fetcher` and `AsyncFetcher` support standard HTTP methods: `.get()`, `.post()`, `.put()`, `.delete()`.
All methods return a Scrapling `Response` object (which is essentially a `Selector` with extra network properties like `.status`, `.url`, `.headers`, etc.).

### Shared Arguments (Apply to all Fetchers)

All fetcher methods (and sessions) accept these key arguments:
- `headers` (dict): Custom HTTP headers.
- `cookies` (dict): Cookies to include.
- `proxy` (str): Single proxy URL (e.g., `http://user:pass@1.2.3.4:8080`).
- `timeout` (float): Request timeout in seconds (default: 10.0 for static, 30.0 for browser).
- `retries` (int): Number of retries on failure (default: 0).
- `verify` (bool): Verify SSL certificates (default: True).
- `data` / `json`: For POST/PUT requests.
- `stealthy_headers` (bool): Auto-generate browser-like headers. Default True.
- `impersonate` (str): Impersonate a specific browser's TLS signature (e.g., `'chrome'`, `'firefox'`, `'safari'`).

### FetcherSession & AsyncFetcherSession

Sessions persist cookies and headers across multiple requests, improving performance by reusing connections.

```python
from scrapling import FetcherSession

# Using a context manager ensures proper cleanup
with FetcherSession(impersonate='chrome') as session:
    # 1. Login
    res1 = session.post("https://site.com/login", data={"user": "...", "pass": "..."})
    
    # 2. Cookies are remembered automatically
    res2 = session.get("https://site.com/dashboard")
```

For async:
```python
from scrapling import AsyncFetcherSession

async with AsyncFetcherSession() as session:
    res = await session.get("https://example.com")
```

---

## 2. Dynamic Fetching (`DynamicFetcher` & `AsyncDynamicSession`)

Best for websites rendering content using JavaScript via browser automation (Playwright underneath). 

### Basic Usage

```python
from scrapling import DynamicFetcher

# Automatically launches browser, fetches page, and closes browser
page = DynamicFetcher.get("https://example.com")
```

### Advanced Arguments

- `headless` (bool): Run without GUI (default: True). Enabling GUI helps debugging.
- `disable_resources` (bool): Blocks images/fonts/media for speed (default: False).
- `wait_selector` (str): Wait for a specific CSS element before returning.
- `network_idle` (bool): Wait until network traffic stops (useful for SPAs).
- `timeout` (float): Max wait time in milliseconds.

```python
page = DynamicFetcher.get(
    "https://example.com",
    wait_selector=".loaded-content",
    network_idle=True,
    disable_resources=True
)
```

### Page Actions (Executing Playwright commands)

You can pass a function to `page_action` to interact with the Playwright `Page` object before Scrapling parses the HTML.

```python
from playwright.sync_api import Page

def login_action(page: Page):
    page.locator("#username").fill("admin")
    page.locator("#password").fill("password123")
    page.locator("#submit").click()
    page.wait_for_selector(".dashboard")

response = DynamicFetcher.get("https://example.com/login", page_action=login_action)
```
*(Use `playwright.async_api.Page` for async actions with `AsyncDynamicSession`)*

### DynamicSession & AsyncDynamicSession

Like static sessions, dynamic sessions keep the browser alive, persisting cookies and local storage across requests.

```python
from scrapling import DynamicSession

with DynamicSession(headless=False) as session:
    res1 = session.get("https://example.com/page1")
    res2 = session.get("https://example.com/page2") # Same browser window
```

---

## 3. Stealthy Fetching (`StealthyFetcher` & `AsyncStealthySession`)

Best for bypassing severe anti-bot protections (Cloudflare Turnstile, Datadome, Kasada). Built on top of Playwright and advanced stealth plugins.

### Basic Usage

```python
from scrapling import StealthyFetcher

# Bypasses Cloudflare automatically
page = StealthyFetcher.get("https://protected-site.com", solve_cloudflare=True)
```

### Anti-Bot Arguments

- `solve_cloudflare` (bool): Special handling to bypass CF managed challenges.
- `block_webrtc` (bool): Prevents IP leaks via WebRTC.
- `hide_canvas` (bool): Mitigates canvas fingerprinting.
- `real_chrome` (bool): Uses actual Google Chrome instead of Chromium (requires Chrome installed).
- `google_search` (bool): Navigates via Google Search to provide an organic HTTP Referer.

```python
page = StealthyFetcher.get(
    "https://protected-site.com",
    solve_cloudflare=True,
    hide_canvas=True,
    real_chrome=True,
    google_search=True
)
```

*(Note: `StealthyFetcher` also supports `page_action`, `wait_selector`, and `network_idle` like `DynamicFetcher`.)*

### StealthySession & AsyncStealthySession

Keep the stealth browser alive:

```python
from scrapling import AsyncStealthySession

async with AsyncStealthySession(headless=False, block_webrtc=True) as session:
    res = await session.get("https://cloudflare-site.com", solve_cloudflare=True)
```

---

## 4. Proxy Rotation (`ProxyRotator`)

Automatically rotates proxies across requests in any Session. Integrates seamlessly with error handling and Scrapling Spiders.

### Basic Setup

```python
from scrapling import FetcherSession, ProxyRotator

rotator = ProxyRotator([
    "http://proxy1:8080",
    "http://user:pass@proxy2:8080"
])

# Pass the rotator to the session
with FetcherSession(proxy_rotator=rotator) as session:
    # Uses proxy1
    res1 = session.get("https://example.com/1")
    # Uses proxy2
    res2 = session.get("https://example.com/2")
    
    # Check which proxy was used
    print(res2.meta.get("proxy"))
```

For Browser Sessions (Playwright format):
```python
rotator = ProxyRotator([
    {"server": "http://proxy1:8080", "username": "usr", "password": "pwd"}
])
```

### Custom Rotation Strategies

By default, it cycles sequentially. You can provide a custom strategy (e.g., random).

```python
import random

def random_strategy(proxies: list, current_index: int):
    idx = random.randint(0, len(proxies) - 1)
    return proxies[idx], idx

rotator = ProxyRotator(["proxy1", "proxy2", "proxy3"], strategy=random_strategy)
```

### Per-Request Override

You can override the rotator for a specific request by passing `proxy=`:
```python
# Bypasses the rotator, uses specific proxy
res = session.get("https://example.com", proxy="http://special-proxy:8080")
```
