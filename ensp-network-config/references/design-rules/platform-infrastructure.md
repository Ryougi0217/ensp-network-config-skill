# Platform Infrastructure Design Rules

Read these rules for hardware-dependent PoE planning and switch stacking changes. They are planning and risk rules, not a model compatibility table or a command cookbook.

## DR-PLAT-001: Confirm PoE hardware capability before port configuration
- Status: validated
- Tags: poe, hardware, power, platform-support
- Evidence cases: none; source-reference only
- Validation basis: Direct source-rule adoption authorized by the user on 2026-08-09 from the Huawei manual `POE配置`; no independent eNSP PoE runtime or target-model confirmation was performed.
- Trigger: A switch is expected to power APs, phones, cameras, or other PoE endpoints.
- Design goal: Prevent a software-looking configuration from masking unsupported switch, power-module, or port hardware.
- Decision logic: Confirm device form factor, model family, installed power capability, software/package support, and endpoint power class; only then plan port-level behavior.
- Recompute parameters: Available device budget, per-port demand, endpoint count, power-module redundancy, reserve, and alarm thresholds.
- Applicability boundary: Recheck every target model, module combination, and VRP/eNSP version; this rule does not establish that a particular simulator image supports PoE.
- Common failure: The port command is accepted but the hardware cannot supply the requested power, or a built-in and pluggable power design is treated as equivalent.
- Implementation order: Confirm hardware and software; inventory endpoints; calculate budget; select port policy; configure; verify power state and alarms.
- Verification method: Inspect hardware/module capability, per-port power state, total/remaining budget, and a controlled shortage or alarm result when the platform permits it.

## DR-PLAT-002: Allocate limited PoE power by business criticality
- Status: validated
- Tags: poe, power-budget, priority, availability
- Evidence cases: none; source-reference only
- Validation basis: Direct source-rule adoption authorized by the user on 2026-08-09 from the Huawei manual PoE priority and power-matching discussion; no independent shortage or recovery test was performed.
- Trigger: Sum of endpoint demand may exceed the usable PoE budget.
- Design goal: Keep critical endpoints powered and make non-critical degradation predictable.
- Decision logic: Classify endpoint criticality from the requirement; calculate peak demand and reserve; map priorities; define the shedding order; then configure and observe the result.
- Recompute parameters: Endpoint demand, concurrency, peak factor, reserve, priority tiers, shedding order, and recovery thresholds.
- Applicability boundary: Priority semantics and overload behavior are device/version dependent; do not claim graceful shedding without a controlled platform test.
- Common failure: A high-priority label is set without a budget calculation, or all ports are treated as equally important.
- Implementation order: Inventory and rank endpoints; calculate; configure priority and alarms; inspect normal state; test shortage/recovery if supported.
- Verification method: Compare configured priority and power consumption with the observed powered/depowered set and alarms.

## DR-STACK-001: Establish stack-member compatibility before cabling
- Status: validated
- Tags: stacking, istack, compatibility, software, hardware
- Evidence cases: none; source-reference only
- Validation basis: Direct source-rule adoption authorized by the user on 2026-08-09 from the Huawei manual stack compatibility and topology guidance; no independent eNSP stack runtime or target-model confirmation was performed.
- Trigger: Multiple switches are to operate as one logical stack.
- Design goal: Avoid building a physically connected but unsupported or unstable stack.
- Decision logic: Verify member model/form factor, software/VRP compatibility, stack ports/cards/cables, supported topology, and member count before selecting ring or chain wiring.
- Recompute parameters: Member set, compatibility matrix, stack link count, ring/chain choice, redundancy, and bandwidth.
- Applicability boundary: This rule does not replace the target platform's compatibility documentation or a pre-change lab test.
- Common failure: Different form factors are mixed, an unsupported cable/card is used, or a two-member chain is assumed to have ring redundancy.
- Implementation order: Confirm support; select topology; map ports/cables; document risks; only then configure and connect.
- Verification method: Check member discovery, stack link state, topology closure, and system role state after startup.

## DR-STACK-002: Plan member IDs, priorities, and roles before enabling stack
- Status: validated
- Tags: stacking, member-id, priority, master, standby
- Evidence cases: none; source-reference only
- Validation basis: Direct source-rule adoption authorized by the user on 2026-08-09 from the Huawei manual stack ID/priority and role planning guidance; no independent runtime or role-election test was performed.
- Trigger: A stack needs predictable master/standby selection and stable management identity.
- Design goal: Make role selection intentional and reduce split-brain or management ambiguity.
- Decision logic: Assign unique member IDs; rank priorities from the operational requirement; define expected master/standby/linecard roles; record the resulting logical interface impact before applying changes.
- Recompute parameters: Member IDs, priority order, role expectation, logical port mapping, system MAC behavior, and startup order.
- Applicability boundary: Role selection can change after failure or reboot; the planned role is not proof of the current runtime role.
- Common failure: Duplicate/default IDs remain, priorities are changed repeatedly, or a member role is inferred from the physical position.
- Implementation order: Back up; define IDs/priority/roles; apply during a maintenance window; reboot in the planned order; inspect the logical stack.
- Verification method: Compare planned and observed IDs, priorities, roles, system MAC, and member interfaces.

## DR-STACK-003: Treat stack cabling and enablement as a high-risk change
- Status: validated
- Tags: stacking, change-safety, reboot, configuration-loss, rollback
- Evidence cases: none; source-reference only
- Validation basis: Direct source-rule adoption authorized by the user on 2026-08-09 from Huawei manual warnings for `stack enable`, slot changes, non-hot-swappable stack cards, power-down, and reboot; no independent recovery test was performed.
- Trigger: Enabling stacking, changing member IDs/priorities, installing stack hardware, or connecting stack cables requires a reboot or power cycle.
- Design goal: Prevent configuration loss, stack split, wrong boot order, and extended outage.
- Decision logic: Capture current configuration and state; confirm recovery media and maintenance window; power down when hardware requires it; apply one planned change set; cable with verified port direction; boot in order; validate before restoring dependent services.
- Recompute parameters: Impacted members, backup scope, outage duration, boot order, cable endpoints, rollback point, and service recovery checks.
- Applicability boundary: Exact data-loss and reboot behavior is platform/version specific; stop when hardware identity or rollback is uncertain.
- Common failure: A card is installed hot, a member is rebooted before peers are ready, or a slot/priority change is applied repeatedly without a saved baseline.
- Implementation order: Backup and inspect; approve window; isolate power/stack change; connect; boot; display stack; verify service and rollback readiness.
- Verification method: Use pre/post configuration hashes or snapshots, stack membership/role/link state, and representative VLAN/uplink/service tests.
