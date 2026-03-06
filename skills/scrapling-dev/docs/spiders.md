# Scrapling Spiders Reference

This document details Scrapling's concurrent, Scrapy-inspired asynchronous crawling framework. It unifies fetchers and parsing into a system capable of managing multiple sessions, schedules, rate limits, and checkpointing.

---

## 1. Spider Basics

A spider is a subclass of `scrapling.spiders.Spider`. It requires a `name`, `start_urls`, and a `parse` async generator method.

```python
from scrapling.spiders import Spider, Response

class MySpider(Spider):
    name = "example_spider"
    start_urls = ["https://quotes.toscrape.com"]
    
    # Must be an async generator
    async def parse(self, response: Response):
        for quote in response.css("div.quote"):
            # Yield items (dicts)
            yield {
                "text": quote.css("span.text::text").get(""),
                "author": quote.css("small.author::text").get(""),
            }
            
        # Yield follow-up requests
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

# Run the spider
result = MySpider().start()

# Export scraped
result.items.to_json("output.json", indent=True)
result.items.to_jsonl("output.jsonl")
```

### CrawlResult and Stats

The `start()` method returns a `CrawlResult` containing `.items` (an `ItemList`) and `.stats` (a `CrawlStats` object).

```python
stats = result.stats
print(f"Scraped: {stats.items_scraped}")
print(f"Requests: {stats.requests_count}") 
print(f"Errors/Blocked: {stats.failed_requests_count} / {stats.blocked_requests_count}")
print(f"Elapsed: {stats.elapsed_seconds:.1f}s")
```

---

## 2. Following Links and the `Request` Object

`response.follow()` is the preferred way to create follow-up requests inside callbacks. It handles relative URLs and inherits the current session, proxy, and headers.

```python
from scrapling.spiders import Request

async def parse(self, response: Response):
    # Relative URLs automatically resolved
    yield response.follow("/next", callback=self.parse, priority=10)
    
    # Pass metadata to the next callback
    yield response.follow(
        "/item/123", 
        callback=self.parse_item,
        meta={"source_category": "electronics"}
    )
    
    # Or create a Request manually (e.g., POSTing data)
    yield Request(
        "https://api.example.com",
        method="POST",
        data={"key": "value"},
        callback=self.parse_api
    )
    
async def parse_item(self, response: Response):
    # Retrieve metadata passed
    category = response.meta.get("source_category")
```

### Request Deduplication
To allow revisiting a URL (e.g., pagination loops or reloading after an action), pass `dont_filter=True` to the request.

---

## 3. Multi-Session Management

Spiders can manage multiple concurrent network sessions (e.g., mixing HTTP for listings and Browser for protected details).
By default, spiders create one `FetcherSession`. Override `configure_sessions` to customize.

```python
from scrapling.spiders import Spider, SessionManager
from scrapling.fetchers import FetcherSession, AsyncStealthySession

class MultiToolSpider(Spider):
    name = "mixed"
    start_urls = ["https://listing.com"]
    
    def configure_sessions(self, manager: SessionManager):
        # Default session for fast HTTP requests
        manager.add("http", FetcherSession())
        
        # Browser session for js-heavy pages (started lazily)
        manager.add("browser", AsyncStealthySession(headless=True), lazy=True)

    async def parse(self, response: Response):
        # Route specific URLs to the stealth browser via `sid`
        for link in response.css('.protected-link::attr(href)').getall():
            yield response.follow(link, sid="browser", callback=self.parse_detail)
```

**Note**: Inside Spiders, sessions must use their asynchronous counterparts (if they take time to spin up like StealthyFetcher). When declaring them in the manager, `AsyncDynamicSession` or `AsyncStealthySession` must be used.

---

## 4. Proxies, Retries, and Handling Blocks

The spider integrates `ProxyRotator` seamlessly. If a proxy gets blocked, the spider catches it and retries with a fresh proxy.

```python
from scrapling.fetchers import FetcherSession, ProxyRotator

class ProxySpider(Spider):
    name = "proxied"
    # Retry a blocked request up to 5 times
    max_blocked_retries = 5 
    
    def configure_sessions(self, manager):
        rotator = ProxyRotator([
            "http://proxy1:8080",
            "http://proxy2:8080"
        ])
        manager.add("default", FetcherSession(proxy_rotator=rotator))
        
    async def is_blocked(self, response: Response) -> bool:
        # Override to detect blocks beyond standard HTTP statuses (403, 429)
        if "captcha" in response.body.decode("utf-8").lower():
            return True
        return False
        
    async def retry_blocked_request(self, request: Request, response: Response) -> Request:
        # Optional: Switch sessions entirely on a block
        # request.sid = "backup_stealth_browser"
        return request
```

*(Note: Provide custom proxy strategies via `ProxyRotator(..., strategy=fn)` if cyclical rotation isn't desired).*

---

## 5. Advanced Features

### Concurrency and Rate Limiting
Control politeness using class attributes:
```python
class PoliteSpider(Spider):
    concurrent_requests = 8           # Global max in-flight requests
    concurrent_requests_per_domain = 2 # Max per specific domain
    download_delay = 1.0              # 1 second fixed delay between requests
```

### Pause, Resume, and Checkpointing
By specifying a `crawldir`, the spider enables checkpointing. If interrupted with `Ctrl+C`, it saves its state. Rerunning with the same directory resumes instantly.
```python
# Pass interval to save state every 60 seconds
spider = MySpider(crawldir="./spider_state", interval=60.0)
result = spider.start()

if result.paused:
    print("Paused successfully!")
```

### Streaming API
For real-time UI integration or continuous operation, use `stream()` instead of `start()`.
```python
import anyio

async def run():
    spider = MySpider()
    async for item in spider.stream():
        print("Live item scraped:", item)

anyio.run(run)
```

### Lifecycle Hooks
Override these methods for setup, teardown, or custom behaviors:
- `on_start(self, resuming: bool)`
- `on_close(self)`
- `on_error(self, request, error)`
- `on_scraped_item(self, item) -> dict | None` (Return `None` to drop the item silently)
- `start_requests(self)` (Yield initial Requests manually instead of `start_urls`)
