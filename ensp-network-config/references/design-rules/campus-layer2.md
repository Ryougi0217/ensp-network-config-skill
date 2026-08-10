# Campus Layer-2 Design Rules

Read these rules for Layer-2 forwarding, VLAN, and spanning-tree decisions. Match each trigger and boundary before use.

## DR-MSTP-VRRP-001: Group MSTP instances by business forwarding intent
- Status: validated
- Tags: mstp, vlan, load-sharing
- Evidence level: validated design constraint; require current-project runtime evidence for operational claims.
- Requires: `layer2-transport-ready`, `loop-domain-defined`
- Provides: `layer2-path-plan-ready`
- Trigger: Multiple VLANs share a Layer-2 loop domain and the requirements distinguish their normal forwarding paths or gateway ownership.
- Design goal: Keep the instance map compact while giving each distinct forwarding intent an independently selectable root/path.
- Decision logic: Group VLANs that have the same required forwarding behavior; choose an instance root and path from the current topology; tune costs only when the topology needs path steering. Do not assume one instance per VLAN.
- Recompute parameters: VLAN-to-instance map, instance roots and secondary roles, interface costs, trunk VLAN sets, and endpoint placement.
- Applicability boundary: Ignore this rule when there is no Layer-2 loop or no requirement for distinct forwarding behavior.
- Common failure: A copied map or cost makes one VLAN take an avoidable detour, strands a VLAN, or creates an unintended root.
- Implementation order: Define VLANs and trunks; make the MST region consistent; select roots and costs; then verify per-instance paths.
- Verification method: Check region/map consistency, root roles, per-instance forwarding state, and same-VLAN reachability with runtime evidence.

## DR-MSTP-VRRP-003: Treat MST region identity as a domain-wide invariant
- Status: validated
- Tags: mstp, region, vlan, consistency
- Evidence level: validated design constraint; require current-project runtime evidence for operational claims.
- Requires: `vlan-roles-defined`, `loop-domain-defined`
- Provides: `mst-region-ready`
- Trigger: Two or more switches participate in the same MSTP region.
- Design goal: Ensure every participating switch computes the same region and instance topology rather than accidentally creating region boundaries.
- Decision logic: Define one project-specific region identity and VLAN map, apply it to every intended member, and compare the resulting state before selecting roots or costs.
- Recompute parameters: Region name, revision, participating switches, VLAN set, instance map, and any topology-specific root/cost choices.
- Applicability boundary: Ignore when MSTP is not used or when the device is intentionally outside the region.
- Common failure: One member differs in name, revision, or mapping; the resulting boundary or inconsistent instance view invalidates path reasoning.
- Implementation order: Define the region; apply and activate the common map on all members; only then tune roots/costs and enable dependent gateway behavior.
- Verification method: Inspect region digest/membership and instance maps on representative and boundary switches, then confirm runtime root/path state.

## DR-L2-001: Define access VLAN roles and trunk transport before spanning-tree selection
- Status: validated
- Tags: vlan, access, trunk, stp, mstp, layer2
- Evidence level: validated design constraint; require current-project runtime evidence for operational claims.
- Requires: `interface-map-confirmed`, `vlan-roles-defined`
- Provides: `layer2-transport-ready`
- Trigger: Endpoints in one or more VLANs must cross multiple switches or redundant Layer-2 links.
- Design goal: Make the VLAN transport domain complete and explicit before using STP/MSTP to reason about loops and forwarding paths.
- Decision logic: Derive endpoint access membership from the requirement; identify every inter-switch transport link; carry the required VLAN set across each intended path, including the logical aggregation interface when present; then select STP/MSTP roots and paths.
- Recompute parameters: Endpoint VLAN membership, access/native/PVID behavior, trunk allowed VLANs, aggregation membership, inter-switch graph, and the VLAN-to-instance map.
- Applicability boundary: Reassess when routing separates the domains, when a VLAN is intentionally local, or when a link is not part of the Layer-2 forwarding path.
- Common failure: A required VLAN is absent from a trunk, an access PVID is wrong, an aggregation member is inconsistent, or STP path conclusions are drawn from an incomplete transport graph.
- Implementation order: Confirm endpoints and VLANs; configure access and transport; verify the allowed set and aggregation; configure STP/MSTP; then verify protocol state and same-VLAN reachability.
- Verification method: Check VLAN/access/trunk/aggregation structure, inspect STP/MSTP state, and test required same-VLAN positive results. Add negative isolation checks only where the requirement asks for isolation.

## DR-HYBRID-001: Use Hybrid PVID and untagged membership to separate subordinate VLANs
- Status: validated
- Tags: vlan, hybrid, pvid, isolation, inter-vlan
- Evidence level: validated design constraint; require current-project runtime evidence for operational claims.
- Requires: `interface-map-confirmed`, `vlan-roles-defined`
- Provides: `layer2-isolation-ready`
- Trigger: Multiple endpoint-facing VLANs must remain isolated while a parent or routed VLAN must cross an upstream Hybrid/Trunk boundary.
- Design goal: Preserve the required child/subordinate isolation while carrying only the intended parent and routed VLAN semantics upstream.
- Decision logic: Assign each endpoint-facing port its child-VLAN PVID and untagged membership in the parent plus that child. When the requirement explicitly selects parent/child fan-in, set the local fan-in uplink PVID to the parent and make the parent plus mapped children untagged there; place the peer-facing port in the parent VLAN; carry only the parent VLAN farther upstream; create the Layer-3 gateway only on the parent. Derive every port from the current topology.
- Recompute parameters: Parent-to-child VLAN map, endpoint and fan-in ports, per-port PVID, tagged/untagged sets, conversion boundary, parent-only upstream transport, parent VLANIF/gateway, endpoint subnet, and isolation assertions.
- Applicability boundary: Use parent/child fan-in only when child VLANs are local Layer-2 isolation domains that intentionally share one parent subnet and gateway. Do not treat it as a generic replacement for Trunk, MUX VLAN, Super-VLAN, or policy isolation; stop when platform Hybrid semantics or the bidirectional return behavior is unconfirmed.
- Common failure: A child receives its own VLANIF, a child is carried beyond the conversion boundary, the fan-in or peer PVID is wrong, return traffic cannot reach the child-facing port, or the shared parent path leaks connectivity between children.
- Implementation order: Define parent/child roles and the conversion boundary; configure child-facing Hybrid ports; configure the local fan-in Hybrid port; configure the peer as parent access and the upstream as parent-only transport; configure the parent gateway; then verify both directions and isolation.
- Verification method: Inspect PVID and untagged membership at both sides of the conversion boundary, confirm that child VLANs remain local and only the parent reaches the gateway, then test gateway access, return traffic, same-parent child isolation, ARP, and representative unicast/broadcast behavior.

## DR-MUX-001: Model MUX VLAN roles as an explicit access policy
- Status: candidate
- Tags: mux-vlan, principal, group, separate, isolation
- Evidence level: candidate; exclude from normal projects until independently validated.
- Requires: `interface-map-confirmed`, `vlan-roles-defined`
- Provides: `layer2-isolation-ready`
- Trigger: A Layer-2 design requires a principal service endpoint, group-member communication, and separate-member isolation in one broadcast domain.
- Design goal: Encode the intended principal/group/separate relationship without confusing shared Layer-2 adjacency with permitted application reachability.
- Decision logic: Choose one principal role and the group/separate roles from the requirement; apply the same role map across participating switches; enable MUX behavior on the intended access ports; carry all required roles across the inter-switch transport.
- Recompute parameters: Principal/group/separate VLAN roles, access-port membership, participating switches, trunk VLAN set, and positive/negative endpoint assertions.
- Applicability boundary: Do not infer MUX semantics from a title alone; stop when the platform support or the principal/group behavior is unclear.
- Common failure: Role definitions differ across switches, a separate port is treated as a group port, or a source description conflicts with the platform's MUX behavior.
- Implementation order: Confirm the role policy; define the common MUX map; configure access ports; configure transport; verify group, principal, and separate positive/negative results.
- Verification method: Check role consistency and port enablement, then collect the complete required positive and negative reachability set before promoting this candidate rule.

## DR-STP-001: Derive a single-tree forwarding path from the graph and cost intent
- Status: candidate
- Tags: stp, root-bridge, path-selection, cost, vlan
- Evidence level: candidate; exclude from normal projects until independently validated.
- Requires: `layer2-transport-ready`, `loop-domain-defined`
- Provides: `layer2-path-plan-ready`
- Trigger: A Layer-2 loop must use a specified root bridge or engineered forwarding path under classic STP.
- Design goal: Make the root and cost plan explainable from the topology instead of copying cost values or assuming the shortest path is selected.
- Decision logic: Select the root from the requirement and graph; compare candidate paths; apply costs only where needed to make the requested path win; keep trunk transport complete; verify the actual blocked/forwarding state.
- Recompute parameters: Root priority, path costs, VLAN transport, endpoint access placement, and the expected blocked/forwarding ports.
- Applicability boundary: Reassess for RSTP/MSTP, per-instance path requirements, unequal link semantics, or missing runtime status evidence.
- Common failure: The root is not the intended device, the cost plan does not produce the requested path, or a static path diagram is treated as proof of runtime state.
- Implementation order: Confirm graph and VLANs; configure root and costs; verify trunk/access structure; inspect STP state; test same-VLAN reachability and the requested negative/failure assertions.
- Verification method: Correlate root ID, port roles, forwarding/blocking state, and reachability; retain pending runtime gates when status output is missing.

## DR-LACP-001: Choose one aggregation profile and prove member-state recovery
- Status: validated
- Tags: eth-trunk, lacp, link-aggregation, failure, vlan
- Evidence level: source-derived design constraint; confirm target-platform support and runtime behavior.
- Requires: `interface-map-confirmed`, `parallel-links-confirmed`
- Provides: `aggregation-ready`, `layer2-transport-ready`
- Trigger: Parallel Layer-2 links must be represented by one logical aggregation and remain usable after a member failure.
- Design goal: Keep aggregation mode, member selection, active-link limits, and failure recovery as one explicit profile rather than merging alternative configurations.
- Decision logic: Select manual or LACP mode from the requirement. When the requirement names only Eth-Trunk and the target platform's manual default is confirmed, keep the manual profile and omit `mode lacp-static`; never infer LACP from an unrelated example. Remove prior membership before changing profiles; derive eligible members from the current parallel-link topology; set limits or priorities only when required; inspect the logical trunk and execute the requested member-failure test.
- Recompute parameters: Aggregation mode, logical interface, physical members, VLAN transport, active-member limit, priorities, failure target, and recovery assertions.
- Applicability boundary: Do not combine manual and LACP profiles in one final state. Configure `mode lacp-static` only when LACP negotiation is explicitly required and supported; do not claim active/standby selection or recovery until runtime member and endpoint evidence exists.
- Common failure: A member remains bound to a previous profile, the two ends disagree, a standby member is called active without state output, or failure recovery is inferred from configuration text.
- Implementation order: Confirm parallel links; choose one profile; clear prior membership; configure the logical trunk and transport; inspect members; then execute and verify failure/recovery.
- Verification method: Correlate logical trunk state, active/standby members, VLAN forwarding, endpoint reachability, and post-failure recovery.

## DR-RSTP-001: Treat fast convergence and edge protection as separate runtime claims
- Status: candidate
- Tags: rstp, convergence, edge-port, bpdu-protection, loop-protection
- Evidence level: candidate; exclude from normal projects until independently validated.
- Requires: `layer2-transport-ready`, `loop-domain-defined`
- Provides: `layer2-path-plan-ready`, `fault-test-plan-ready`
- Trigger: A design uses RSTP root roles, a controlled link failure, and edge/protection features.
- Design goal: Verify root selection and convergence without turning inferred user-port or upstream-protection contexts into fixed configuration.
- Decision logic: Establish the RSTP mode and root roles; select a topology-aligned failure target; inspect port roles before and after the failure; resolve edge, BPDU-protection, and loop-protection targets from the actual topology; then test each protection effect independently.
- Recompute parameters: Root/secondary roles, failure link, edge-port candidates, BPDU-protection scope, loop-protection scope, and recovery assertions.
- Applicability boundary: Candidate while runtime convergence and exact protection contexts are missing; do not use this rule to generalize classic STP or MSTP behavior.
- Common failure: A topology label is treated as a confirmed interface context, a fast transition is claimed without before/after state, or protection is enabled on an inferred non-edge port.
- Implementation order: Confirm topology and device roles; configure RSTP roots; inspect baseline; execute one controlled failure; inspect convergence; then validate each protection target.
- Verification method: Use `display stp brief` or equivalent before/after output and separate edge/BPDU/loop-protection status and effect evidence.
