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

## 3. Build the stage dependency plan

Use this fixed skeleton and skip or split stages according to the topology:

1. planning baseline
2. access layer
3. aggregation layer
4. core layer and backbone routing
5. independent routing areas or service branches
6. network services and exit
7. security policy
8. end-to-end acceptance

Use a network layer or independent fault domain as the normal gate size. Do not stop after every small command group. Execute serially by default; identify safe parallel branches and let the user choose whether to parallelize them.

Define positive and negative functional assertions before generating each stage script.

## 4. Generate one TXT per stage

Read [vrp-patterns.md](references/vrp-patterns.md). Generate complete Huawei VRP command forms from the confirmed baseline. Use the model for command generation; do not make an unproven template renderer a dependency.

For each stage:

- generate only that stage's incremental commands
- place all devices in one versioned TXT file
- order device sections by recommended execution order
- place verification sections at the end of the same file
- omit `save`
- keep host and server addressing in `planning/终端与服务器地址规划.txt`
- write full scripts to files and show only summaries and links in chat

Run `scripts/validate_stage_script.py` before delivery. Automatically repair only mechanical representation errors. Ask before changing IPs, VLANs, ports, areas, Router IDs, next hops, policies, links, or any confirmed design value.

## 5. Apply the stage gate

Read [verification-rules.md](references/verification-rules.md). Use minimum sufficient acceptance commands during normal execution; add diagnostic commands only after failure.

Allow two gate paths:

- explicit user self-verification -> `passed` with `user_attestation`
- pasted output or screenshot -> extract facts, evaluate assertions, and record `runtime_evidence`

Use `scripts/evaluate_gate.py` for explicit attestations or structured assertion results. Let deterministic parsing decide clear results; use model reasoning only for ambiguous or conflicting evidence.

When a gate fails, notify the user, explain downstream impact, and let the user choose repair or forced continuation. Record forced continuation as `forced_pass`, never as normal success. Do not advance automatically on ambiguity.

After a normal pass, generate the next stage automatically. Pause on failure, forced continuation, baseline change, destructive work, or user request.

## 6. Handle errors and rework

Do not generate command-level rollback scripts. When a stage is partially applied, fails, or needs rework:

1. identify the smallest affected device set
2. explain the impact
3. ask whether the user wants to reset those devices
4. let the user perform reset and configuration clearing
5. regenerate the affected devices from the persisted cumulative project state

Suggest a full-layer or full-network reset only when dependencies cannot be isolated. Never reset or clear a device automatically.

## 7. Complete and assemble

After all stage gates, generate `98-全网验收.txt` from the confirmed project requirements. Cover every required reachability, isolation, routing, service, redundancy, and forced-risk retest.

Use `scripts/assemble_stage_scripts.py` only at project completion or on user request to build `99-全网最终完整配置.txt`. Assemble device blocks deterministically in stage order; never semantically deduplicate commands.

Use these project result states:

- `script_ready`: scripts generated and statically checked
- `implemented`: user says scripts were applied
- `verified`: every required stage and final acceptance passed normally
- `completed_with_risks`: work ended with forced passes or unresolved risks

Never claim operational success from static reasoning alone.

## 8. Import a case only when authorized

After configuration and acceptance are complete, ask once whether to save the project as a case. Do not import, update the capability matrix, or delay script delivery without explicit authorization.

For authorized imports, use this quality progression:

`imported -> normalized -> statically_validated -> runtime_validated -> approved`

Only approved cases may serve as trusted evidence. Skip cases that add no new capability.
