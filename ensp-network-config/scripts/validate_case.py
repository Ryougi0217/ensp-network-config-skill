#!/usr/bin/env python3
"""Validate an eNSP case directory and emit a JSON report."""

from __future__ import annotations

import argparse
import ipaddress
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required to validate steps.yaml and assertions.yaml") from exc

from parse_vrp_config import parse_config


def endpoint_device(endpoint: object) -> str | None:
    if isinstance(endpoint, str):
        return endpoint.split(":", 1)[0]
    if isinstance(endpoint, dict):
        value = endpoint.get("device")
        return value if isinstance(value, str) else None
    return None


def endpoint_interface(endpoint: object) -> str | None:
    if isinstance(endpoint, str) and ":" in endpoint:
        return endpoint.split(":", 1)[1]
    if isinstance(endpoint, dict):
        value = endpoint.get("interface")
        return value if isinstance(value, str) else None
    return None


def normalize_interface_name(name: str) -> str:
    aliases = (
        ("GE", "GigabitEthernet"),
        ("GigabitEthernet", "GigabitEthernet"),
        ("Ethernet", "Ethernet"),
        ("E", "Ethernet"),
    )
    compact = name.replace(" ", "")
    for prefix, expanded in aliases:
        if compact.lower().startswith(prefix.lower()):
            suffix = compact[len(prefix) :]
            if suffix and suffix[0].isdigit():
                return expanded + suffix
    return compact


def wildcard_network(address: str, wildcard: str) -> ipaddress.IPv4Network:
    wildcard_value = int(ipaddress.IPv4Address(wildcard))
    netmask = ipaddress.IPv4Address(wildcard_value ^ 0xFFFFFFFF)
    return ipaddress.ip_network(f"{address}/{netmask}", strict=False)


def collect_ips(topology: dict) -> list[str]:
    values: list[str] = []
    for device in topology.get("devices", []):
        if isinstance(device.get("ipv4"), str):
            values.append(device["ipv4"])
        for interface in device.get("interfaces", []):
            for address in interface.get("ipv4", []):
                if isinstance(address, str):
                    values.append(address)
                elif isinstance(address, dict) and address.get("address") is not None:
                    values.append(f"{address['address']}/{address.get('prefix_length', 32)}")
    for gateway in topology.get("gateways", []):
        if isinstance(gateway.get("ipv4"), str):
            values.append(gateway["ipv4"])
    return values


def validate(case_dir: Path) -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    required = ["case.json", "topology.json", "steps.yaml", "assertions.yaml"]
    for name in required:
        if not (case_dir / name).is_file():
            errors.append(f"missing required file: {name}")
    if errors:
        return {"case": str(case_dir), "valid": False, "errors": errors, "warnings": warnings}

    try:
        case = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
        topology = json.loads((case_dir / "topology.json").read_text(encoding="utf-8"))
        steps = yaml.safe_load((case_dir / "steps.yaml").read_text(encoding="utf-8"))
        assertions = yaml.safe_load((case_dir / "assertions.yaml").read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"parse error: {exc}")
        return {"case": str(case_dir), "valid": False, "errors": errors, "warnings": warnings}

    case_id = case.get("case_id")
    if case_id != case_dir.name:
        errors.append(f"case_id {case_id!r} does not match directory name {case_dir.name!r}")
    for document_name, document in (("topology", topology), ("steps", steps), ("assertions", assertions)):
        if not isinstance(document, dict) or document.get("case_id") != case_id:
            errors.append(f"{document_name} case_id does not match case.json")

    devices = topology.get("devices", [])
    device_ids = [device.get("id") for device in devices if isinstance(device, dict)]
    if len(device_ids) != len(set(device_ids)):
        errors.append("device IDs are not unique")
    known_devices = set(device_ids)

    for index, link in enumerate(topology.get("links", [])):
        for side in ("a", "b"):
            device = endpoint_device(link.get(side))
            if device not in known_devices:
                errors.append(f"links[{index}].{side} references unknown device {device!r}")
        network = link.get("network")
        if network:
            try:
                ipaddress.ip_network(network, strict=False)
            except ValueError:
                errors.append(f"links[{index}] has invalid network {network!r}")

    parsed_ips: list[ipaddress.IPv4Interface] = []
    for value in collect_ips(topology):
        try:
            parsed_ips.append(ipaddress.ip_interface(value))
        except ValueError:
            errors.append(f"invalid IPv4 value: {value!r}")
    concrete = [str(item.ip) for item in parsed_ips]
    duplicates = sorted({value for value in concrete if concrete.count(value) > 1})
    if duplicates:
        warnings.append(f"duplicate addresses require review: {duplicates}")

    configs: list[dict] = []
    configs_by_sysname: dict[str, dict] = {}
    for relative in case.get("artifacts", {}).get("provided_configs", []):
        config_path = case_dir / relative
        if not config_path.is_file():
            errors.append(f"missing configuration artifact: {relative}")
            continue
        parsed = parse_config(config_path)
        configs.append(parsed)
        if parsed.get("sysname"):
            configs_by_sysname[parsed["sysname"]] = parsed
        expected_name = config_path.stem.lower()
        if parsed.get("sysname") and parsed["sysname"].lower() != expected_name:
            warnings.append(
                f"{relative} sysname {parsed['sysname']!r} differs from filename {config_path.stem!r}"
            )

    for index, link in enumerate(topology.get("links", [])):
        network_value = link.get("network")
        if not network_value:
            continue
        network = ipaddress.ip_network(network_value, strict=False)
        for side in ("a", "b"):
            device = endpoint_device(link.get(side))
            interface = endpoint_interface(link.get(side))
            if device not in configs_by_sysname or not interface:
                continue
            normalized = normalize_interface_name(interface)
            parsed_interface = configs_by_sysname[device].get("interfaces", {}).get(normalized)
            if parsed_interface is None:
                errors.append(f"links[{index}].{side} interface {device}:{interface} is absent from its config")
                continue
            addresses = parsed_interface.get("ipv4", [])
            if not any(ipaddress.ip_interface(value).ip in network for value in addresses):
                errors.append(
                    f"links[{index}].{side} {device}:{interface} has no address in {network_value}"
                )

    ospf_topology = topology.get("ospf")
    if isinstance(ospf_topology, dict):
        router_ids: list[str] = []
        advertised_by_area: dict[str, set[ipaddress.IPv4Network]] = {}
        routers_by_area: dict[str, set[str]] = {}
        for config in configs:
            sysname = config.get("sysname") or "unknown"
            for process in config.get("ospf", []):
                if process.get("router_id"):
                    router_ids.append(process["router_id"])
                for area in process.get("areas", []):
                    area_id = str(area.get("id"))
                    routers_by_area.setdefault(area_id, set()).add(sysname)
                    target = advertised_by_area.setdefault(area_id, set())
                    for statement in area.get("networks", []):
                        try:
                            target.add(wildcard_network(statement["address"], statement["wildcard"]))
                        except (KeyError, ValueError) as exc:
                            errors.append(f"invalid OSPF network statement on {sysname}: {exc}")
        duplicates = sorted({router_id for router_id in router_ids if router_ids.count(router_id) > 1})
        if duplicates:
            errors.append(f"duplicate OSPF Router IDs: {duplicates}")

        expected_areas = ospf_topology.get("areas", {})
        for area_id, networks in expected_areas.items():
            observed = advertised_by_area.get(str(area_id), set())
            for network_value in networks:
                expected = ipaddress.ip_network(network_value, strict=False)
                if expected not in observed:
                    errors.append(f"OSPF area {area_id} does not advertise {network_value}")

        backbone_routers = routers_by_area.get("0", set())
        if expected_areas and not backbone_routers:
            errors.append("OSPF topology has no configured Area 0")
        for area_id in expected_areas:
            if str(area_id) == "0":
                continue
            if not (routers_by_area.get(str(area_id), set()) & backbone_routers):
                errors.append(f"OSPF area {area_id} has no ABR connected to Area 0")

    missing = case.get("missing_required_evidence", [])
    approved = case.get("approval_status") == "approved"
    if approved and missing:
        errors.append("approved case still has missing_required_evidence")
    if approved:
        validation_path = case_dir / "validation.json"
        if not validation_path.is_file():
            errors.append("approved case is missing validation.json")
        else:
            validation = json.loads(validation_path.read_text(encoding="utf-8"))
            if validation.get("validation_status") != "passed":
                errors.append("approved case validation_status is not passed")

    if approved:
        for group in ("result_assertions", "runtime_assertions"):
            for assertion in assertions.get(group, []):
                if assertion.get("state") != "passed":
                    errors.append(f"approved assertion {assertion.get('id')!r} is not passed")

    return {
        "case": str(case_dir),
        "case_id": case_id,
        "valid": not errors,
        "device_count": len(devices),
        "link_count": len(topology.get("links", [])),
        "config_count": len(configs),
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_dir", type=Path)
    args = parser.parse_args()
    report = validate(args.case_dir.resolve())
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
