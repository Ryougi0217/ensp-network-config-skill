#!/usr/bin/env python3
"""Validate the deterministic structure of an eNSP stage TXT script."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


STAGE_RE = re.compile(r"^=====\s*STAGE:\s*(.+?)\s*=====$")
CONFIG_RE = re.compile(r"^=====\s*CONFIG DEVICE:\s*([A-Za-z0-9_.-]+)\s*=====$")
VERIFY_RE = re.compile(r"^=====\s*VERIFY DEVICE:\s*([A-Za-z0-9_.-]+)\s*=====$")
ABBREVIATION_RE = re.compile(
    r"^(?:sy|sys|int|dis|disp|qu|shut|desc|ip\s+ad|v\s+b|p\s+l|p\s+d\s+v|p\s+t\s+a|p\s+h\s+p|p\s+h\s+u)(?:\s|$)",
    re.IGNORECASE,
)
PLACEHOLDER_PATTERNS = (
    ("angle-bracket", re.compile(r"<[^<>\r\n]+>")),
    ("template-variable", re.compile(r"\$\{[^{}\r\n]+\}|\{\{[^{}\r\n]+\}\}")),
    (
        "marker",
        re.compile(r"(?<![A-Za-z0-9_-])(?:TODO|TBD|PLACEHOLDER|REPLACE_ME|CHANGEME)(?![A-Za-z0-9_-])", re.IGNORECASE),
    ),
)
SENSITIVE_COMMAND_PATTERNS = (
    ("reset", re.compile(r"^reset(?:\s|$)", re.IGNORECASE)),
    ("device-restart", re.compile(r"^(?:reboot|restart)(?:\s|$)", re.IGNORECASE)),
    ("scheduled-restart", re.compile(r"^schedule\s+reboot(?:\s|$)", re.IGNORECASE)),
    ("device-power", re.compile(r"^(?:power-off|power\s+off)(?:\s|$)", re.IGNORECASE)),
    ("file-delete", re.compile(r"^(?:delete|remove|erase|rmdir)(?:\s|$)", re.IGNORECASE)),
    ("format", re.compile(r"^format(?:\s|$)", re.IGNORECASE)),
    ("clear", re.compile(r"^clear(?:\s|$)", re.IGNORECASE)),
    ("rollback", re.compile(r"^rollback(?:\s|$)", re.IGNORECASE)),
    (
        "startup-change",
        re.compile(r"^(?:undo\s+)?startup(?:\s|$)", re.IGNORECASE),
    ),
)
SAVE_RE = re.compile(r"^save(?:\s+.*)?$", re.IGNORECASE)


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


def canonical_command(line: str) -> str:
    return " ".join(line.split()).casefold()


def contains_abbreviation(line: str) -> bool:
    stripped = line.strip()
    candidates = [stripped]
    if stripped.casefold().startswith("undo "):
        candidates.append(stripped[5:].lstrip())
    return any(ABBREVIATION_RE.match(candidate) for candidate in candidates)


def placeholder_kinds(line: str) -> list[str]:
    return [name for name, pattern in PLACEHOLDER_PATTERNS if pattern.search(line)]


def sensitive_command_kind(line: str) -> str | None:
    normalized = " ".join(line.split())
    for name, pattern in SENSITIVE_COMMAND_PATTERNS:
        if pattern.match(normalized):
            return name
    return None


def command_records(parsed: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for key, section in (("configs", "CONFIG"), ("verifies", "VERIFY")):
        for block in parsed[key]:
            for offset, raw_line in enumerate(block["lines"], start=1):
                line = raw_line.strip()
                if not line:
                    continue
                records.append(
                    {
                        "section": section,
                        "device": block["device"],
                        "command": line,
                        "line_number": block["line_number"] + offset,
                    }
                )
    return records


def authorization_key(section: str, device: str, command: str) -> tuple[str, str, str]:
    return section.upper(), device.casefold(), canonical_command(command)


def load_authorization(
    authorization_file: Path,
    stage_sha256: str,
) -> tuple[set[tuple[str, str, str]], str | None, list[str]]:
    errors: list[str] = []
    try:
        data = json.loads(authorization_file.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        return set(), None, [f"cannot read command authorization file {authorization_file}: {exc}"]
    if not isinstance(data, dict):
        return set(), None, ["command authorization file must contain one JSON object"]

    authorization_ref = data.get("authorization_ref")
    if not isinstance(authorization_ref, str) or not authorization_ref.strip():
        errors.append("command authorization requires a non-empty authorization_ref")

    authorized_stage_sha256 = data.get("stage_sha256")
    hash_matches = authorized_stage_sha256 == stage_sha256
    if not hash_matches:
        errors.append("command authorization stage_sha256 does not match the stage file")

    entries = data.get("authorized_commands")
    if not isinstance(entries, list) or not entries:
        errors.append("command authorization requires a non-empty authorized_commands list")
        entries = []

    keys: set[tuple[str, str, str]] = set()
    for position, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"authorized_commands[{position}] must be an object")
            continue
        section = entry.get("section")
        device = entry.get("device")
        command = entry.get("command")
        if section not in {"CONFIG", "VERIFY"}:
            errors.append(f"authorized_commands[{position}].section must be CONFIG or VERIFY")
            continue
        if not isinstance(device, str) or not device.strip():
            errors.append(f"authorized_commands[{position}].device must be a non-empty string")
            continue
        if not isinstance(command, str) or not command.strip():
            errors.append(f"authorized_commands[{position}].command must be a non-empty string")
            continue
        key = authorization_key(section, device, command)
        if key in keys:
            errors.append(f"duplicate command authorization: {section}/{device}/{command}")
            continue
        keys.add(key)

    if errors or not hash_matches:
        return set(), authorization_ref if isinstance(authorization_ref, str) else None, errors
    return keys, authorization_ref, errors


def validate(
    path: Path,
    authorization_file: Path | None = None,
    allow_abbreviations: bool = False,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8-sig")
    except OSError as exc:
        return {"file": str(path), "valid": False, "errors": [str(exc)], "warnings": warnings}
    except UnicodeDecodeError as exc:
        return {"file": str(path), "valid": False, "errors": [str(exc)], "warnings": warnings}
    parsed = parse_stage_text(text)
    stage_sha256 = hashlib.sha256(raw).hexdigest()

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

    for block in parsed["verifies"]:
        if not nonempty_lines(block):
            errors.append(f"VERIFY DEVICE {block['device']} is empty")

    records = command_records(parsed)
    sensitive_records: list[tuple[dict[str, Any], str]] = []
    for record in records:
        label = f"{record['section']} DEVICE {record['device']} line {record['line_number']}"
        line = record["command"]
        placeholders = placeholder_kinds(line)
        if placeholders:
            errors.append(
                f"{label} contains unresolved placeholder ({', '.join(placeholders)}): {line}"
            )
        if SAVE_RE.fullmatch(line):
            errors.append(f"{label} contains forbidden save command")
        if contains_abbreviation(line):
            message = f"{label} contains abbreviation: {line}"
            if allow_abbreviations:
                warnings.append(message)
            else:
                errors.append(message)
        if kind := sensitive_command_kind(line):
            sensitive_records.append((record, kind))

    authorized_keys: set[tuple[str, str, str]] = set()
    authorization_ref: str | None = None
    if authorization_file is not None:
        authorized_keys, authorization_ref, authorization_errors = load_authorization(
            authorization_file.resolve(), stage_sha256
        )
        errors.extend(authorization_errors)

    used_authorizations: set[tuple[str, str, str]] = set()
    for record, kind in sensitive_records:
        key = authorization_key(record["section"], record["device"], record["command"])
        label = f"{record['section']} DEVICE {record['device']} line {record['line_number']}"
        if key not in authorized_keys:
            errors.append(
                f"{label} contains sensitive command and requires exact explicit authorization ({kind}): "
                f"{record['command']}"
            )
            continue
        used_authorizations.add(key)
        warnings.append(
            f"{label} contains explicitly authorized sensitive command ({kind}): {record['command']}"
        )

    unused_authorizations = sorted(authorized_keys - used_authorizations)
    for section, device, command in unused_authorizations:
        errors.append(f"unused or non-sensitive command authorization: {section}/{device}/{command}")

    return {
        "file": str(path),
        "stage_sha256": stage_sha256,
        "valid": not errors,
        "stage": parsed["stage_headers"][0] if len(parsed["stage_headers"]) == 1 else None,
        "verification_only": verification_only,
        "config_devices": config_devices,
        "verify_devices": verify_devices,
        "authorization_file": str(authorization_file.resolve()) if authorization_file else None,
        "authorization_ref": authorization_ref,
        "authorized_sensitive_commands": len(used_authorizations),
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage_file", type=Path)
    parser.add_argument(
        "--authorization-file",
        type=Path,
        help="JSON authorization bound to the exact stage hash and exact sensitive commands",
    )
    parser.add_argument(
        "--allow-abbreviations",
        action="store_true",
        help="allow known command abbreviations only when the user explicitly requested them",
    )
    args = parser.parse_args()
    report = validate(
        args.stage_file.resolve(),
        authorization_file=args.authorization_file,
        allow_abbreviations=args.allow_abbreviations,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
