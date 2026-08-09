# Rule flow

Use this workflow for multi-domain, redundant, or service-dependent projects. Keep simple projects on the same interface with a minimal rule plan.

## Contents

1. Interface
2. Two-pass loading
3. Selection and composition
4. Project rule plan
5. State and evidence
6. Context control
7. Failure and rework
8. Commands

## 1. Interface

Build one project decision chain from confirmed business outcomes, topology facts, and user-mandated protocols. Do not return a flat rule list or generate commands directly from catalog discovery.

The decision chain must state:

- applied validated rules and their scoped instances
- capability dependencies and selected exclusive profiles
- parameters that must be recomputed elsewhere in planning
- assertion references and required evidence maturity
- candidate advisories, conflicts, unsupported branches, and unruled requirements

Store the complete graph in `planning/rule-plan-vN.yaml`. Keep topology values in `topology.json` and planning files, assertions in validation artifacts, and full rule bodies in the catalogs.

## 2. Two-pass loading

Do not scan or load every rule body.

1. Normalize requirements and topology into tags, hard protocol constraints, scope references, and required outcomes.
2. Run `rule_flow.py query` against the generated rule index. Search active validated rules first.
3. Search candidates only when validated coverage is missing, a material risk remains, or the user requests evaluation.
4. Treat scenario chains as search seeds, not mandatory templates.
5. Load full rule bodies only for the current stage with `rule_flow.py context`.
6. After a stage passes, retain capability and evidence references; do not carry completed rule bodies forward.

Reserved catalogs are unavailable unless the user explicitly requests that protocol or an evaluation flow. A rule catalog is not a protocol whitelist: mark unmatched work `unruled` and use confirmed evidence plus protocol reasoning with stronger verification.

## 3. Selection and composition

Apply this precedence when rules conflict:

1. confirmed business requirements and topology facts
2. target platform and version capability
3. security and non-destructive constraints
4. the more specific matching validated rule
5. a broader matching validated rule
6. candidate advice

Select among several providers of one capability by explicit user constraint, existing network method, platform support, minimum sufficient complexity, verification/maintenance cost, then change size. Ask only when remaining choices materially change the design.

Each rule declares controlled `Requires` and `Provides` tokens from [rule-capabilities.json](rule-capabilities.json). Do not use rule IDs as fixed dependencies. Instantiate a rule with scope references so the same rule can be applied independently to multiple VLANs, paths, or services.

Use choice groups for mutually exclusive profiles. Select one value per group, scope, and phase. Keep sequential experiment phases separate.

## 4. Project rule plan

Use this compact shape:

```yaml
schema_version: "1.0.0"
baseline_version: v1
mode: staged
requirements:
  - id: req-internet
    handling: rule:nat:branch-egress
choice_groups:
  - id: edge-nat-mode
    group: nat-phase
    scope_ref: edge:branch-egress
    phase: final
    selected: easy-ip
capabilities:
  - id: cap:egress-route:branch
    name: egress-route-resolved
    scope_ref: edge:branch-egress
    provider: route:branch
    maturity: runtime_proven
    evidence_refs: [validation/route-branch.json]
  - id: cap:nat:branch
    name: outbound-translation-ready
    scope_ref: edge:branch-egress
    provider: nat:branch-egress
    maturity: planned
    evidence_refs: []
instances:
  - id: nat:branch-egress
    rule_id: DR-NAT-001
    stage: 05-services-exit
    scope_refs: [edge:branch-egress]
    application_state: applied
    validation_state: planned
    reason_code: trigger-matched
    requires:
      cap:egress-route:branch: runtime_proven
    provides: [cap:nat:branch]
    assertion_refs: [nat-outbound-positive, nat-inbound-negative]
```

Write skipped and duplicate decisions to `planning/rule-selection-log.jsonl`; do not keep them in the active plan. Every confirmed requirement must reference an instance or use one of `unruled`, `blocked`, `needs_confirmation`, or `platform_unsupported`.

## 5. State and evidence

Keep three state dimensions separate:

- catalog quality: `validated`, `candidate`, `deprecated`
- project application: `matched`, `applied`, `advisory`, `skipped`, `blocked`
- project validation: `planned`, `statically_validated`, `passed`, `failed`, `uncertain`

Use capability maturity `planned`, `statically_ready`, or `runtime_proven`. Record forced continuation as `forced`; never equate it with runtime proof. Planning may use planned providers, but execution must satisfy the downstream instance's declared minimum maturity.

Only validated rules in active catalogs may be `applied`. Candidates may be `advisory` and may propose a question or evaluation branch; they must not alter the main configuration chain.

Each applied instance must reference assertions. Let rules define what must be proven; merge assertions at the stage level without erasing distinct claims.

## 6. Context control

Default stage budgets are defined in `rule-capabilities.json`:

- at most 12 full rule bodies
- at most 4 catalogs
- at most 3 candidate advisories

Split an oversized stage by network layer or independent business/fault domain. Keep only the current rule plan, current stage context, compact upstream capability results, unresolved conflicts, and required evidence in active context. Never load source-learning reports or case corpora during normal configuration.

## 7. Failure and rework

When an instance fails, block only consumers of capabilities it provides. Continue independent branches. Preserve passed work; never clear devices or generate rollback automatically.

Version the rule plan with the planning baseline. On change, find affected scope references, their rule instances, provided capabilities, and downstream consumers. Mark only that subgraph `needs_rework` and write a new `rule-plan-vN.yaml`.

Project completion may produce a learning candidate, but it must not update or promote catalog rules automatically. Follow the authorized case-learning workflow separately.

## 8. Commands

```powershell
python scripts\rule_flow.py index
python scripts\rule_flow.py index --check
python scripts\rule_flow.py query --tags vlan mstp vrrp
python scripts\rule_flow.py query --tags bgp --include-candidates --include-reserved
python scripts\rule_flow.py validate projects\PROJECT\planning\rule-plan-v1.yaml
python scripts\rule_flow.py context projects\PROJECT\planning\rule-plan-v1.yaml --stage 05-services-exit --output projects\PROJECT\planning\context\05-services-exit.md
```

Run the structural validator before baseline confirmation, after every rule-plan change, and before building a stage context. It checks bookkeeping invariants only; it does not establish protocol correctness or runtime success.
