# Resilience and OAM Design Rules

Read these rules for cross-protocol redundancy, failure handling, and operational proof. Match each trigger and boundary before use.

## DR-MSTP-VRRP-002: Align the Layer-2 root with the same-VLAN VRRP master
- Status: candidate
- Tags: mstp, vrrp, vlan, redundancy
- Evidence cases: `014-vrrp-mstp-ethtrunk-rip`
- Validation basis: One approved integrated case; no blind test in this batch.
- Trigger: A VLAN is carried across redundant gateway switches, both have an SVI/VRRP group, and the requirement asks to avoid unnecessary Layer-2 hairpinning.
- Design goal: Keep the normal Layer-2 forwarding root and the selected gateway on the same device where the topology permits, while preserving a usable backup path.
- Decision logic: Select the desired gateway per VLAN; derive VRRP priority and MSTP root/path choices together; if the topology cannot align them, state the unavoidable detour and verify it explicitly.
- Recompute parameters: Per-VLAN master/backup, real SVI addresses, virtual address, VRID, priority, instance membership, roots, costs, and allowed VLANs.
- Applicability boundary: Ignore when there is no redundant gateway or when MSTP cannot influence the gateway path; upstream failure may still require tracking or routing convergence.
- Common failure: MSTP root and VRRP master split without a design reason, causing stable hairpin traffic or a misleading failover claim.
- Implementation order: Establish Layer-2 reachability; configure SVIs and VRRP; add tracking/routing only when required; verify normal and failure paths.
- Verification method: Correlate per-VLAN MSTP root/path with VRRP state, then test gateway access after convergence and after the requested fault.

## DR-MSTP-VRRP-005: Verify redundancy against the stated fault model
- Status: candidate
- Tags: mstp, vrrp, failure, verification
- Evidence cases: `009-mstp-basic`, `010-mstp-expanded`, `013-vrrp-basic`, `014-vrrp-mstp-ethtrunk-rip`
- Validation basis: Multiple approved normal-state cases expose the evidence boundary, but no approved case executes the requested fault; no blind test in this batch.
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
- Evidence cases: 060-bfd-static-route-tracking-exam, 061-nqa-icmp-exam
- Validation basis: Direct source-rule adoption authorized by the user; cases 060 and 061 contain source-visual BFD route-withdrawal and NQA observations, while independent platform, recovery, and blind-test evidence remain unavailable.
- Trigger: A route or gateway decision is attached to BFD/NQA liveness.
- Design goal: Keep liveness configuration, normal state, fault response, and recovery state observable as separate gates.
- Decision logic: Confirm peer/probe scope and tracked route; capture normal liveness and route presence; execute the specified fault; capture liveness loss and route withdrawal; restore and capture reinstallation or document platform behavior.
- Recompute parameters: Probe/session name, source/destination, timers, tracked prefix, next hop, fault target, withdrawal expectation, and recovery window.
- Applicability boundary: Confirm target VRP/simulator support before generating executable commands, and do not claim recovery without post-restore evidence; a successful NQA sample alone is not a service-level objective.
- Common failure: The session is Up but not attached to the intended route, a route withdrawal is asserted without a fault, or recovery is assumed from a normal-state result.
- Implementation order: Establish base reachability; configure liveness; verify normal state; execute the fault; verify withdrawal; restore and verify recovery.
- Verification method: Correlate session/probe state with route-table presence across normal, fault, and restored phases.
