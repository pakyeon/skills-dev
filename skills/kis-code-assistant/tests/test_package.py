#!/usr/bin/env python3
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch


SKILL_DIR = Path(__file__).resolve().parents[1]
SEARCH_SCRIPT = SKILL_DIR / "scripts" / "search_api.py"
SOURCE_SCRIPT = SKILL_DIR / "scripts" / "read_source_code.py"


def run_json(cmd):
    result = subprocess.run(cmd, cwd=SKILL_DIR, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    search_result = run_json([sys.executable, str(SEARCH_SCRIPT), "--query", "삼성전자"])
    assert search_result["status"] == "success", search_result
    assert search_result["total_count"] > 0, search_result

    response_result = run_json([sys.executable, str(SEARCH_SCRIPT), "--category", "domestic_stock", "--response", "PER"])
    assert response_result["status"] == "success", response_result
    assert response_result["total_count"] > 0, response_result

    source_module = load_module(SOURCE_SCRIPT, "kis_skill_read_source_code_package")
    valid_main = "https://github.com/koreainvestment/open-trading-api/tree/main/examples_llm/auth/auth_token/auth_token.py"
    with patch("urllib.request.urlopen", side_effect=RuntimeError("boom")):
        result = source_module.read_source_code(url_main=valid_main)
    assert result["status"] == "error", result
    assert result["results"]["main"]["status"] == "error", result

    skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert "docs/standalone-projects.md" in skill_text

    standalone_text = (SKILL_DIR / "docs" / "standalone-projects.md").read_text(encoding="utf-8")
    assert "issue_access_token" in standalone_text
    assert "KIS_APP_KEY" in standalone_text

    print("Standalone package checks passed.")


if __name__ == "__main__":
    main()
