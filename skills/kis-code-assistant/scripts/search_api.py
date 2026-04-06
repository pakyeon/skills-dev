#!/usr/bin/env python3
import argparse
import csv
import json
from pathlib import Path


EXACT_MATCH_FIELDS = {"category", "subcategory"}
MAX_RESULTS = 10
DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "data.csv"
BROAD_QUERY_FIELDS = ("api_name", "function_name", "description", "args", "example")
RESPONSE_FIELDS = ("returns", "column_mapping", "description", "example")


def load_rows():
    with DATA_PATH.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader), reader.fieldnames or []


def search(**kwargs):
    rows, columns = load_rows()
    if not rows:
        return {
            "status": "error",
            "message": "Data not loaded",
            "total_count": 0,
            "results": [],
        }

    valid_kwargs = {
        key: value
        for key, value in kwargs.items()
        if value is not None and key in columns
    }

    query_value = kwargs.get("query")
    response_value = kwargs.get("response")

    if not valid_kwargs and query_value is None and response_value is None:
        return {
            "status": "error",
            "message": "No valid search parameters",
            "total_count": 0,
            "results": [],
        }

    filtered = rows
    for key, value in valid_kwargs.items():
        needle = str(value)
        if key in EXACT_MATCH_FIELDS:
            filtered = [row for row in filtered if row.get(key) == needle]
        else:
            filtered = [
                row for row in filtered
                if needle.lower() in str(row.get(key, "")).lower()
            ]

    if query_value is not None:
        needle = str(query_value).lower()
        filtered = [
            row for row in filtered
            if any(needle in str(row.get(field, "")).lower() for field in BROAD_QUERY_FIELDS)
        ]

    if response_value is not None:
        needle = str(response_value).lower()
        filtered = [
            row for row in filtered
            if any(needle in str(row.get(field, "")).lower() for field in RESPONSE_FIELDS)
        ]

    if not filtered:
        return {
            "status": "no_results",
            "message": f"No APIs found with conditions: {valid_kwargs}",
            "total_count": 0,
            "results": [],
        }

    if len(valid_kwargs) == 1 and ("category" in valid_kwargs or "subcategory" in valid_kwargs):
        seen = set()
        results = []
        for row in filtered:
            api_name = row.get("api_name")
            if api_name in seen:
                continue
            seen.add(api_name)
            results.append(
                {
                    "function_name": row.get("function_name", ""),
                    "api_name": api_name,
                    "category": row.get("category", ""),
                    "subcategory": row.get("subcategory", ""),
                }
            )
        return {
            "status": "success",
            "message": f"Found {len(filtered)} APIs ({len(results)} unique)",
            "total_count": len(filtered),
            "results": results,
        }

    results = []
    for row in filtered[:MAX_RESULTS]:
        results.append(
            {
                "function_name": row.get("function_name", ""),
                "api_name": row.get("api_name", ""),
                "category": row.get("category", ""),
                "subcategory": row.get("subcategory", ""),
                "description": row.get("description", ""),
                "args": row.get("args", ""),
                "returns": row.get("returns", ""),
                "example": row.get("example", ""),
                "column_mapping": row.get("column_mapping", ""),
                "url_main": row.get("url_main", ""),
                "url_chk": row.get("url_chk", ""),
            }
        )

    message = f"Found {len(filtered)} APIs"
    if len(filtered) > MAX_RESULTS:
        message += f" (showing first {MAX_RESULTS})"

    return {
        "status": "success",
        "message": message,
        "total_count": len(filtered),
        "results": results,
    }


def main():
    parser = argparse.ArgumentParser(description="Search the bundled KIS API index.")
    parser.add_argument("--category")
    parser.add_argument("--subcategory")
    parser.add_argument("--api-name", dest="api_name")
    parser.add_argument("--function-name", dest="function_name")
    parser.add_argument("--description")
    parser.add_argument("--response")
    parser.add_argument("--query")
    args = parser.parse_args()

    result = search(
        category=args.category,
        subcategory=args.subcategory,
        api_name=args.api_name,
        function_name=args.function_name,
        description=args.description,
        response=args.response,
        query=args.query,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
