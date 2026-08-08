#!/usr/bin/env python3
"""Assemble versioned eNSP stage TXT files into one final device-grouped TXT."""

from __future__ import annotations

import argparse
import json
import sys
from collections import OrderedDict
from pathlib import Path

from validate_stage_script import nonempty_lines, parse_stage_text, validate


def project_stage_files(project_dir: Path) -> list[Path]:
    project_path = project_dir.resolve()
    try:
        data = json.loads((project_path / "project.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"无法读取项目状态: {exc}") from exc
    files: list[Path] = []
    for stage in data.get("stages", []):
        if str(stage.get("id", "")).startswith("98-"):
            continue
        current = stage.get("current_script")
        if not current:
            continue
        stage_file = (project_path / current).resolve()
        try:
            stage_file.relative_to(project_path)
        except ValueError as exc:
            raise SystemExit(f"阶段脚本越出项目目录: {current}") from exc
        files.append(stage_file)
    return files


def assemble(files: list[Path], output: Path) -> dict:
    if not files:
        raise SystemExit("没有可拼接的阶段文件。")
    device_blocks: OrderedDict[str, list[list[str]]] = OrderedDict()
    reports: list[dict] = []

    for path in files:
        report = validate(path)
        reports.append(report)
        if not report["valid"]:
            raise SystemExit(f"阶段文件结构无效，停止拼接: {path}\n{json.dumps(report, ensure_ascii=False, indent=2)}")
        parsed = parse_stage_text(path.read_text(encoding="utf-8-sig"))
        for block in parsed["configs"]:
            lines = nonempty_lines(block)
            device_blocks.setdefault(block["device"], []).append(lines)

    output_lines = ["===== eNSP FINAL CONFIGURATION =====", ""]
    for device, chunks in device_blocks.items():
        output_lines.append(f"===== DEVICE: {device} =====")
        for chunk in chunks:
            output_lines.extend(chunk)
            output_lines.append("")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(output_lines).rstrip() + "\n", encoding="utf-8")
    return {
        "output": str(output.resolve()),
        "stage_files": [str(path.resolve()) for path in files],
        "devices": list(device_blocks),
        "device_count": len(device_blocks),
        "semantic_deduplication": False,
        "warnings": [warning for report in reports for warning in report["warnings"]],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--project", type=Path)
    source.add_argument("--files", type=Path, nargs="+")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if args.project:
        project_dir = args.project.resolve()
        files = project_stage_files(project_dir)
        output = args.output or (project_dir / "scripts" / "99-全网最终完整配置.txt")
    else:
        files = [path.resolve() for path in args.files]
        if not args.output:
            raise SystemExit("使用 --files 时必须提供 --output。")
        output = args.output.resolve()

    report = assemble(files, output)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
