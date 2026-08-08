#!/usr/bin/env python3
"""Validate the deterministic structure of an eNSP stage TXT script."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


STAGE_RE = re.compile(r"^=====\s*STAGE:\s*(.+?)\s*=====$")
CONFIG_RE = re.compile(r"^=====\s*CONFIG DEVICE:\s*([A-Za-z0-9_.-]+)\s*=====$")
VERIFY_RE = re.compile(r"^=====\s*VERIFY DEVICE:\s*([A-Za-z0-9_.-]+)\s*=====$")
ABBREVIATION_RE = re.compile(
    r"^(?:sy|sys|int|ip\s+ad|v\s+b|p\s+l|p\s+d\s+v|p\s+t\s+a|p\s+h\s+p|p\s+h\s+u)(?:\s|$)",
    re.IGNORECASE,
)


def parse_stage_text(text: str) -> dict[str, Any]:
    stage_headers: list[str] = []
    configs: list[dict[str, Any]] = []
    verifies: list[dict[str, Any]] = []
    preamble: list[str] = []
    current: dict[str, Any] | None = None
    seen_verify = False

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.rstrip()
        if match := STAGE_RE.match(line):
            stage_headers.append(match.group(1).strip())
            current = None
            continue
        if match := CONFIG_RE.match(line):
            current = {"device": match.group(1), "lines": [], "line_number": line_number}
            configs.append(current)
            if seen_verify:
                current["after_verify"] = True
            continue
        if match := VERIFY_RE.match(line):
            current = {"device": match.group(1), "lines": [], "line_number": line_number}
            verifies.append(current)
            seen_verify = True
            continue
        if current is None:
            if line.strip():
                preamble.append(line)
        else:
            current["lines"].append(line)

    return {"stage_headers": stage_headers, "configs": configs, "verifies": verifies, "preamble": preamble}


def nonempty_lines(block: dict[str, Any]) -> list[str]:
    return [line.strip() for line in block["lines"] if line.strip()]


def validate(path: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        return {"file": str(path), "valid": False, "errors": [str(exc)], "warnings": warnings}
    parsed = parse_stage_text(text)

    if len(parsed["stage_headers"]) != 1:
        errors.append(f"expected exactly one STAGE marker, found {len(parsed['stage_headers'])}")
    verification_only = bool(
        len(parsed["stage_headers"]) == 1
        and parsed["stage_headers"][0].split("|", 1)[0].strip().startswith("98-")
    )
    if not parsed["configs"] and not verification_only:
        errors.append("no CONFIG DEVICE blocks found")
    if not parsed["verifies"]:
        errors.append("no VERIFY DEVICE blocks found")

    config_devices = [block["device"] for block in parsed["configs"]]
    verify_devices = [block["device"] for block in parsed["verifies"]]
    duplicate_configs = sorted({device for device in config_devices if config_devices.count(device) > 1})
    duplicate_verifies = sorted({device for device in verify_devices if verify_devices.count(device) > 1})
    if duplicate_configs:
        errors.append(f"duplicate CONFIG DEVICE blocks: {duplicate_configs}")
    if duplicate_verifies:
        errors.append(f"duplicate VERIFY DEVICE blocks: {duplicate_verifies}")

    for block in parsed["configs"]:
        lines = nonempty_lines(block)
        device = block["device"]
        if block.get("after_verify"):
            errors.append(f"CONFIG DEVICE {device} appears after a VERIFY block")
        if not lines:
            errors.append(f"CONFIG DEVICE {device} is empty")
            continue
        if lines[0].lower() != "system-view":
            warnings.append(f"CONFIG DEVICE {device} does not start with full command 'system-view'")
        for line in lines:
            if re.fullmatch(r"save(?:\s+.*)?", line, re.IGNORECASE):
                errors.append(f"CONFIG DEVICE {device} contains forbidden save command")
            if ABBREVIATION_RE.match(line):
                warnings.append(f"CONFIG DEVICE {device} contains abbreviation: {line}")

    for block in parsed["verifies"]:
        if not nonempty_lines(block):
            errors.append(f"VERIFY DEVICE {block['device']} is empty")

    return {
        "file": str(path),
        "valid": not errors,
        "stage": parsed["stage_headers"][0] if len(parsed["stage_headers"]) == 1 else None,
        "verification_only": verification_only,
        "config_devices": config_devices,
        "verify_devices": verify_devices,
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage_file", type=Path)
    args = parser.parse_args()
    report = validate(args.stage_file.resolve())
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
