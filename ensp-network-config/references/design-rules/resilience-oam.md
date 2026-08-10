# Resilience and OAM Design Rules

Read these rules for cross-protocol redundancy, failure handling, and operational proof. Match each trigger and boundary before use.

## DR-MSTP-VRRP-002: Align the Layer-2 root with the same-VLAN VRRP master
- Status: candidate
- Tags: mstp, vrrp, vlan, redundancy
- Evidence level: candidate; exclude from normal projects until independently validated.
- Requires: `layer2-path-plan-ready`, `redundant-gateway-ready`
- Provides: `redundancy-coordination-ready`
- Trigger: A VLAN is carried across redundant gateway switches, both have an SVI/VRRP group, and the requirement asks to avoid unnecessary Layer-2 hairpinning.
- Design goal: Keep the normal Layer-2 forwarding root and the selected gateway on the same device where the topology permits, while preserving a usable backup path.
- Decision logic: Select the desired gateway per VLAN; derive VRRP priority and MSTP root/path choices together; if the topology cannot align them, state the unavoidable detour and verify it explicitly.
- Recompute parameters: Per-VLAN master/backup, real SVI addresses, virtual address, VRID, priority, instance membership, roots, costs, and allowed VLANs.
- Applicability boundary: Ignore when there is no redundant gateway or when MSTP cannot influence the gateway path; upstream failure may still require tracking or routing convergence.
- Common failure: MSTP root and VRRP master split without a design reason, causing stable hairpin traffic or a misleading failover claim.
- Implementation order: Establish Layer-2 reachability; configure SVIs and VRRP; add tracking/routing only when required; verify normal and failure paths.
- Verification method: Correlate per-VLAN MSTP root/path with VRRP state, then test gateway access after convergence and after the requested fault.

## DR-MSTP-VRRP-005: Verify redundancy against the stated fault model
- Status: deprecated
- Tags: mstp, vrrp, failure, verification
- Evidence level: deprecated; generic fault-model behavior is owned by verification-rules.md.
- Requires: `topology-baseline-confirmed`
- Provides: `fault-test-plan-ready`, `recovery-test-plan-ready`
- Trigger: The requirement names link failure, gateway/core failure, recovery, or convergence behavior.
- Design goal: Separate static design plausibility from runtime proof and test every required recovery claim.
- Decision logic: Define positive and negative assertions for normal operation, each requested fault, and post-convergence recovery; collect minimum status and reachability evidence after the user performs the fault.
- Recompute parameters: Current endpoints, gateways, paths, failure targets, convergence-sensitive checks, and evidence locations.
- Applicability boundary: If runtime execution is unavailable, record an unverified/static result; never upgrade it to operational success.
- Common failure: One normal ping or a parsed script is treated as proof of failover, or a transient convergence loss is mistaken for a permanent failure.
- Implementation order: Verify the Layer-2 base; verify gateway/routing normal state; run user-controlled fault tests; repeat after convergence and record residual risk.
- Verification method: Use protocol status plus reachability for each assertion, distinguish user attestation from runtime evidence, and retain failed/ambiguous gates.

## DR-OAM-001: Require a three-state proof for liveness-tracked routes
- Status: validated
- Tags: bfd, nqa, static-route, tracking, failure, recovery
- Evidence level: source-derived design constraint; confirm target-platform support and runtime behavior.
- Requires: `layer3-adjacency-ready`, `internal-routing-ready`
- Provides: `liveness-tracking-ready`, `fault-test-plan-ready`, `recovery-test-plan-ready`
- Trigger: A route or gateway decision is attached to BFD/NQA liveness.
- Design goal: Keep liveness configuration, normal state, fault response, and recovery state observable as separate gates.
- Decision logic: Derive the protected health condition from the real forwarding topology. Create a session for every local upstream path whose loss must affect the route or gateway decision; do not substitute a peer or aggregation interconnect for upstream reachability. Attach each session only to the intended route or active gateway group, choose the decrement/withdrawal behavior from the desired single- and multi-fault outcome, then prove normal, fault, and restored states. Keep platform defaults for timers unless the requirement or verified platform behavior needs explicit values.
- Recompute parameters: Relevant upstream links, probe/session names, source/destination, optional timers, tracked route or gateway groups, priority decrement or withdrawal rule, single/multi-fault targets, and recovery window.
- Applicability boundary: Confirm target VRP/simulator support before generating executable commands, and do not claim recovery without post-restore evidence; a successful NQA sample alone is not a service-level objective.
- Common failure: Only a peer/inter-switch session is monitored while the actual upstream fails, one relevant uplink is omitted, a decrement causes unintended takeover after a non-critical fault, or recovery is assumed from a normal-state result.
- Implementation order: Establish every relevant upstream; configure one liveness session per protected path; attach the sessions to the intended route/gateway decisions; verify normal state; execute each named single or combined fault; restore and verify recovery.
- Verification method: Correlate every session/probe state with route or gateway ownership across normal, each named fault, and restored phases; do not use one session or one Ping as proof for all upstreams.
