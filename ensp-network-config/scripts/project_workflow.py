#!/usr/bin/env python3
"""Create and operate a persistent staged eNSP configuration project."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


STAGE_STATES = {
    "planned",
    "script_generated",
    "statically_validated",
    "delivered",
    "passed",
    "failed",
    "forced_pass",
    "needs_rework",
    "skipped",
}
RESULT_STATES = {"planning", "script_ready", "implemented", "verified", "completed_with_risks"}
TRANSITIONS = {
    "planned": {"script_generated", "skipped"},
    "script_generated": {"statically_validated", "needs_rework"},
    "statically_validated": {"delivered", "needs_rework"},
    "delivered": {"passed", "failed", "needs_rework"},
    "passed": {"needs_rework"},
    "failed": {"forced_pass", "needs_rework", "script_generated"},
    "forced_pass": {"needs_rework"},
    "needs_rework": {"script_generated", "skipped"},
    "skipped": {"needs_rework"},
}

STAGED_SKELETON = [
    ("01-access", "接入层", []),
    ("02-aggregation", "汇聚层", ["01-access"]),
    ("03-core-backbone", "核心层与骨干路由", ["02-aggregation"]),
    ("04-branches", "独立路由区域或业务分支", ["03-core-backbone"]),
    ("05-services-exit", "网络服务与出口", ["03-core-backbone"]),
    ("06-security", "安全策略", ["04-branches", "05-services-exit"]),
    ("98-acceptance", "全网验收", ["06-security"]),
]
SIMPLE_SKELETON = [
    ("01-complete", "完整配置", []),
    ("98-acceptance", "全网验收", ["01-complete"]),
]


def now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def safe_project_id(value: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "-", value.strip())
    cleaned = re.sub(r"\s+", "-", cleaned).strip(".-")
    if not cleaned:
        raise ValueError("项目名称不能生成有效目录名。")
    return cleaned


def ensure_project_dir(path: Path) -> Path:
    resolved = path.resolve()
    if not (resolved / "project.json").is_file():
        raise SystemExit(f"不是有效项目目录: {resolved}")
    return resolved


def load_project(path: Path) -> tuple[Path, dict[str, Any]]:
    project_dir = ensure_project_dir(path)
    try:
        data = json.loads((project_dir / "project.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"无法读取 project.json: {exc}") from exc
    return project_dir, data


def save_project(project_dir: Path, data: dict[str, Any]) -> None:
    data["updated_at"] = now()
    (project_dir / "project.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    render_stage_plan(project_dir, data)


def yaml_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


def render_stage_plan(project_dir: Path, data: dict[str, Any]) -> None:
    lines = [
        f"project_id: {yaml_scalar(data['project_id'])}",
        f"mode: {yaml_scalar(data['mode'])}",
        f"baseline_version: {yaml_scalar(data['baseline']['version'])}",
        f"baseline_status: {yaml_scalar(data['baseline']['status'])}",
        f"active_rule_plan: {yaml_scalar(data.get('active_rule_plan'))}",
        "stages:",
    ]
    for stage in data["stages"]:
        lines.extend(
            [
                f"  - id: {yaml_scalar(stage['id'])}",
                f"    title: {yaml_scalar(stage['title'])}",
                f"    status: {yaml_scalar(stage['status'])}",
                f"    depends_on: {json.dumps(stage['depends_on'], ensure_ascii=False)}",
                f"    current_script: {yaml_scalar(stage.get('current_script'))}",
                f"    evidence_type: {yaml_scalar(stage.get('evidence_type'))}",
            ]
        )
    (project_dir / "stage-plan.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def create_project(path: Path, name: str, mode: str) -> Path:
    project_dir = path.resolve()
    if project_dir.exists() and any(project_dir.iterdir()):
        raise SystemExit(f"目标目录非空，拒绝覆盖: {project_dir}")
    project_dir.mkdir(parents=True, exist_ok=True)
    for relative in ("planning", "planning/context", "scripts", "validation", "evidence"):
        (project_dir / relative).mkdir()

    project_id = safe_project_id(name)
    skeleton = SIMPLE_SKELETON if mode == "simple" else STAGED_SKELETON
    created_at = now()
    data: dict[str, Any] = {
        "project_id": project_id,
        "name": name,
        "mode": mode,
        "result_state": "planning",
        "baseline": {"version": "v0", "status": "draft", "confirmed_by": None, "confirmed_at": None},
        "active_rule_plan": "planning/rule-plan-v0.yaml",
        "active_stage_id": None,
        "stages": [
            {
                "id": stage_id,
                "title": title,
                "depends_on": dependencies,
                "status": "planned",
                "current_script": None,
                "evidence_type": None,
                "history": [{"state": "planned", "at": created_at}],
            }
            for stage_id, title, dependencies in skeleton
        ],
        "risks": [],
        "created_at": created_at,
        "updated_at": created_at,
    }
    (project_dir / "project.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (project_dir / "topology.json").write_text(
        json.dumps(
            {"source": {}, "devices": [], "links": [], "uncertainties": []},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (project_dir / "requirements.yaml").write_text(
        "status: draft\nrequirements: []\n",
        encoding="utf-8",
    )
    (project_dir / "planning" / "rule-plan-v0.yaml").write_text(
        "baseline_version: \"v0\"\n"
        f"mode: {mode}\n"
        "requirements: []\n"
        "choice_groups: []\n"
        "capabilities: []\n"
        "feature_profiles: []\n"
        "instances: []\n",
        encoding="utf-8",
    )
    planning_files = {
        "网络设备与链路规划.txt": "网络设备与链路规划\n状态：待提取与确认\n",
        "VLAN与网关规划.txt": "VLAN与网关规划\n状态：待提取与确认\n",
        "终端与服务器地址规划.txt": "终端与服务器地址规划\n状态：待提取与确认\n",
        "阶段实施计划.txt": "阶段实施计划\n状态：待基线确认\n",
    }
    for filename, content in planning_files.items():
        (project_dir / "planning" / filename).write_text(content, encoding="utf-8")
    render_stage_plan(project_dir, data)
    return project_dir


def find_stage(data: dict[str, Any], stage_id: str) -> dict[str, Any]:
    for stage in data["stages"]:
        if stage["id"] == stage_id:
            return stage
    raise SystemExit(f"不存在阶段: {stage_id}")


def validate_and_version_rule_plan(
    project_dir: Path, data: dict[str, Any], target_version: str
) -> tuple[str, list[str]]:
    from rule_flow import current_index, load_capability_contract, load_document, validate_plan

    relative = Path(str(data.get("active_rule_plan") or "planning/rule-plan-v0.yaml"))
    source = (project_dir / relative).resolve()
    try:
        source.relative_to(project_dir.resolve())
    except ValueError as exc:
        raise SystemExit(f"规则计划必须位于项目目录内: {source}") from exc
    if not source.is_file():
        raise SystemExit(f"规则计划不存在: {source}")

    plan_data = load_document(source)
    if "feature_profiles" not in plan_data:
        raise SystemExit(
            "项目规则计划缺少当前结构要求的 feature_profiles；"
            "旧计划只能用于审计，不能确认新基线。"
        )
    if plan_data.get("mode") != data.get("mode"):
        raise SystemExit(
            f"规则计划模式与项目不一致: plan={plan_data.get('mode')!r}, project={data.get('mode')!r}"
        )
    if plan_data.get("baseline_version") != data["baseline"]["version"]:
        raise SystemExit(
            "规则计划版本与当前草稿基线不一致: "
            f"plan={plan_data.get('baseline_version')!r}, project={data['baseline']['version']!r}"
        )
    report = validate_plan(plan_data, current_index(), load_capability_contract())
    if not report["valid"]:
        details = "\n".join(f"- {item}" for item in report["errors"])
        raise SystemExit(f"规则计划未通过校验，不能确认基线:\n{details}")

    target_relative = Path("planning") / f"rule-plan-{target_version}.yaml"
    target = project_dir / target_relative
    if target.exists() and target.resolve() != source:
        raise SystemExit(f"目标规则计划已存在，拒绝覆盖: {target}")
    rendered, count = re.subn(
        r"(?m)^baseline_version:\s*.*$",
        f"baseline_version: {json.dumps(target_version, ensure_ascii=False)}",
        source.read_text(encoding="utf-8-sig"),
        count=1,
    )
    if count != 1:
        raise SystemExit(f"规则计划缺少 baseline_version: {source}")
    if target.resolve() != source:
        target.write_text(rendered, encoding="utf-8")
    return target_relative.as_posix(), report["warnings"]


def dependencies_satisfied(data: dict[str, Any], stage: dict[str, Any]) -> bool:
    allowed = {"passed", "forced_pass", "skipped"}
    return all(find_stage(data, item)["status"] in allowed for item in stage["depends_on"])


def update_active_stage(data: dict[str, Any]) -> None:
    data["active_stage_id"] = None
    if data["baseline"]["status"] != "confirmed":
        return
    for stage in data["stages"]:
        if stage["status"] in {"planned", "script_generated", "statically_validated", "delivered", "failed", "needs_rework"}:
            if dependencies_satisfied(data, stage):
                data["active_stage_id"] = stage["id"]
                return


def transition_stage(
    data: dict[str, Any],
    stage_id: str,
    target_state: str,
    reason: str | None,
    evidence_type: str | None,
    script: str | None,
) -> None:
    if target_state not in STAGE_STATES:
        raise SystemExit(f"无效阶段状态: {target_state}")
    stage = find_stage(data, stage_id)
    current = stage["status"]
    if target_state not in TRANSITIONS[current]:
        raise SystemExit(f"不允许的状态转换: {stage_id} {current} -> {target_state}")
    if target_state == "script_generated" and not script and not stage.get("current_script"):
        raise SystemExit("标记 script_generated 时必须提供 --script。")
    if target_state == "forced_pass" and not reason:
        raise SystemExit("forced_pass 必须提供 --reason，且只能由用户明确决定。")
    if target_state in {"passed", "failed"} and not evidence_type:
        raise SystemExit(f"{target_state} 必须提供 --evidence-type。")

    stage["status"] = target_state
    if script:
        stage["current_script"] = script
    if evidence_type:
        stage["evidence_type"] = evidence_type
    event = {"state": target_state, "at": now()}
    if reason:
        event["reason"] = reason
    if evidence_type:
        event["evidence_type"] = evidence_type
    if script:
        event["script"] = script
    stage["history"].append(event)
    if target_state == "forced_pass":
        data["risks"].append(
            {"id": f"R{len(data['risks']) + 1:03d}", "stage_id": stage_id, "reason": reason, "status": "open"}
        )
    update_active_stage(data)


def dependent_stage_ids(data: dict[str, Any], root_id: str) -> set[str]:
    affected = {root_id}
    changed = True
    while changed:
        changed = False
        for stage in data["stages"]:
            if stage["id"] not in affected and any(dep in affected for dep in stage["depends_on"]):
                affected.add(stage["id"])
                changed = True
    return affected


def invalidate_from(data: dict[str, Any], root_id: str, reason: str) -> list[str]:
    find_stage(data, root_id)
    affected = dependent_stage_ids(data, root_id)
    changed: list[str] = []
    for stage in data["stages"]:
        if stage["id"] not in affected or stage["status"] == "planned":
            continue
        stage["status"] = "needs_rework"
        stage["history"].append({"state": "needs_rework", "at": now(), "reason": reason})
        changed.append(stage["id"])
    update_active_stage(data)
    return changed


def add_stage(
    data: dict[str, Any], stage_id: str, title: str, dependencies: list[str], before: str | None
) -> None:
    if not re.fullmatch(r"[0-9A-Za-z][0-9A-Za-z._-]*", stage_id):
        raise SystemExit(f"阶段编号格式无效: {stage_id}")
    if any(stage["id"] == stage_id for stage in data["stages"]):
        raise SystemExit(f"阶段已经存在: {stage_id}")
    for dependency in dependencies:
        find_stage(data, dependency)
    new_stage = {
        "id": stage_id,
        "title": title,
        "depends_on": dependencies,
        "status": "planned",
        "current_script": None,
        "evidence_type": None,
        "history": [{"state": "planned", "at": now(), "reason": "dynamic stage added"}],
    }
    if before:
        for index, stage in enumerate(data["stages"]):
            if stage["id"] == before:
                data["stages"].insert(index, new_stage)
                break
        else:
            raise SystemExit(f"--before 指定的阶段不存在: {before}")
    else:
        data["stages"].append(new_stage)
    update_active_stage(data)


def print_status(data: dict[str, Any]) -> None:
    print(f"项目: {data['name']} ({data['project_id']})")
    print(f"模式: {data['mode']}  基线: {data['baseline']['version']} / {data['baseline']['status']}")
    print(f"项目状态: {data['result_state']}  当前阶段: {data.get('active_stage_id') or '-'}")
    print(f"规则计划: {data.get('active_rule_plan') or '-'}")
    print("阶段:")
    for stage in data["stages"]:
        script = stage.get("current_script") or "-"
        print(f"  {stage['id']:<20} {stage['status']:<22} {script}")
    if data["risks"]:
        print(f"未关闭风险: {sum(1 for risk in data['risks'] if risk['status'] == 'open')}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init")
    init.add_argument("project_dir", type=Path)
    init.add_argument("--name", required=True)
    init.add_argument("--mode", choices=("simple", "staged"), required=True)

    status = sub.add_parser("status")
    status.add_argument("project_dir", type=Path)

    baseline = sub.add_parser("confirm-baseline")
    baseline.add_argument("project_dir", type=Path)
    baseline.add_argument("--by", default="user")

    transition = sub.add_parser("transition")
    transition.add_argument("project_dir", type=Path)
    transition.add_argument("stage_id")
    transition.add_argument("state", choices=sorted(STAGE_STATES))
    transition.add_argument("--reason")
    transition.add_argument("--evidence-type", choices=("user_attestation", "runtime_evidence"))
    transition.add_argument("--script")

    invalidate = sub.add_parser("invalidate")
    invalidate.add_argument("project_dir", type=Path)
    invalidate.add_argument("--from-stage", required=True)
    invalidate.add_argument("--reason", required=True)

    add = sub.add_parser("add-stage")
    add.add_argument("project_dir", type=Path)
    add.add_argument("--id", required=True)
    add.add_argument("--title", required=True)
    add.add_argument("--depends-on", nargs="*", default=[])
    add.add_argument("--before")

    result = sub.add_parser("set-result")
    result.add_argument("project_dir", type=Path)
    result.add_argument("state", choices=sorted(RESULT_STATES - {"planning"}))

    args = parser.parse_args()

    if args.command == "init":
        project_dir = create_project(args.project_dir, args.name, args.mode)
        print(f"已创建项目: {project_dir}")
        return 0

    project_dir, data = load_project(args.project_dir)

    if args.command == "status":
        print_status(data)
        return 0
    if args.command == "confirm-baseline":
        if data["baseline"]["status"] == "confirmed":
            raise SystemExit("基线已经确认；变更时应先执行影响分析和 invalidate。")
        version_number = int(str(data["baseline"]["version"]).lstrip("v") or 0) + 1
        target_version = f"v{version_number}"
        active_rule_plan, rule_warnings = validate_and_version_rule_plan(project_dir, data, target_version)
        data["baseline"] = {
            "version": target_version,
            "status": "confirmed",
            "confirmed_by": args.by,
            "confirmed_at": now(),
        }
        data["active_rule_plan"] = active_rule_plan
        update_active_stage(data)
        save_project(project_dir, data)
        print(f"已确认基线 {data['baseline']['version']}；当前阶段: {data['active_stage_id']}")
        if rule_warnings:
            print("规则计划警告:")
            for warning in rule_warnings:
                print(f"  - {warning}")
        return 0
    if args.command == "transition":
        transition_stage(data, args.stage_id, args.state, args.reason, args.evidence_type, args.script)
        save_project(project_dir, data)
        print(f"{args.stage_id}: {args.state}; 当前阶段: {data.get('active_stage_id') or '-'}")
        return 0
    if args.command == "invalidate":
        changed = invalidate_from(data, args.from_stage, args.reason)
        save_project(project_dir, data)
        print("需要返工的阶段: " + (", ".join(changed) if changed else "无已执行阶段"))
        return 0
    if args.command == "add-stage":
        add_stage(data, args.id, args.title, args.depends_on, args.before)
        save_project(project_dir, data)
        print(f"已新增阶段: {args.id} ({args.title})")
        return 0
    if args.command == "set-result":
        if args.state == "verified":
            bad = [stage["id"] for stage in data["stages"] if stage["status"] not in {"passed", "skipped"}]
            open_risks = [risk["id"] for risk in data["risks"] if risk["status"] == "open"]
            if bad or open_risks:
                raise SystemExit(f"不能标记 verified；未正常通过阶段={bad}，开放风险={open_risks}")
        if args.state == "completed_with_risks" and not data["risks"]:
            raise SystemExit("没有记录风险，不能标记 completed_with_risks。")
        data["result_state"] = args.state
        save_project(project_dir, data)
        print(f"项目状态已更新为: {args.state}")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
