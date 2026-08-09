---
name: ensp-network-config
description: Analyze Huawei eNSP topology screenshots, project information, requirements, terminal output, and existing VRP configurations; create confirmed network plans; generate dependency-ordered stage TXT scripts for access, aggregation, core, routing, services, exit, and security; validate each stage with user attestation or runtime evidence; and diagnose inconsistencies. Use for eNSP configuration generation, staged implementation, verification, repair, or optional import of a verified lab case.
---

# eNSP Network Config

Treat configuration delivery as the primary workflow. Keep case learning optional and strictly after configuration work.

## Select the mode

- Use **simple mode** for at most three network devices, one main technology, and no meaningful redundancy, dynamic-routing, security, or service dependency. Create one configuration stage and one gate.
- Use **staged mode** when the topology has multiple network layers, redundant links, loops, multi-area routing, ACL/NAT/PPPoE, reliability features, several dependent technologies, or when the user requests staged work.
- For existing configurations, inspect `display current-configuration` before generating changes.
- For a reported failure, diagnose first; modify configuration only when the user requests a fix.

Read [project-workflow.md](references/project-workflow.md) before starting a configuration project. Use `scripts/project_workflow.py` to persist project state instead of relying on chat history.

## 1. Inspect and normalize inputs

Read every supplied screenshot, requirement, project artifact, configuration, and validation result. Prefer evidence in this order:

1. eNSP project data or explicit user confirmation
2. verified current configuration
3. clearly visible screenshot labels
4. model inference

Read [topology-schema.md](references/topology-schema.md) and create one canonical `topology.json`. Record devices, roles, observed interfaces, links, addressing, VLANs, routing domains, confidence, sources, and uncertainties.

Treat clear ports as observed. Propose a non-conflicting planned port only when the device resources are known. Ask the user to confirm every uncertain used port and any possible expansion module. Never configure an unresolved interface.

## 2. Confirm one planning baseline

Obtain required behavior: reachability, isolation, redundancy, routing, services, and security policy. Propose missing non-conflicting values but preserve user-provided values.

For staged mode, persist complete planning data under `planning/` and show only a concise summary plus uncertainties in chat. Confirm the baseline once before generating the first stage. Treat baseline confirmation as authorization to begin.

When the baseline changes, perform impact analysis and ask whether to rework. Do not silently invalidate prior results. If the user declines rework, either keep the old baseline active or record forced continuation with unresolved risk.

When the task involves a covered technology, read [design-rules.md](references/design-rules.md) first and follow its routing table. Load only the catalog or catalogs listed under Active catalogs whose tags match the current task; do not load every catalog, and do not treat catalog names embedded elsewhere as a whitelist. Use matching `validated` rules, then re-derive device roles, interfaces, VLANs, addresses, VRIDs, priorities, costs, and verification from the current topology. Never copy concrete case parameters or configurations. Ignore rules whose triggers or boundaries do not match; on conflict, prioritize confirmed project evidence and report it. Use `candidate` rules only in an explicit evaluation flow, never in normal projects.

## 3. Build the stage dependency plan

Follow the stage skeleton and status model in [project-workflow.md](references/project-workflow.md). Use a network layer or independent fault domain as the normal gate size. Execute serially by default; identify safe parallel branches and let the user choose whether to parallelize them. Define positive and negative functional assertions before generating each stage script.

## 4. Generate one TXT per stage

Read [vrp-patterns.md](references/vrp-patterns.md) and follow the Stage TXT contract and static delivery gate in [project-workflow.md](references/project-workflow.md). Generate complete Huawei VRP command forms from the confirmed baseline; do not make an unproven template renderer a dependency. Write full scripts to versioned files and show only summaries and links in chat.

Run `scripts/validate_stage_script.py` before delivery. Automatically repair only mechanical representation errors. Ask before changing IPs, VLANs, ports, areas, Router IDs, next hops, policies, links, or any confirmed design value.

## 5. Apply the stage gate

Follow the runtime gate in [project-workflow.md](references/project-workflow.md) and the evidence semantics in [verification-rules.md](references/verification-rules.md). Use `scripts/evaluate_gate.py` for explicit attestations or structured assertion results. Let deterministic parsing decide clear results; use model reasoning only for ambiguous or conflicting evidence. Advance automatically only after a normal pass; pause on failure, forced continuation, ambiguity, baseline change, destructive work, or user request.

## 6. Handle errors and rework

Follow Failure, reset, and change handling in [project-workflow.md](references/project-workflow.md). Never generate command-level rollback or reset or clear a device automatically. Regenerate the smallest affected device set from persisted cumulative project state after the user performs any required reset.

## 7. Complete and assemble

Follow Completion and case learning in [project-workflow.md](references/project-workflow.md). Generate `98-全网验收.txt` from confirmed requirements. Use `scripts/assemble_stage_scripts.py` only at project completion or on user request to build `99-全网最终完整配置.txt`; never semantically deduplicate commands. Never claim operational success from static reasoning alone.

## 8. Import a case only when authorized

After configuration and acceptance are complete, ask once whether to save the project as a case. Do not import, update the capability matrix, or delay script delivery without explicit authorization.

For an authorized import, normalize the case to `case.json`, `topology.json`, `steps.yaml`, and `assertions.yaml`, plus every configuration artifact listed by the case. Run `python scripts/validate_case.py CASE_DIR`; it invokes `scripts/parse_vrp_config.py` for supplied VRP configurations. Require a report with `"valid": true` before marking the case `statically_validated`. If PyYAML is unavailable, report the dependency instead of skipping validation.

For authorized imports, use this quality progression:

`imported -> normalized -> statically_validated -> runtime_validated -> approved`

Only approved cases may serve as trusted evidence. Skip cases that add no new capability.
