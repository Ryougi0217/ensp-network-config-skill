# Campus Layer-2 Design Rules

Read these rules for Layer-2 forwarding, VLAN, and spanning-tree decisions. Match each trigger and boundary before use.

## DR-MSTP-VRRP-001: Group MSTP instances by business forwarding intent
- Status: validated
- Tags: mstp, vlan, load-sharing
- Evidence cases: `009-mstp-basic`, `010-mstp-expanded`, `014-vrrp-mstp-ethtrunk-rip`
- Trigger: Multiple VLANs share a Layer-2 loop domain and the requirements distinguish their normal forwarding paths or gateway ownership.
- Design goal: Keep the instance map compact while giving each distinct forwarding intent an independently selectable root/path.
- Decision logic: Group VLANs that have the same required forwarding behavior; choose an instance root and path from the current topology; tune costs only when the topology needs path steering. Do not assume one instance per VLAN.
- Recompute parameters: VLAN-to-instance map, instance roots and secondary roles, interface costs, trunk VLAN sets, and endpoint placement.
- Do not copy: The evidence cases' instance numbers, switch IDs, port names, cost values, or forwarding paths.
- Applicability boundary: Ignore this rule when there is no Layer-2 loop or no requirement for distinct forwarding behavior.
- Common failure: A copied map or cost makes one VLAN take an avoidable detour, strands a VLAN, or creates an unintended root.
- Implementation order: Define VLANs and trunks; make the MST region consistent; select roots and costs; then verify per-instance paths.
- Verification method: Check region/map consistency, root roles, per-instance forwarding state, and same-VLAN reachability with runtime evidence.

## DR-MSTP-VRRP-003: Treat MST region identity as a domain-wide invariant
- Status: validated
- Tags: mstp, region, vlan, consistency
- Evidence cases: `009-mstp-basic`, `010-mstp-expanded`, `014-vrrp-mstp-ethtrunk-rip`
- Trigger: Two or more switches participate in the same MSTP region.
- Design goal: Ensure every participating switch computes the same region and instance topology rather than accidentally creating region boundaries.
- Decision logic: Define one project-specific region identity and VLAN map, apply it to every intended member, and compare the resulting state before selecting roots or costs.
- Recompute parameters: Region name, revision, participating switches, VLAN set, instance map, and any topology-specific root/cost choices.
- Do not copy: The evidence cases' region name, revision, VLAN IDs, switch set, or configuration text as fixed values.
- Applicability boundary: Ignore when MSTP is not used or when the device is intentionally outside the region.
- Common failure: One member differs in name, revision, or mapping; the resulting boundary or inconsistent instance view invalidates path reasoning.
- Implementation order: Define the region; apply and activate the common map on all members; only then tune roots/costs and enable dependent gateway behavior.
- Verification method: Inspect region digest/membership and instance maps on representative and boundary switches, then confirm runtime root/path state.
