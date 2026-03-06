---
name: scrapling-dev
description: How to scrape websites and build crawlers using the Scrapling framework. Make sure to use this skill whenever the user asks to scrape a website, extract data from a URL, build a spider/crawler, bypass Cloudflare/anti-bot systems, or automate web browsers using Scrapling in Python.
---

# Scrapling Skill

Scrapling is an undetected, fast, and lightweight web scraping Python library that unifies HTTP requests, browser automation, anti-bot bypassing, and HTML parsing under a single intuitive API. 

This document serves as the **entry point**. For comprehensive API details, you **MUST** refer to the sub-documents in the `docs/` directory:

- 📄 **[`docs/fetchers.md`](docs/fetchers.md)**: Details on `Fetcher`, `DynamicFetcher`, `StealthyFetcher`, Sessions, and `ProxyRotator`.
- 📄 **[`docs/parsing.md`](docs/parsing.md)**: Details on CSS/XPath selection, `find_*` methods, `TextHandler` regex extraction, DOM traversal, and **Adaptive Scraping**.
- 📄 **[`docs/spiders.md`](docs/spiders.md)**: Details on the `Spider` class, multi-session management, Requests/Callbacks, pauses, limits, and the Streaming API.

---

## Which Tool Should I Use? (Decision Tree)

1. **Do I need to crawl multiple pages or follow links iteratively?**
   - **YES** ➡️ Read **[`docs/spiders.md`](docs/spiders.md)** and use `Spider`.
   - **NO** ➡️ Go to step 2.
2. **Does the website use advanced bot protection (e.g., Cloudflare, Kasada)?**
   - **YES** ➡️ Read **[`docs/fetchers.md`](docs/fetchers.md)** and use `StealthyFetcher`.
   - **NO** ➡️ Go to step 3.
3. **Does the website require JavaScript to load the content I need?**
   - **YES** ➡️ Read **[`docs/fetchers.md`](docs/fetchers.md)** and use `DynamicFetcher`.
   - **NO** (Static HTML) ➡️ Read **[`docs/fetchers.md`](docs/fetchers.md)** and use the extremely fast `Fetcher`.

---

## Quick-Start Examples

### 1. Basic Fetch & Parse (Static HTML)
*Use when speed is critical and no JS is needed.*

```python
from scrapling import Fetcher

# 1. Fetch the page (Returns a Response object, which inherits from Selector)
page = Fetcher.get("https://quotes.toscrape.com")

# 2. Parse using unified CSS/XPath (.get() for strings, .getall() for lists)
quotes = page.css('.quote')
for q in quotes:
    text = q.css('.text::text').get()
    author = q.xpath('.//small[@class="author"]/text()').get()
    print(f"{author}: {text}")
```
*📖 Read **[`docs/parsing.md`](docs/parsing.md)** for advanced selection (`find_by_text`, `find_similar`, `re`).*

---

### 2. Bypassing Cloudflare
*Use when encountering 403 Forbidden or CAPTCHA challenges.*

```python
from scrapling import StealthyFetcher

# 1. Automatically solve Cloudflare challenges
page = StealthyFetcher.get(
    "https://protected-site.com", 
    solve_cloudflare=True,
    headless=True,
    network_idle=True 
)

title = page.css('title::text').get()
print(title)
```
*📖 Read **[`docs/fetchers.md`](docs/fetchers.md)** for `page_action` (Playwright automation) and Sessions.*

---

### 3. Spidering / Crawling
*Use for large-scale scraping or pagination.*

```python
from scrapling.spiders import Spider, Response

class SimpleSpider(Spider):
    name = "simple"
    start_urls = ["https://quotes.toscrape.com"]
    concurrent_requests = 4

    async def parse(self, response: Response):
        # Extract items
        for quote in response.css('div.quote'):
            yield {
                "text": quote.css('span.text::text').get(),
                "author": quote.css('small.author::text').get()
            }

        # Follow pagination linking to the same callback
        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

# Run and export
result = SimpleSpider().start()
result.items.to_json("output.json", indent=True)
print(f"Scraped {result.stats.items_scraped} items in {result.stats.elapsed_seconds:.1f}s")
```
*📖 Read **[`docs/spiders.md`](docs/spiders.md)** for Multi-Sessions, Proxy Rotation, and Checkpointing.*
