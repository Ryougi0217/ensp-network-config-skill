# Resilience and OAM Design Rules

Read these rules for cross-protocol redundancy, failure handling, and operational proof. Match each trigger and boundary before use.

## DR-MSTP-VRRP-002: Align the Layer-2 root with the same-VLAN VRRP master
- Status: validated
- Tags: mstp, vrrp, vlan, redundancy
- Evidence cases: `014-vrrp-mstp-ethtrunk-rip`
- Trigger: A VLAN is carried across redundant gateway switches, both have an SVI/VRRP group, and the requirement asks to avoid unnecessary Layer-2 hairpinning.
- Design goal: Keep the normal Layer-2 forwarding root and the selected gateway on the same device where the topology permits, while preserving a usable backup path.
- Decision logic: Select the desired gateway per VLAN; derive VRRP priority and MSTP root/path choices together; if the topology cannot align them, state the unavoidable detour and verify it explicitly.
- Recompute parameters: Per-VLAN master/backup, real SVI addresses, virtual address, VRID, priority, instance membership, roots, costs, and allowed VLANs.
- Do not copy: Any case's gateway IPs, VRIDs, priorities, device roles, or interface layout.
- Applicability boundary: Ignore when there is no redundant gateway or when MSTP cannot influence the gateway path; upstream failure may still require tracking or routing convergence.
- Common failure: MSTP root and VRRP master split without a design reason, causing stable hairpin traffic or a misleading failover claim.
- Implementation order: Establish Layer-2 reachability; configure SVIs and VRRP; add tracking/routing only when required; verify normal and failure paths.
- Verification method: Correlate per-VLAN MSTP root/path with VRRP state, then test gateway access after convergence and after the requested fault.

## DR-MSTP-VRRP-005: Verify redundancy against the stated fault model
- Status: validated
- Tags: mstp, vrrp, failure, verification
- Evidence cases: `009-mstp-basic`, `010-mstp-expanded`, `013-vrrp-basic`, `014-vrrp-mstp-ethtrunk-rip`
- Trigger: The requirement names link failure, gateway/core failure, recovery, or convergence behavior.
- Design goal: Separate static design plausibility from runtime proof and test every required recovery claim.
- Decision logic: Define positive and negative assertions for normal operation, each requested fault, and post-convergence recovery; collect minimum status and reachability evidence after the user performs the fault.
- Recompute parameters: Current endpoints, gateways, paths, failure targets, convergence-sensitive checks, and evidence locations.
- Do not copy: Historical screenshots, pass/fail conclusions, timing assumptions, or test commands as proof for a new topology.
- Applicability boundary: If runtime execution is unavailable, record an unverified/static result; never upgrade it to operational success.
- Common failure: One normal ping or a parsed script is treated as proof of failover, or a transient convergence loss is mistaken for a permanent failure.
- Implementation order: Verify the Layer-2 base; verify gateway/routing normal state; run user-controlled fault tests; repeat after convergence and record residual risk.
- Verification method: Use protocol status plus reachability for each assertion, distinguish user attestation from runtime evidence, and retain failed/ambiguous gates.
