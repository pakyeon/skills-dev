#!/usr/bin/env python3
import argparse
import json
import re
import time
import urllib.request


MAIN_TEMPLATE = "https://raw.githubusercontent.com/koreainvestment/open-trading-api/main/examples_llm/{category}/{function_name}/{function_name}.py"
CHK_TEMPLATE = "https://raw.githubusercontent.com/koreainvestment/open-trading-api/main/examples_llm/{category}/{function_name}/chk_{function_name}.py"


def extract_category_function_from_url(github_url):
    pattern = r"examples_llm/([^/]+)/([^/]+)/(?:chk_)?([^/]+)\.py"
    match = re.search(pattern, github_url or "")
    if not match:
        return None
    return {"category": match.group(1), "function_name": match.group(2)}


def fetch_text(url):
    time.sleep(0.1)
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return True, response.read().decode("utf-8")
    except Exception as exc:
        return False, f"❌ GitHub file read failed: {exc}"


def github_to_raw_url(url):
    if not url:
        return None
    if "raw.githubusercontent.com" in url:
        return url
    converted = url.replace("://github.com/", "://raw.githubusercontent.com/")
    converted = converted.replace("/blob/", "/")
    converted = converted.replace("/tree/", "/")
    return converted


def build_result(url, mode):
    params = extract_category_function_from_url(url)
    if not params:
        return {
            "status": "error",
            "message": "Invalid GitHub URL format",
            "content": "",
            "url": url,
        }

    raw_url = github_to_raw_url(url)
    if not raw_url:
        template = MAIN_TEMPLATE if mode == "main" else CHK_TEMPLATE
        raw_url = template.format(**params)
    ok, content = fetch_text(raw_url)
    status = "success" if ok else "error"
    message = "Fetched source code successfully" if ok else content
    git_uri_prefix = "internal://kis-api/" if mode == "main" else "internal://kis-api-chk/"
    return {
        "status": status,
        "message": message,
        "content": content,
        "url": url,
        "raw_url": raw_url,
        "git_uri": f"{git_uri_prefix}{params['category']}/{params['function_name']}",
    }


def read_source_code(url_main=None, url_chk=None):
    results = {}
    if url_main:
        results["main"] = build_result(url_main, "main")
    if url_chk:
        results["check"] = build_result(url_chk, "check")

    if not results:
        return {
            "status": "error",
            "message": "No URL was provided",
            "results": {},
        }

    success_count = sum(1 for item in results.values() if item["status"] == "success")
    total_count = len(results)
    if success_count == total_count:
        status = "success"
        message = f"Fetched all code successfully ({success_count}/{total_count})"
    elif success_count > 0:
        status = "partial_success"
        message = f"Fetched some code successfully ({success_count}/{total_count})"
    else:
        status = "error"
        message = f"Failed to fetch all code (0/{total_count})"

    return {
        "status": status,
        "message": message,
        "results": results,
    }


def main():
    parser = argparse.ArgumentParser(description="Fetch KIS example source code from GitHub URLs.")
    parser.add_argument("--url-main", dest="url_main")
    parser.add_argument("--url-chk", dest="url_chk")
    args = parser.parse_args()
    print(json.dumps(read_source_code(args.url_main, args.url_chk), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
