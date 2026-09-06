---
name: ensp-network-config
description: Analyze Huawei eNSP topology screenshots, project information, requirements, terminal output, and existing VRP configurations; create confirmed network plans; generate dependency-ordered stage TXT scripts for access, aggregation, core, routing, services, exit, and security; validate each stage with user attestation or runtime evidence; diagnose inconsistencies; and validate a supplied eNSP case when requested.
---

# eNSP Network Config

Use the configuration workflow below. Validate a supplied case only when the user explicitly requests it.

This skill produces planning artifacts, staged VRP scripts, and evidence-gated
decisions. It does not connect to, control, or claim runtime success for eNSP
or network devices; runtime evidence must be supplied by an authorized
operator or an execution environment.

## Select the mode

- Use **simple mode** for at most three network devices, one main technology, and no meaningful redundancy, dynamic-routing, security, or service dependency. Create one configuration stage and one gate.
- Use **staged mode** when the topology has multiple network layers, redundant links, loops, multi-area routing, ACL/NAT/PPPoE, reliability features, several dependent technologies, or when the user requests staged work.
- For existing configurations, inspect `display current-configuration` before generating changes.
- For a reported failure, diagnose first; modify configuration only when the user requests a fix.

Read [project-workflow.md](references/project-workflow.md) before starting a configuration project. Use `scripts/project_workflow.py` to persist project state instead of relying on transient interaction history.

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

For every selected protocol, derive a requirement-driven feature profile before
planning commands. Separate the required outcome, mandatory protocol and
topology dependencies, explicitly requested optional features, and unrequested
features. A complete protocol configuration means the smallest complete
dependency chain that achieves the confirmed outcome, not every feature the
protocol supports. Omit any optional feature that cannot be traced to a
confirmed requirement, topology dependency, existing peer constraint, or
target-platform necessity. For example, do not add OSPF authentication merely
because it is available; add it only when the confirmed security requirement
or peer configuration requires it.

Persist these decisions in the rule plan's `feature_profiles`. Every applied
rule instance must reference the matching profile. Do not enter a stage while
one of its features is `needs_confirmation`; use the generated stage context so
required, selected, and deliberately omitted features remain visible during
command generation.

For staged mode, persist complete planning data under `planning/` and return only a concise summary plus uncertainties in the current interaction. Confirm the baseline once before generating the first stage. Treat baseline confirmation as authorization to begin.

When the baseline changes, perform impact analysis and ask whether to rework. Do not silently invalidate prior results. If the user declines rework, either keep the old baseline active or record forced continuation with unresolved risk.

Use [rule-flow.md](references/rule-flow.md) to build the project decision chain. Normalize requirements and topology into tags, hard protocol constraints, scope references, and required outcomes; query `references/rule-index.json` with `scripts/rule_flow.py` before loading rule bodies.

Treat the Markdown catalogs under `references/design-rules/` as the only reusable rule source. A project rule plan references those rules by stable ID and records project-specific selection, scope, and evidence. Keep project values in the plan and do not copy a rule body into it.

Persist the selected scoped instances, capability dependencies, requirement coverage, choice groups, and assertion references in `planning/rule-plan-vN.yaml`. Run `scripts/rule_flow.py validate` before baseline confirmation. Simple mode uses the same interface with a minimal plan.

Use matching rules to re-derive device roles, interfaces, VLANs, addresses, VRIDs, priorities, costs, and verification from the current topology. Never copy concrete case parameters or configurations. Ignore rules whose triggers or boundaries do not match. Resolve conflicts by the precedence in `rule-flow.md`, and record the decision with a reason code.

## 3. Build the stage dependency plan

Follow the stage skeleton and status model in [project-workflow.md](references/project-workflow.md). Use a network layer or independent fault domain as the normal gate size. Execute serially by default; identify safe parallel branches and let the user choose whether to parallelize them. Define positive and negative functional assertions before generating each stage script.

Before working on a stage, run `scripts/rule_flow.py context` for that stage. Load only the generated context pack, compact upstream capability results, current unresolved conflicts, and current-stage planning data. If the context budget is exceeded, split the stage by network layer or independent business or fault domain.

## 4. Generate one TXT per stage

Read only the matching sections of [vrp-patterns.md](references/vrp-patterns.md) and follow the Stage TXT contract and static delivery gate in [project-workflow.md](references/project-workflow.md). Generate complete Huawei VRP command forms from the confirmed baseline; do not make an unproven template renderer a dependency. Write full scripts to versioned files and return only summaries and links in the current interaction.

Before emitting a protocol feature, trace it to a confirmed requirement or a
mandatory dependency of the selected design. Remove convenience, hardening,
tuning, authentication, encryption, redistribution, failure-detection, and
other optional commands when that trace does not exist. If omitting an
unrequested feature would materially conflict with a confirmed outcome, record
the conflict for decision instead of silently enabling the feature.

Run `scripts/validate_stage_script.py` before delivery. Automatically repair only mechanical representation errors. Ask before changing IPs, VLANs, ports, areas, Router IDs, next hops, policies, links, or any confirmed design value.

Treat unresolved placeholders and unapproved command abbreviations as static errors. Reject `save` unconditionally. Treat reset, reboot or restart, delete, erase, remove, format, clear, rollback, and startup-configuration changes as sensitive commands. Do not create an authorization record merely to satisfy validation: accept one only after the user explicitly authorizes the exact command, device, section, and immutable stage-file hash. Keep authorized maintenance actions separate from normal configuration stages and never assemble them into the final configuration.

## 5. Apply the stage gate

Follow the runtime gate in [project-workflow.md](references/project-workflow.md) and the evidence semantics in [verification-rules.md](references/verification-rules.md). Use `scripts/evaluate_gate.py` for explicit attestations or structured assertion results. Let deterministic parsing decide clear results; use model reasoning only for ambiguous or conflicting evidence. Advance automatically only after a normal pass; pause on failure, forced continuation, ambiguity, baseline change, destructive work, or user request.

## 6. Handle errors and rework

Follow Failure, reset, and change handling in [project-workflow.md](references/project-workflow.md). Never generate command-level rollback or reset or clear a device automatically. If the user explicitly requests a sensitive maintenance command, validate it against the exact authorization record and deliver it separately for manual execution. Regenerate the smallest affected device set from persisted cumulative project state after the user performs any required reset.

## 7. Complete and assemble

Follow Completion in [project-workflow.md](references/project-workflow.md). Generate `98-全网验收.txt` from confirmed requirements. Use `scripts/assemble_stage_scripts.py` only at project completion or on user request to build `99-全网最终完整配置.txt`; never semantically deduplicate commands. Never claim operational success from static reasoning alone.

## 8. Validate a supplied case on request

When the user provides a case for validation, keep it separate from the current configuration project and do not delay script delivery.

Normalize the case to `case.json`, `topology.json`, `steps.yaml`, and `assertions.yaml`, plus every configuration artifact listed by the case. Run `python scripts/validate_case.py CASE_DIR`; it invokes `scripts/parse_vrp_config.py` for supplied VRP configurations. Require a report with `"valid": true` before using the case as project evidence. If PyYAML is unavailable, report the dependency instead of skipping validation.
