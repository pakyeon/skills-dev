# Scrapling Parsing Engine Reference

This document details Scrapling’s HTML parsing engine, including the `Selector` class, selection methods, tree traversal, TextHandlers, and auto-adaptive element matching.

---

## 1. The Selector Object

Any HTML passed to Scrapling (via `url`, `bytes`, or `str`) results in a `Selector` object. This is the core object across the framework. Fetcher methods (`.get()`, `.post()`) return `Response` objects, which inherit from `Selector`.

### Basic Properties

```python
from scrapling import Selector

page = Selector('<html>...</html>', url="https://example.com")

# Get the tag name of the root/current element
tag = page.tag # "html"

# Get a dictionary of all attributes
attrs = page.attrib # {'id': 'main', 'class': 'container'}

# Access specific attributes like a dictionary
class_name = page.attrib.get('class')
id_val = page['id'] # Shorthand in v0.3+

# Retrieve raw content
html_string = page.html_content # '<div class="container">...</div>'
bytes_content = page.body # raw bytes from fetchers

# Prettify HTML output
pretty_html = page.prettify()

# Get all nested text content combined
all_text = page.get_all_text(separator=' ', strip=True, ignore_tags=('script', 'style'))
```

---

## 2. Querying Elements

Scrapling offers unified searching via CSS, XPath, regular expressions, and literal text. Methods return either a `Selector` (single element) or a `Selectors` list (multiple elements).

### Data Extraction (`get()`, `getall()`)

*Starting from v0.4, all selection methods return `Selector(s)` - even for text nodes and attribute values.* Use `get()` (or `extract_first`) to get the first match as a string, and `getall()` (or `extract`) for all matches as a list. Text/attr selections return the exact text content; Element selections return the *outer HTML*.

```python
# CSS & XPath Element Selection
items = page.css('.item') # Returns a Selectors list
first_item = page.xpath('//div[@class="item"]')[0]

# Extracting Text / Attributes
title = page.css('h1::text').get(default="No Title")
links = page.xpath('//a/@href').getall()

# Extracting Outer HTML
outer = page.css('h1').get() # '<h1>Title</h1>'
```

### Advanced Selection Methods

- `find_all` / `find`: Similar to BeautifulSoup. Accepts a single filter function.
```python
# Find elements that have an attribute starting with "data-"
elements = page.find_all(lambda e: any(attr.startswith("data-") for attr in e.attrib))
sidebar = page.find(lambda e: e.has_class('sidebar'))
```

- `find_by_text` / `find_by_regex`: Finds elements based on their immediate text content, handling edge cases effectively.
```python
# Returns the matching element itself (not just the text string)
btn = page.find_by_text("Submit", exact=True, case_sensitive=False)
prices = page.find_by_regex(r'\$\d+\.\d{2}', exact=False)
```

- `has_class`: Fast utility.
```python
if button.has_class('btn-primary'): pass
```

---

## 3. DOM Traversal

Navigate up, down, or sideways from any parsed `Selector`.

```python
element = page.css('.product')[0]

# Parents and Ancestors
parent = element.parent
all_ancestors = element.path # List of parent nodes from the root down to the element
top_div = element.find_ancestor(lambda e: e.tag == 'div' and e.has_class('container'))

for anc in element.iterancestors():
    pass

# Children and Descendants
children = element.children # Direct children only
descendants = element.below_elements # All elements underneath (nested tree)

# Siblings
siblings = element.siblings
next_elem = element.next 
prev_elem = element.previous # None if it's the first child
```

---

## 4. `Selectors` List Operations

The `Selectors` class extends standard Python lists with utility methods for bulk operations.

```python
elements = page.css('.product')

# Chaining queries
links = elements.css('a::attr(href)')

# Filtering
over_50 = elements.filter(lambda p: float(p.css('.price').re_first(r'\d+')) > 50)
first_match = elements.search(lambda p: "discount" in p.get_all_text())

# Quality of Life
first_elem = elements.first # None instead of IndexError
last_elem = elements.last
size = elements.length # Same as len()
```

---

## 5. TextHandler and Regex Extraction

All string outputs (from `get()`, text methods) in Scrapling return a `TextHandler` (a subclass of `str`). It adds convenient text-processing utilities that can be chained.

```python
from scrapling import TextHandler

# Extract using Regex (re returns list, re_first returns string)
# Very useful when matched directly against element selections
prices_list = page.css('.product').re(r'\$\d+\.\d{2}') 
first_price = page.css('.price').re_first(r'\d+\.\d{2}')

# Parse JSON strings seamlessly
script_json = page.css('script#data::text').get().json()

# Clean up whitespace formatting
clean_text = page.css('.messy::text').get().clean() # Removes \n, \r, multi-spaces
```

---

## 6. Adaptive Scraping (Resilience to DOM Changes)

The Adaptive feature makes scrapers survive website design changes by creating a unique digital footprint for an element, saving it locally, and relocating it later if the original CSS/XPath fails.

### Using Auto-save (Recommended)

Requires passing `adaptive=True` to the `Selector` and using the `auto_save` argument in `css`/`xpath`.

```python
# 1. First Run (Original code):
page = Selector(html, url="https://example.com/item123", adaptive=True)

# Using auto_save calculates a unique profile for this element "title" and saves it to disk (default JSON).
title = page.css('h1.product-main-title', auto_save="title")[0]

# 2. Sometime later (Website structure changed):
# h1.product-main-title no longer exists.
# Behind the scenes, Scrapling reads the saved footprint for "title", scans the DOM, 
# and returns the new location of the element (e.g. h2.title-text).
title = page.css('h1.product-main-title', auto_save="title")[0]
```

### Required Configuration Fields
When using `adaptive=True`:
- `url` must be provided (limits footprints to a specific domain).
- **Matching is slow**: The rescue phase computes similarities across the entire page.

### Manual Relocation (`save`/`retrieve`/`relocate`/`find_similar`)

If you want fine-grained control or prefer keeping adaptive configs in your database rather than local files:

```python
# 1. Saving manually
element = page.css('h1')[0]
profile = element.save() # dict containing visual/textual features
# DB.insert(profile)

# 2. Relocating manually later
# profile = DB.get()
element_features = page.retrieve(profile) 
found_element = page.relocate(element_features)[0]

# Or simply finding visually/structurally similar elements on the page
similar_elements = current_element.find_similar()
```
