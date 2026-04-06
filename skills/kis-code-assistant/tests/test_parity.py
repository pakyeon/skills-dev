#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
SKILL_DIR = Path(__file__).resolve().parents[1]
MCP_DIR = REPO_ROOT / "open-trading-api" / "MCP" / "KIS Code Assistant MCP"
MCP_PYTHON = MCP_DIR / ".venv" / "bin" / "python"
SEARCH_SCRIPT = SKILL_DIR / "scripts" / "search_api.py"
SOURCE_SCRIPT = SKILL_DIR / "scripts" / "read_source_code.py"
ENTRY_SKILL = SKILL_DIR / "SKILL.md"


def run_json(cmd, cwd=None):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def run_mcp_search(**kwargs):
    code = """
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from src.utils.api_searcher import APISearcher

searcher = APISearcher("data.csv")
params = json.loads(sys.argv[1])
print(json.dumps(searcher.search(**params), ensure_ascii=False))
"""
    return run_json([str(MCP_PYTHON), "-c", code, json.dumps(kwargs, ensure_ascii=False)], cwd=MCP_DIR)


def run_skill_search(**kwargs):
    cmd = [sys.executable, str(SEARCH_SCRIPT)]
    for key, value in kwargs.items():
        if value is None:
            continue
        cmd.extend([f"--{key.replace('_', '-')}", str(value)])
    return run_json(cmd, cwd=SKILL_DIR)


def run_mcp_source(url_main=None, url_chk=None):
    code = """
import json, sys, importlib.util, time, urllib.request
from pathlib import Path

path = Path.cwd() / "server.py"
spec = importlib.util.spec_from_file_location("kis_code_assistant_server", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

def fetch_raw(url):
    time.sleep(0.1)
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return response.read().decode("utf-8")
    except Exception as exc:
        return f"❌ GitHub file read failed: {exc}"

args = json.loads(sys.argv[1])
results = {}
if args.get("url_main"):
    params = module.extract_category_function_from_url(args["url_main"])
    if params:
        results["main"] = {
            "status": "success",
            "message": "코드를 성공적으로 가져왔습니다",
            "content": fetch_raw(f"https://raw.githubusercontent.com/koreainvestment/open-trading-api/main/examples_llm/{params['category']}/{params['function_name']}/{params['function_name']}.py"),
            "url": args["url_main"],
            "git_uri": f"internal://kis-api/{params['category']}/{params['function_name']}",
        }
    else:
        results["main"] = {
            "status": "error",
            "message": "GitHub URL 형식이 올바르지 않습니다",
            "content": "",
            "url": args["url_main"],
        }
if args.get("url_chk"):
    params = module.extract_category_function_from_url(args["url_chk"])
    if params:
        results["check"] = {
            "status": "success",
            "message": "코드를 성공적으로 가져왔습니다",
            "content": fetch_raw(f"https://raw.githubusercontent.com/koreainvestment/open-trading-api/main/examples_llm/{params['category']}/{params['function_name']}/chk_{params['function_name']}.py"),
            "url": args["url_chk"],
            "git_uri": f"internal://kis-api-chk/{params['category']}/{params['function_name']}",
        }
    else:
        results["check"] = {
            "status": "error",
            "message": "GitHub URL 형식이 올바르지 않습니다",
            "content": "",
            "url": args["url_chk"],
        }

if not results:
    payload = {"status": "error", "message": "제공된 URL이 없습니다", "results": {}}
else:
    success_count = sum(1 for result in results.values() if result["status"] == "success")
    total_count = len(results)
    if success_count == total_count:
        status = "success"
    elif success_count > 0:
        status = "partial_success"
    else:
        status = "error"
    payload = {"status": status, "results": results}
print(json.dumps(payload, ensure_ascii=False))
"""
    args = {"url_main": url_main, "url_chk": url_chk}
    return run_json([str(MCP_PYTHON), "-c", code, json.dumps(args, ensure_ascii=False)], cwd=MCP_DIR)


def run_skill_source(url_main=None, url_chk=None):
    cmd = [sys.executable, str(SOURCE_SCRIPT)]
    if url_main:
        cmd.extend(["--url-main", url_main])
    if url_chk:
        cmd.extend(["--url-chk", url_chk])
    return run_json(cmd, cwd=SKILL_DIR)


def assert_search_parity(params):
    mcp = run_mcp_search(**params)
    skill = run_skill_search(**params)
    assert mcp["status"] == skill["status"], (mcp, skill)
    assert mcp["total_count"] == skill["total_count"], (mcp, skill)
    assert [item["function_name"] for item in mcp["results"]] == [item["function_name"] for item in skill["results"]], (mcp, skill)


def assert_source_parity(url_main=None, url_chk=None):
    mcp = run_mcp_source(url_main=url_main, url_chk=url_chk)
    skill = run_skill_source(url_main=url_main, url_chk=url_chk)
    assert mcp["status"] == skill["status"], (mcp, skill)
    assert set(mcp["results"].keys()) == set(skill["results"].keys()), (mcp, skill)
    for key in mcp["results"]:
        assert mcp["results"][key]["status"] == skill["results"][key]["status"], (mcp, skill)
        if mcp["results"][key]["status"] == "success":
            assert bool(mcp["results"][key]["content"]) == bool(skill["results"][key]["content"]), (mcp, skill)


def assert_navigation_docs():
    text = ENTRY_SKILL.read_text(encoding="utf-8")
    required_links = [
        "docs/overview.md",
        "docs/search-workflow.md",
        "docs/code-generation.md",
        "docs/standalone-projects.md",
        "docs/kis-trading-mcp-setup.md",
    ]
    for link in required_links:
        assert link in text, link


def assert_search_enrichment():
    result = run_skill_search(category="domestic_stock", api_name="주식현재가 시세")
    first = result["results"][0]
    for key in ["description", "args", "returns", "example", "column_mapping"]:
        assert key in first, key


def assert_query_and_response_fallbacks():
    query_result = run_skill_search(query="삼성전자")
    assert query_result["status"] == "success", query_result
    assert query_result["total_count"] > 0, query_result

    response_result = run_skill_search(category="domestic_stock", response="PER")
    assert response_result["status"] == "success", response_result
    assert response_result["total_count"] > 0, response_result


def assert_runtime_boundary_language():
    text = ENTRY_SKILL.read_text(encoding="utf-8")
    assert "generate code first" in text
    assert "actual runtime execution" in text


def assert_source_failure_is_error():
    import importlib.util
    from unittest.mock import patch

    script_path = SKILL_DIR / "scripts" / "read_source_code.py"
    spec = importlib.util.spec_from_file_location("kis_skill_read_source_code", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    valid_main = "https://github.com/koreainvestment/open-trading-api/tree/main/examples_llm/auth/auth_token/auth_token.py"
    with patch("urllib.request.urlopen", side_effect=RuntimeError("boom")):
        result = module.read_source_code(url_main=valid_main)
    assert result["status"] == "error", result
    assert result["results"]["main"]["status"] == "error", result


def assert_standalone_doc_has_bootstrap():
    doc = (SKILL_DIR / "docs" / "standalone-projects.md").read_text(encoding="utf-8")
    assert "issue_access_token" in doc
    assert "KIS_APP_KEY" in doc


def main():
    if not MCP_PYTHON.exists():
        raise SystemExit("Missing MCP virtualenv. Run `uv sync` in the original MCP directory first.")

    search_cases = [
        {"category": "auth", "function_name": "auth_token"},
        {"category": "domestic_stock", "api_name": "주식현재가 시세"},
        {"category": "domestic_stock", "subcategory": "실시간시세"},
        {"category": "overseas_stock", "function_name": "price"},
        {"category": "etfetn"},
        {"category": "domestic_bond", "description": "발행정보"},
    ]
    for case in search_cases:
        assert_search_parity(case)

    valid_main = "https://github.com/koreainvestment/open-trading-api/tree/main/examples_llm/auth/auth_token/auth_token.py"
    valid_chk = "https://github.com/koreainvestment/open-trading-api/tree/main/examples_llm/auth/auth_token/chk_auth_token.py"
    invalid = "https://github.com/koreainvestment/open-trading-api/tree/main/examples_llm/bad"
    assert_source_parity(url_main=valid_main)
    assert_source_parity(url_main=valid_main, url_chk=valid_chk)
    assert_source_parity(url_main=invalid)
    assert_navigation_docs()
    assert_search_enrichment()
    assert_query_and_response_fallbacks()
    assert_runtime_boundary_language()
    assert_source_failure_is_error()
    assert_standalone_doc_has_bootstrap()
    print("All parity checks passed.")


if __name__ == "__main__":
    main()
