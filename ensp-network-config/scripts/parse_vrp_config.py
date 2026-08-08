#!/usr/bin/env python3
"""Extract common Huawei VRP lab configuration facts as JSON."""

from __future__ import annotations

import argparse
import ipaddress
import json
import re
from pathlib import Path


def expand_vlans(tokens: list[str]) -> list[int | str]:
    if any(token.lower() == "all" for token in tokens):
        return ["all"]
    result: list[int | str] = []
    index = 0
    while index < len(tokens):
        if (
            index + 2 < len(tokens)
            and tokens[index].isdigit()
            and tokens[index + 1].lower() == "to"
            and tokens[index + 2].isdigit()
        ):
            start, end = int(tokens[index]), int(tokens[index + 2])
            result.extend(range(start, end + 1))
            index += 3
        elif tokens[index].isdigit():
            result.append(int(tokens[index]))
            index += 1
        else:
            index += 1
    return sorted(set(result), key=lambda value: (isinstance(value, str), value))


def to_cidr(address: str, mask: str) -> str:
    return str(ipaddress.ip_interface(f"{address}/{mask}"))


def parse_config(path: Path) -> dict:
    result: dict = {
        "path": str(path),
        "sysname": None,
        "vlans": [],
        "interfaces": {},
        "ospf": [],
    }
    current_interface: str | None = None
    current_ospf: dict | None = None
    current_area: dict | None = None

    for raw_line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or set(line) == {"="}:
            continue
        tokens = line.split()
        lower = [token.lower() for token in tokens]

        if lower[0] == "sysname" and len(tokens) >= 2:
            result["sysname"] = tokens[1]
            continue
        if lower[0] in {"sys", "sy"} and len(tokens) == 2:
            result["sysname"] = tokens[1]
            continue

        if lower[0] in {"interface", "int"} and len(tokens) >= 2:
            current_interface = tokens[1]
            current_ospf = None
            current_area = None
            result["interfaces"].setdefault(current_interface, {})
            continue

        if (lower[:2] == ["vlan", "batch"] or lower[:2] == ["v", "b"]) and len(tokens) > 2:
            result["vlans"] = expand_vlans(tokens[2:])
            continue

        if lower[0] == "ospf" and len(tokens) >= 2 and tokens[1].isdigit():
            current_interface = None
            current_area = None
            router_id = None
            for marker in ("router-id", "r"):
                if marker in lower:
                    marker_index = lower.index(marker)
                    if marker_index + 1 < len(tokens):
                        router_id = tokens[marker_index + 1]
            current_ospf = {"process_id": int(tokens[1]), "router_id": router_id, "areas": []}
            result["ospf"].append(current_ospf)
            continue

        if current_ospf is not None and lower[0] in {"area", "a"} and len(tokens) >= 2:
            current_area = {"id": tokens[1], "networks": []}
            current_ospf["areas"].append(current_area)
            continue

        if current_area is not None and lower[0] in {"network", "n"} and len(tokens) >= 3:
            current_area["networks"].append({"address": tokens[1], "wildcard": tokens[2]})
            continue

        if current_interface is None:
            continue
        interface = result["interfaces"][current_interface]

        if len(tokens) >= 4 and lower[0] == "ip" and lower[1] in {"address", "ad"}:
            try:
                interface.setdefault("ipv4", []).append(to_cidr(tokens[2], tokens[3]))
            except ValueError:
                interface.setdefault("invalid_ipv4", []).append(" ".join(tokens[2:4]))
            continue

        if lower[:2] == ["port", "link-type"] and len(tokens) >= 3:
            interface["link_type"] = lower[2]
        elif lower[:3] == ["p", "l", "a"]:
            interface["link_type"] = "access"
        elif lower[:3] == ["p", "l", "t"]:
            interface["link_type"] = "trunk"
        elif lower[:3] == ["p", "l", "h"]:
            interface["link_type"] = "hybrid"
        elif lower[:3] == ["port", "default", "vlan"] and len(tokens) >= 4:
            interface["pvid"] = int(tokens[3])
        elif lower[:3] == ["p", "de", "v"] and len(tokens) >= 4:
            interface["pvid"] = int(tokens[3])
        elif lower[:4] == ["port", "hybrid", "pvid", "vlan"] and len(tokens) >= 5:
            interface["pvid"] = int(tokens[4])
        elif lower[:4] == ["p", "h", "p", "v"] and len(tokens) >= 5:
            interface["pvid"] = int(tokens[4])
        elif lower[:4] == ["port", "trunk", "allow-pass", "vlan"]:
            interface["allowed_vlans"] = expand_vlans(tokens[4:])
        elif lower[:4] == ["p", "t", "a", "v"]:
            interface["allowed_vlans"] = expand_vlans(tokens[4:])
        elif lower[:4] == ["port", "hybrid", "untagged", "vlan"]:
            interface["untagged_vlans"] = expand_vlans(tokens[4:])
        elif lower[:4] == ["p", "h", "u", "v"]:
            interface["untagged_vlans"] = expand_vlans(tokens[4:])

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("configs", nargs="+", type=Path)
    args = parser.parse_args()
    parsed = [parse_config(path.resolve()) for path in args.configs]
    print(json.dumps(parsed, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
