# Rule flow

Use this workflow for multi-domain, redundant, or service-dependent projects. Keep simple projects on the same interface with a minimal rule plan.

The reusable rules live in `references/design-rules/*.md`. A project rule plan references their stable IDs and records project-specific selection, scope, dependencies, and evidence. Keep topology values in `topology.json` and planning files, assertions in validation artifacts, and rule bodies in the catalogs.

## Contents

1. Build the decision chain
2. Select and compose rules
3. Project rule plan
4. Stage context
5. State and evidence
6. Context control
7. Failure and rework
8. Commands

## 1. Build the decision chain

Build one project decision chain from confirmed outcomes, topology facts, and user-mandated protocols. Do not return a flat rule list or generate commands directly from catalog discovery.

The decision chain must state:

- selected rules and their scoped instances
- requirement-driven feature profiles and the instances that use them
- capability dependencies and selected exclusive profiles
- parameters that must be recomputed in planning
- assertion references and required evidence
- conflicts, unsupported branches, and requirements without a matching rule

Store the complete graph in `planning/rule-plan-vN.yaml`. Keep each rule body in its catalog and reference it by ID.

## 2. Select and compose rules

Do not scan or load every rule body.

1. Normalize requirements and topology into tags, hard protocol constraints, scope references, and required outcomes.
2. Run `rule_flow.py query` against the rule index.
3. Select rules whose triggers and applicability boundaries match the confirmed project.
4. If no rule matches, mark that requirement for confirmed protocol reasoning and stronger verification instead of inventing a catalog rule.
5. Treat scenario descriptions as search seeds, not mandatory templates.
6. Load full rule bodies only for the current stage with `rule_flow.py context`.

Apply this precedence when rules conflict:

1. confirmed business requirements and topology facts
2. target platform capability
3. security and non-destructive constraints
4. the more specific matching rule
5. the broader matching rule

Select among several providers of one capability by explicit user constraint, existing network method, platform support, minimum sufficient complexity, verification/maintenance cost, then change size. Ask only when remaining choices materially change the design.

For each applied protocol instance, derive the minimum sufficient feature set:

1. the confirmed outcomes it must provide
2. the base and dependency features required to provide those outcomes
3. optional features explicitly required by the user, an approved baseline, or an existing peer
4. supported but unrequested features that must remain omitted

Protocol completeness means that items 1-3 form a working dependency chain; it does not mean enabling every supported feature. If an omitted option creates a material conflict with a confirmed outcome, record `needs_confirmation` rather than adding it silently.

Each rule declares `Requires` and `Provides` tokens from [rule-capabilities.json](rule-capabilities.json). Instantiate a rule with scope references so the same rule can be applied independently to multiple VLANs, paths, or services.

Use choice groups for mutually exclusive profiles. Select one value per group, scope, and phase. Keep sequential configuration phases separate.

## 3. Project rule plan

Use this compact project-plan shape:

```yaml
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
feature_profiles:
  - id: feature:nat:branch-egress
    protocol: nat
    scope_ref: edge:branch-egress
    requirement_refs: [req-internet]
    required_outcomes: [private-sources-reach-public-network]
    features:
      - name: easy-ip-source-translation
        state: required
        basis: confirmed_requirement
        refs: [req-internet]
      - name: nat-server
        state: omitted
        basis: not_requested
        refs: []
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
    feature_profile_refs: [feature:nat:branch-egress]
    requires:
      cap:egress-route:branch: runtime_proven
    provides: [cap:nat:branch]
    assertion_refs: [nat-outbound-positive, nat-inbound-negative]
```

Every confirmed requirement must reference an instance or use `unruled`, `blocked`, `needs_confirmation`, or `platform_unsupported`. An applied instance must reference a feature profile with a matching scope and must not use a profile that still needs confirmation. Plans without `feature_profiles` remain readable for audit, but must be completed before stage execution.

## 4. Stage context

Query the index first, then load full rule bodies only for the current stage. After a stage passes, retain capability and evidence references; do not carry completed rule bodies forward.

The generated stage context carries the current stage's requirements, choice-group selections, feature profiles, capabilities, instances, and rule bodies. Use the feature profile as the command-eligibility list: omitted features must not appear in the configuration.

## 5. State and evidence

Keep project application and validation separate:

- application: `applied`, `skipped`, or `blocked`
- validation: `planned`, `statically_validated`, `passed`, `failed`, or `uncertain`

Use capability maturity `planned`, `statically_ready`, or `runtime_proven`. Record forced continuation as `forced`; never equate it with runtime proof. Planning may use planned providers, but execution must satisfy the downstream instance's declared minimum maturity.

Each applied instance must reference assertions. Let rules define what must be proven; merge assertions at the stage level without erasing distinct claims.

## 6. Context control

Default stage budgets are defined in `rule-capabilities.json`:

- at most 12 full rule bodies
- at most 4 catalogs

Split an oversized stage by network layer or independent business/fault domain. Keep only the current rule plan, current stage context, compact upstream capability results, unresolved conflicts, and required evidence in active context. Never load unrelated catalogs during normal configuration.

## 7. Failure and rework

When an instance fails, block only consumers of capabilities it provides. Continue independent branches. Preserve passed work; never clear devices or generate rollback automatically.

Version the rule plan with the planning baseline. On change, find affected scope references, their rule instances, provided capabilities, and downstream consumers. Mark only that subgraph `needs_rework` and write a new `rule-plan-vN.yaml`.

## 8. Commands

```sh
python scripts/rule_flow.py index
python scripts/rule_flow.py index --check
python scripts/rule_flow.py query --tags vlan mstp vrrp
python scripts/rule_flow.py validate projects/PROJECT/planning/rule-plan-v1.yaml
python scripts/rule_flow.py context projects/PROJECT/planning/rule-plan-v1.yaml --stage 05-services-exit --output projects/PROJECT/planning/context/05-services-exit.md
```

Run the structural validator before baseline confirmation, after every rule-plan change, and before building a stage context. It checks bookkeeping invariants only; it does not establish protocol correctness or runtime success.
