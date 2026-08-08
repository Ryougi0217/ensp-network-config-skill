#!/usr/bin/env python3
"""Evaluate an eNSP stage gate from explicit attestation or assertion JSON."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


AMBIGUOUS_RE = re.compile(r"好像|应该|差不多|可能|似乎|大概|基本上")
FAIL_RE = re.compile(r"未通过|不通过|验证失败|测试失败|不能通信|无法通信|ping不通|不通|报错|有问题", re.IGNORECASE)
PASS_RE = re.compile(r"本阶段(?:验证|测试)?通过|验证通过|测试通过|自行验证通过|确认通过|可以进入下一(?:步|阶段)", re.IGNORECASE)


def result_template(evidence_type: str) -> dict[str, Any]:
    return {
        "gate": "uncertain",
        "evidence_type": evidence_type,
        "passed_assertions": [],
        "failed_assertions": [],
        "missing_assertions": [],
        "next_action": "request_clearer_evidence",
    }


def evaluate_attestation(text: str) -> dict[str, Any]:
    result = result_template("user_attestation")
    normalized = re.sub(r"\s+", "", text.strip())
    if not normalized or AMBIGUOUS_RE.search(normalized):
        return result
    failed = bool(FAIL_RE.search(normalized))
    passed = bool(PASS_RE.search(normalized))
    if failed and passed:
        result["next_action"] = "resolve_conflicting_attestation"
    elif failed:
        result["gate"] = "failed"
        result["next_action"] = "notify_user_choose_repair_or_force"
    elif passed:
        result["gate"] = "passed"
        result["next_action"] = "advance_to_next_stage"
    return result


def evaluate_assertions(data: dict[str, Any]) -> dict[str, Any]:
    result = result_template("runtime_evidence")
    assertions = data.get("assertions")
    if not isinstance(assertions, list) or not assertions:
        result["missing_assertions"].append("all_required_assertions")
        return result

    for index, assertion in enumerate(assertions, start=1):
        if not isinstance(assertion, dict):
            result["missing_assertions"].append(f"assertion-{index}")
            continue
        assertion_id = str(assertion.get("id") or f"assertion-{index}")
        if assertion.get("required", True) is False:
            continue
        state = str(assertion.get("state") or "unknown").lower()
        if state == "passed":
            result["passed_assertions"].append(assertion_id)
        elif state == "failed":
            result["failed_assertions"].append(assertion_id)
        else:
            result["missing_assertions"].append(assertion_id)

    if result["failed_assertions"]:
        result["gate"] = "failed"
        result["next_action"] = "notify_user_choose_repair_or_force"
    elif result["missing_assertions"]:
        result["gate"] = "uncertain"
        result["next_action"] = "request_missing_evidence"
    else:
        result["gate"] = "passed"
        result["next_action"] = "advance_to_next_stage"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    attestation = sub.add_parser("attestation")
    attestation.add_argument("text")
    evidence = sub.add_parser("evidence")
    evidence.add_argument("json_file", type=Path)
    args = parser.parse_args()

    if args.command == "attestation":
        result = evaluate_attestation(args.text)
    else:
        try:
            data = json.loads(args.json_file.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            raise SystemExit(f"无法读取证据JSON: {exc}") from exc
        result = evaluate_assertions(data)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["gate"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
