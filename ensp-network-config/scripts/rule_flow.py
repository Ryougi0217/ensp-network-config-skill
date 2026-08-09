#!/usr/bin/env python3
"""Index, query, validate, and stage-load eNSP design rules."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


SKILL_DIR = Path(__file__).resolve().parent.parent
REFERENCES_DIR = SKILL_DIR / "references"
CATALOG_DIR = REFERENCES_DIR / "design-rules"
CATALOG_INDEX = REFERENCES_DIR / "design-rules.md"
CAPABILITIES_FILE = REFERENCES_DIR / "rule-capabilities.json"
RULE_INDEX_FILE = REFERENCES_DIR / "rule-index.json"

RULE_HEADING_RE = re.compile(r"^## (DR-[^:]+):\s*(.+?)\s*$")
FIELD_RE = re.compile(r"^- ([A-Za-z][A-Za-z ]+):\s*(.*?)\s*$")
ACTIVE_LINK_RE = re.compile(r"\(design-rules/([^)]+\.md)\)")
RESERVED_FILE_RE = re.compile(r"`([^`]+\.md)`")

MANDATORY_FIELDS = {
    "Status",
    "Tags",
    "Evidence level",
    "Requires",
    "Provides",
    "Trigger",
    "Design goal",
    "Decision logic",
    "Recompute parameters",
    "Applicability boundary",
    "Common failure",
    "Implementation order",
    "Verification method",
}


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"无法读取 JSON {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"JSON 顶层必须是对象: {path}")
    return data


def load_document(path: Path) -> dict[str, Any]:
    if path.suffix.lower() == ".json":
        return read_json(path)
    try:
        import yaml  # type: ignore
    except ImportError as exc:
        raise SystemExit("读取 YAML rule plan 需要 PyYAML；也可以提供 JSON 文件。") from exc
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
    except (OSError, yaml.YAMLError) as exc:
        raise SystemExit(f"无法读取 rule plan {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"rule plan 顶层必须是对象: {path}")
    return data


def section(text: str, start_heading: str, end_heading: str | None) -> str:
    start = text.find(start_heading)
    if start < 0:
        raise ValueError(f"missing section: {start_heading}")
    start += len(start_heading)
    if end_heading is None:
        return text[start:]
    end = text.find(end_heading, start)
    if end < 0:
        raise ValueError(f"missing section: {end_heading}")
    return text[start:end]


def catalog_states() -> dict[str, str]:
    text = CATALOG_INDEX.read_text(encoding="utf-8")
    active = section(text, "## Active catalogs", "## Reserved routes")
    reserved = section(text, "## Reserved routes", "## Rule ownership")
    result = {name: "active" for name in ACTIVE_LINK_RE.findall(active)}
    for name in RESERVED_FILE_RE.findall(reserved):
        if name in result:
            raise ValueError(f"catalog appears as active and reserved: {name}")
        result[name] = "reserved"
    return result


def parse_token_list(value: str) -> list[str]:
    value = value.strip()
    if not value or value.lower() == "none":
        return []
    quoted = re.findall(r"`([^`]+)`", value)
    if quoted:
        return quoted
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_catalog(path: Path, state: str) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    starts: list[tuple[int, re.Match[str]]] = []
    for index, line in enumerate(lines):
        match = RULE_HEADING_RE.match(line)
        if match:
            starts.append((index, match))

    rules: list[dict[str, Any]] = []
    for position, (start, heading) in enumerate(starts):
        end = starts[position + 1][0] if position + 1 < len(starts) else len(lines)
        block_lines = lines[start:end]
        while block_lines and not block_lines[-1].strip():
            block_lines.pop()
        block = "\n".join(block_lines) + "\n"
        fields: dict[str, str] = {}
        for line in block_lines[1:]:
            field_match = FIELD_RE.match(line)
            if field_match:
                fields[field_match.group(1)] = field_match.group(2)
        missing = sorted(MANDATORY_FIELDS - fields.keys())
        if missing:
            raise ValueError(f"{path.name}:{start + 1} missing fields: {missing}")
        rules.append(
            {
                "id": heading.group(1),
                "title": heading.group(2).strip(),
                "status": fields["Status"].strip(),
                "catalog": path.name,
                "catalog_state": state,
                "tags": [item.strip() for item in fields["Tags"].split(",") if item.strip()],
                "evidence_level": fields["Evidence level"].strip(),
                "requires": parse_token_list(fields["Requires"]),
                "provides": parse_token_list(fields["Provides"]),
                "trigger": fields["Trigger"].strip(),
                "applicability_boundary": fields["Applicability boundary"].strip(),
                "file": path.relative_to(SKILL_DIR).as_posix(),
                "start_line": start + 1,
                "end_line": start + len(block_lines),
                "content_sha256": hashlib.sha256(block.encode("utf-8")).hexdigest(),
            }
        )
    return rules


def load_capability_contract() -> dict[str, Any]:
    contract = read_json(CAPABILITIES_FILE)
    capabilities = contract.get("capabilities")
    if not isinstance(capabilities, list):
        raise ValueError("rule-capabilities.json capabilities must be a list")
    names = [item.get("id") for item in capabilities if isinstance(item, dict)]
    if len(names) != len(set(names)) or any(not isinstance(name, str) for name in names):
        raise ValueError("rule-capabilities.json contains invalid or duplicate capability ids")
    return contract


def build_index() -> dict[str, Any]:
    states = catalog_states()
    contract = load_capability_contract()
    allowed_capabilities = {item["id"] for item in contract["capabilities"]}
    rules: list[dict[str, Any]] = []
    errors: list[str] = []
    for path in sorted(CATALOG_DIR.glob("*.md")):
        state = states.get(path.name, "unlisted")
        if state == "unlisted":
            errors.append(f"catalog not listed in design-rules.md: {path.name}")
        try:
            parsed = parse_catalog(path, state)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        for rule in parsed:
            unknown = sorted((set(rule["requires"]) | set(rule["provides"])) - allowed_capabilities)
            if unknown:
                errors.append(f"{rule['id']} uses unknown capabilities: {unknown}")
        rules.extend(parsed)

    ids = [rule["id"] for rule in rules]
    duplicates = sorted({rule_id for rule_id in ids if ids.count(rule_id) > 1})
    if duplicates:
        errors.append(f"duplicate rule ids: {duplicates}")
    if errors:
        raise ValueError("\n".join(errors))

    return {
        "schema_version": "1.0.0",
        "source": "references/design-rules/*.md",
        "catalog_index": "references/design-rules.md",
        "capability_contract": "references/rule-capabilities.json",
        "rules": sorted(rules, key=lambda item: item["id"]),
    }


def index_text(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def current_index() -> dict[str, Any]:
    try:
        generated = build_index()
    except (OSError, ValueError) as exc:
        raise SystemExit(f"无法构建规则索引: {exc}") from exc
    if not RULE_INDEX_FILE.is_file():
        raise SystemExit("规则索引不存在；先运行 rule_flow.py index。")
    stored = read_json(RULE_INDEX_FILE)
    if stored != generated:
        raise SystemExit("规则索引已过期；先运行 rule_flow.py index。")
    return stored


def rule_map(index: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {rule["id"]: rule for rule in index["rules"]}


def list_of_dicts(data: dict[str, Any], key: str, errors: list[str]) -> list[dict[str, Any]]:
    value = data.get(key, [])
    if not isinstance(value, list):
        errors.append(f"{key} must be a list")
        return []
    result: list[dict[str, Any]] = []
    for position, item in enumerate(value):
        if not isinstance(item, dict):
            errors.append(f"{key}[{position}] must be an object")
        else:
            result.append(item)
    return result


def duplicate_values(items: list[dict[str, Any]], key: str) -> list[str]:
    values = [str(item.get(key)) for item in items if item.get(key) is not None]
    return sorted({value for value in values if values.count(value) > 1})


def detect_cycles(edges: dict[str, set[str]]) -> list[list[str]]:
    visiting: list[str] = []
    visited: set[str] = set()
    cycles: list[list[str]] = []

    def walk(node: str) -> None:
        if node in visiting:
            start = visiting.index(node)
            cycle = visiting[start:] + [node]
            if cycle not in cycles:
                cycles.append(cycle)
            return
        if node in visited:
            return
        visiting.append(node)
        for child in sorted(edges.get(node, set())):
            walk(child)
        visiting.pop()
        visited.add(node)

    for node in sorted(edges):
        walk(node)
    return cycles


def validate_plan(
    data: dict[str, Any], index: dict[str, Any], contract: dict[str, Any], enforce_stage: str | None = None
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if data.get("schema_version") != "1.0.0":
        errors.append("schema_version must be '1.0.0'")
    if not re.fullmatch(r"v\d+", str(data.get("baseline_version") or "")):
        errors.append("baseline_version must use vN format")
    if data.get("mode") not in {"simple", "staged"}:
        errors.append("mode must be simple or staged")
    rules = rule_map(index)
    capability_names = {item["id"] for item in contract["capabilities"]}
    maturity_rank = contract["maturity_rank"]
    application_states = set(contract["application_states"])
    validation_states = set(contract["validation_states"])
    reason_codes = set(contract["reason_codes"])

    requirements = list_of_dicts(data, "requirements", errors)
    choices = list_of_dicts(data, "choice_groups", errors)
    capabilities = list_of_dicts(data, "capabilities", errors)
    instances = list_of_dicts(data, "instances", errors)

    for key, items in (("requirements", requirements), ("choice_groups", choices), ("capabilities", capabilities), ("instances", instances)):
        duplicates = duplicate_values(items, "id")
        if duplicates:
            errors.append(f"duplicate {key} ids: {duplicates}")

    instance_by_id = {str(item.get("id")): item for item in instances if item.get("id")}
    capability_by_id = {str(item.get("id")): item for item in capabilities if item.get("id")}

    for capability in capabilities:
        cap_id = capability.get("id")
        name = capability.get("name")
        maturity = capability.get("maturity")
        if not isinstance(cap_id, str) or not cap_id:
            errors.append("capability id must be a non-empty string")
        if name not in capability_names:
            errors.append(f"{cap_id}: unknown capability name {name!r}")
        if maturity not in maturity_rank:
            errors.append(f"{cap_id}: invalid maturity {maturity!r}")
        if not isinstance(capability.get("scope_ref"), str) or not capability.get("scope_ref"):
            errors.append(f"{cap_id}: scope_ref must be a non-empty string")
        evidence_refs = capability.get("evidence_refs", [])
        if not isinstance(evidence_refs, list):
            errors.append(f"{cap_id}: evidence_refs must be a list")

    edges: dict[str, set[str]] = {instance_id: set() for instance_id in instance_by_id}
    for instance in instances:
        instance_id = instance.get("id")
        rule_id = instance.get("rule_id")
        if not isinstance(instance_id, str) or not instance_id:
            errors.append("instance id must be a non-empty string")
            continue
        rule = rules.get(rule_id)
        if rule is None:
            errors.append(f"{instance_id}: unknown rule_id {rule_id!r}")
            continue

        application_state = instance.get("application_state")
        validation_state = instance.get("validation_state")
        reason_code = instance.get("reason_code")
        if application_state not in application_states:
            errors.append(f"{instance_id}: invalid application_state {application_state!r}")
        if validation_state not in validation_states:
            errors.append(f"{instance_id}: invalid validation_state {validation_state!r}")
        if reason_code not in reason_codes:
            errors.append(f"{instance_id}: invalid reason_code {reason_code!r}")
        if application_state == "applied" and (rule["status"] != "validated" or rule["catalog_state"] != "active"):
            errors.append(
                f"{instance_id}: applied requires an active validated rule; {rule_id} is {rule['status']}/{rule['catalog_state']}"
            )
        if application_state == "advisory" and rule["status"] == "deprecated":
            errors.append(f"{instance_id}: deprecated rule cannot be advisory")
        if application_state in {"matched", "skipped"}:
            warnings.append(f"{instance_id}: keep {application_state} decisions in rule-selection-log.jsonl")

        scope_refs = instance.get("scope_refs", [])
        if not isinstance(scope_refs, list) or not scope_refs:
            errors.append(f"{instance_id}: scope_refs must be a non-empty list")
        assertion_refs = instance.get("assertion_refs", [])
        if not isinstance(assertion_refs, list):
            errors.append(f"{instance_id}: assertion_refs must be a list")
        elif application_state == "applied" and not assertion_refs:
            errors.append(f"{instance_id}: applied rule requires assertion_refs")

        required = instance.get("requires", {})
        if not isinstance(required, dict):
            errors.append(f"{instance_id}: requires must map capability refs to minimum maturity")
            required = {}
        consumed_names: set[str] = set()
        for cap_ref, minimum in required.items():
            capability = capability_by_id.get(str(cap_ref))
            if capability is None:
                errors.append(f"{instance_id}: missing required capability {cap_ref}")
                continue
            if isinstance(capability.get("name"), str):
                consumed_names.add(capability["name"])
            if capability.get("name") not in rule["requires"]:
                errors.append(
                    f"{instance_id}: capability {capability.get('name')!r} is not declared by {rule_id} Requires"
                )
            if minimum not in maturity_rank or minimum == "forced":
                errors.append(f"{instance_id}: invalid minimum maturity {minimum!r} for {cap_ref}")
                continue
            actual = capability.get("maturity")
            provider = capability.get("provider")
            if isinstance(provider, str) and provider in instance_by_id:
                edges[provider].add(instance_id)
                if instance_by_id[provider].get("application_state") == "blocked" and application_state == "applied":
                    errors.append(f"{instance_id}: required capability {cap_ref} is provided by blocked {provider}")
            if actual == "forced":
                if instance.get("forced_continue") is not True:
                    errors.append(f"{instance_id}: forced capability {cap_ref} requires forced_continue: true")
                else:
                    warnings.append(f"{instance_id}: proceeding with forced capability {cap_ref}")
            elif actual in maturity_rank and maturity_rank[actual] < maturity_rank[minimum]:
                message = f"{instance_id}: {cap_ref} maturity {actual} is below required {minimum}"
                if enforce_stage is not None and instance.get("stage") == enforce_stage and application_state == "applied":
                    errors.append(message)
                else:
                    warnings.append(message)
        if application_state == "applied":
            missing_requires = sorted(set(rule["requires"]) - consumed_names)
            if missing_requires:
                errors.append(f"{instance_id}: missing declared Requires capabilities {missing_requires}")

        provided = instance.get("provides", [])
        if not isinstance(provided, list):
            errors.append(f"{instance_id}: provides must be a list of capability refs")
            provided = []
        provided_names: set[str] = set()
        for cap_ref in provided:
            capability = capability_by_id.get(str(cap_ref))
            if capability is None:
                errors.append(f"{instance_id}: missing provided capability {cap_ref}")
                continue
            if isinstance(capability.get("name"), str):
                provided_names.add(capability["name"])
            if capability.get("provider") != instance_id:
                errors.append(f"{instance_id}: capability {cap_ref} provider does not point back to this instance")
            if capability.get("name") not in rule["provides"]:
                errors.append(
                    f"{instance_id}: capability {capability.get('name')!r} is not declared by {rule_id} Provides"
                )
        if application_state == "applied":
            missing_provides = sorted(set(rule["provides"]) - provided_names)
            if missing_provides:
                errors.append(f"{instance_id}: missing declared Provides capabilities {missing_provides}")
        if application_state == "advisory" and provided:
            errors.append(f"{instance_id}: advisory rules cannot provide project capabilities")

    for capability in capabilities:
        provider = capability.get("provider")
        if provider not in {"baseline", "user", "project"} and provider not in instance_by_id:
            errors.append(f"{capability.get('id')}: unknown provider {provider!r}")
        elif provider in instance_by_id and instance_by_id[provider].get("application_state") == "advisory":
            errors.append(f"{capability.get('id')}: advisory provider {provider} cannot supply a project capability")

    for cycle in detect_cycles(edges):
        errors.append("rule dependency cycle: " + " -> ".join(cycle))

    allowed_groups = contract.get("choice_groups", {})
    choice_keys: set[tuple[str, str, str]] = set()
    for choice in choices:
        choice_id = choice.get("id")
        group = choice.get("group")
        scope_ref = choice.get("scope_ref")
        phase = choice.get("phase")
        selected = choice.get("selected")
        if group not in allowed_groups:
            errors.append(f"{choice_id}: unknown choice group {group!r}")
            continue
        if selected not in allowed_groups[group]:
            errors.append(f"{choice_id}: invalid {group} selection {selected!r}")
        key = (str(group), str(scope_ref), str(phase))
        if key in choice_keys:
            errors.append(f"duplicate choice for group/scope/phase: {key}")
        choice_keys.add(key)

    allowed_handling = set(contract.get("requirement_handling", []))
    for requirement in requirements:
        req_id = requirement.get("id")
        handling = requirement.get("handling")
        if not isinstance(req_id, str) or not req_id:
            errors.append("requirement id must be a non-empty string")
        if not isinstance(handling, str):
            errors.append(f"{req_id}: handling must be a string")
        elif handling.startswith("rule:"):
            target = handling[len("rule:") :]
            if target not in instance_by_id:
                errors.append(f"{req_id}: handling references unknown instance {target}")
        elif handling not in allowed_handling:
            errors.append(f"{req_id}: unsupported handling {handling!r}")

    limits = contract.get("context_limits", {})
    by_stage: dict[str, list[dict[str, Any]]] = {}
    for instance in instances:
        stage = str(instance.get("stage") or "")
        if stage:
            by_stage.setdefault(stage, []).append(instance)
    for stage, stage_instances in by_stage.items():
        body_rules = {
            item.get("rule_id")
            for item in stage_instances
            if item.get("application_state") in {"applied", "advisory"}
        }
        catalogs = {rules[rule_id]["catalog"] for rule_id in body_rules if rule_id in rules}
        advisories = [item for item in stage_instances if item.get("application_state") == "advisory"]
        if len(body_rules) > limits.get("max_rules_per_stage", 12):
            errors.append(f"{stage}: context has {len(body_rules)} rules; split the stage")
        if len(catalogs) > limits.get("max_catalogs_per_stage", 4):
            errors.append(f"{stage}: context has {len(catalogs)} catalogs; split the stage")
        if len(advisories) > limits.get("max_candidate_advisories_per_stage", 3):
            errors.append(f"{stage}: context has {len(advisories)} candidate advisories; reduce them")

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "counts": {
            "requirements": len(requirements),
            "choice_groups": len(choices),
            "capabilities": len(capabilities),
            "instances": len(instances),
        },
    }


def extract_rule_block(rule: dict[str, Any]) -> str:
    path = SKILL_DIR / rule["file"]
    lines = path.read_text(encoding="utf-8").splitlines()
    block = "\n".join(lines[rule["start_line"] - 1 : rule["end_line"]]) + "\n"
    digest = hashlib.sha256(block.encode("utf-8")).hexdigest()
    if digest != rule["content_sha256"]:
        raise SystemExit(f"规则内容与索引不一致: {rule['id']}；先运行 rule_flow.py index。")
    return block


def build_context(data: dict[str, Any], index: dict[str, Any], stage: str) -> str:
    rules = rule_map(index)
    stage_instances = [
        item
        for item in data.get("instances", [])
        if isinstance(item, dict)
        and item.get("stage") == stage
        and item.get("application_state") in {"applied", "advisory"}
    ]
    if not stage_instances:
        raise SystemExit(f"阶段没有 applied/advisory 规则实例: {stage}")

    capability_by_id = {
        item["id"]: item for item in data.get("capabilities", []) if isinstance(item, dict) and item.get("id")
    }
    used_capability_refs: list[str] = []
    for instance in stage_instances:
        used_capability_refs.extend(str(item) for item in instance.get("requires", {}).keys())
        used_capability_refs.extend(str(item) for item in instance.get("provides", []))

    lines = [
        f"# Rule context: {stage}",
        "",
        "Generated from the active rule plan. Read only this stage context; do not load unrelated catalogs.",
        "",
        "## Capabilities",
        "",
    ]
    for cap_ref in dict.fromkeys(used_capability_refs):
        capability = capability_by_id.get(cap_ref)
        if capability:
            lines.append(
                f"- `{cap_ref}`: `{capability.get('name')}` / `{capability.get('maturity')}` / scope `{capability.get('scope_ref')}`"
            )

    lines.extend(["", "## Instances", ""])
    for instance in stage_instances:
        lines.append(
            f"- `{instance.get('id')}` -> `{instance.get('rule_id')}`; state `{instance.get('application_state')}`; scopes {json.dumps(instance.get('scope_refs', []), ensure_ascii=False)}; assertions {json.dumps(instance.get('assertion_refs', []), ensure_ascii=False)}"
        )

    lines.extend(["", "## Rule bodies", ""])
    seen: set[str] = set()
    for instance in stage_instances:
        rule_id = instance["rule_id"]
        if rule_id in seen:
            continue
        seen.add(rule_id)
        lines.append(extract_rule_block(rules[rule_id]).rstrip())
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    index_cmd = sub.add_parser("index", help="build or check the generated rule index")
    index_cmd.add_argument("--check", action="store_true")

    query = sub.add_parser("query", help="query rule metadata without loading rule bodies")
    query.add_argument("--tags", nargs="+", required=True)
    query.add_argument("--match", choices=("any", "all"), default="any")
    query.add_argument("--include-candidates", action="store_true")
    query.add_argument("--include-reserved", action="store_true")
    query.add_argument("--limit", type=int, default=30)

    validate = sub.add_parser("validate", help="validate a project rule plan")
    validate.add_argument("plan", type=Path)
    validate.add_argument("--stage", help="enforce capability maturity for one execution stage")

    context = sub.add_parser("context", help="build a bounded context pack for one stage")
    context.add_argument("plan", type=Path)
    context.add_argument("--stage", required=True)
    context.add_argument("--output", type=Path)
    context.add_argument("--force", action="store_true")

    args = parser.parse_args()

    if args.command == "index":
        try:
            generated = build_index()
        except (OSError, ValueError) as exc:
            raise SystemExit(f"无法构建规则索引: {exc}") from exc
        rendered = index_text(generated)
        if args.check:
            if not RULE_INDEX_FILE.is_file() or RULE_INDEX_FILE.read_text(encoding="utf-8") != rendered:
                print("规则索引不一致；运行 rule_flow.py index 更新。")
                return 1
            print(f"规则索引有效：{len(generated['rules'])} 条规则。")
            return 0
        RULE_INDEX_FILE.write_text(rendered, encoding="utf-8")
        print(f"已生成规则索引：{RULE_INDEX_FILE}（{len(generated['rules'])} 条规则）")
        return 0

    index = current_index()
    contract = load_capability_contract()

    if args.command == "query":
        wanted_tags = {item.strip() for item in args.tags if item.strip()}
        allowed_status = {"validated"}
        if args.include_candidates:
            allowed_status.add("candidate")
        matches: list[dict[str, Any]] = []
        for rule in index["rules"]:
            if rule["status"] not in allowed_status:
                continue
            if rule["catalog_state"] != "active" and not args.include_reserved:
                continue
            overlap = wanted_tags & set(rule["tags"])
            if (args.match == "all" and overlap != wanted_tags) or (args.match == "any" and not overlap):
                continue
            matches.append(
                {
                    key: rule[key]
                    for key in (
                        "id",
                        "title",
                        "status",
                        "catalog",
                        "catalog_state",
                        "tags",
                        "requires",
                        "provides",
                        "trigger",
                        "applicability_boundary",
                        "file",
                        "start_line",
                        "end_line",
                    )
                }
            )
        print(json.dumps({"query_tags": sorted(wanted_tags), "matches": matches[: args.limit]}, ensure_ascii=False, indent=2))
        return 0

    plan = load_document(args.plan.resolve())
    report = validate_plan(plan, index, contract, getattr(args, "stage", None))

    if args.command == "validate":
        report["plan"] = str(args.plan.resolve())
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["valid"] else 1

    if not report["valid"]:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1
    rendered = build_context(plan, index, args.stage)
    if args.output:
        output = args.output.resolve()
        if output.exists() and not args.force:
            raise SystemExit(f"输出已存在，拒绝覆盖；使用 --force 明确覆盖: {output}")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        print(f"已生成阶段规则上下文: {output}")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
