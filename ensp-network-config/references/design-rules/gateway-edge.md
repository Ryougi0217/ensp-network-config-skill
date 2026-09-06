# Gateway and Edge Design Rules

Read these rules for first-hop gateway, inter-VLAN, and edge-service decisions. Match each trigger and boundary before use.

## DR-MSTP-VRRP-004: Derive a VRRP tuple independently for each VLAN
- Tags: vrrp, vlan, gateway, addressing
- Requires: `gateway-ready`
- Provides: `redundant-gateway-ready`
- Trigger: A VLAN has two or more redundant Layer-3 gateway interfaces using VRRP.
- Design goal: Make the virtual gateway unambiguous, non-conflicting, and intentionally load-shared or failover-capable.
- Decision logic: Start from the current subnet and gateway participants; allocate non-conflicting real SVI and virtual addresses; use one matching VRID per VLAN across its peers; choose priorities to encode the requested master and backup roles.
- Recompute parameters: VLAN/subnet, real SVI addresses, virtual address, VRID, priority, host default gateway, and tracking requirements.
- Applicability boundary: Ignore when there is only one gateway or VRRP is not part of the requirement; do not treat priority alone as upstream-path health.
- Common failure: A virtual address collides with a real address, peers use different VRIDs, or both VLANs accidentally select the same master against the load-sharing requirement.
- Implementation order: Build VLAN/SVI reachability; create the VRRP groups; add tracking or routing convergence when required; then test gateway and upstream reachability.
- Verification method: Inspect VRRP state and address ownership, ping the virtual gateway from each VLAN, and repeat after the specified gateway/uplink fault.

## DR-NAT-001: Bind Easy-IP source scope to the resolved egress path
- Tags: nat, easy-ip, acl, default-route, gateway
- Requires: `internal-routing-ready`, `egress-route-resolved`, `return-path-defined`
- Provides: `outbound-translation-ready`
- Trigger: An edge router must translate selected private source networks toward a public or provider-facing path.
- Design goal: Keep NAT source selection, outbound interface, and return/default routing aligned so the policy expresses the intended edge boundary.
- Decision logic: Derive the private source networks from the current topology and requirements; choose the actual egress interface from the resolved default or service path; bind the source-matching policy to that interface; verify that the return path and any negative inbound expectation are separately stated.
- Recompute parameters: Private source prefixes, ACL match scope and order, egress interface or dialer, default-route next hop, public-side network, and positive/negative test endpoints.
- Applicability boundary: Reassess when there are multiple exits, policy-based routing, stateful security policies, static NAT requirements, or when the platform's Easy-IP behavior is unconfirmed.
- Common failure: NAT is attached to an internal or inactive interface, the ACL omits a required private prefix, the default route exits elsewhere, or a positive translation test is mistaken for proof of inbound isolation.
- Implementation order: Confirm internal routing; confirm the public edge and return path; define source scope; apply NAT to the resolved egress; then test positive internal-to-public reachability and the explicitly required negative direction.
- Verification method: Check ACL scope, NAT binding, route/default state and translation evidence, then execute the required positive and negative reachability assertions. Static structure or attested intent alone does not prove runtime translation.

## DR-NAT-002: Treat multi-mode NAT exercises as ordered transitions with per-phase proof
- Tags: nat, static-nat, outbound, easy-ip, nat-server, phase-transition
- Requires: `egress-route-resolved`, `return-path-defined`
- Provides: `nat-transition-ready`
- Trigger: A source material demonstrates static NAT, address-group no-PAT, Easy-IP, or NAT Server in sequential phases.
- Design goal: Keep mutually exclusive test phases reversible and prevent a phase-specific result from being attributed to a different final state.
- Decision logic: Record the active phase and its route/source/service prerequisites; remove or update the prior mode before enabling the next; verify the NAT table and the required positive/negative result for that phase; treat FTP or other ALG behavior as a separate service claim.
- Recompute parameters: Inside/source scope, global address or pool, outside interface, ACL, PAT/no-PAT state, transition/cleanup command, service mapping, return route, and phase-specific assertions.
- Applicability boundary: Do not claim all phases are simultaneously active or operationally successful until each required phase has separate runtime translation and reachability evidence.
- Common failure: A stale no-PAT entry remains after Easy-IP transition, a wrong global address is not tested negatively, or NAT Server reachability is claimed from static configuration alone.
- Implementation order: Establish routing; configure one phase; inspect translation and results; cleanly transition; repeat for the next phase; restore or document final state.
- Verification method: Capture NAT table/translation state and separate positive/negative reachability for every phase and service.

## DR-GW-002: Gate inter-VLAN reachability on transport and gateway alignment
- Tags: gateway, inter-vlan, vlan, trunk, verification
- Requires: `layer2-transport-ready`, `vlan-roles-defined`
- Provides: `gateway-ready`
- Trigger: A staged experiment carries multiple VLANs from access ports over a trunk to VLANIF gateways.
- Design goal: Keep access membership, trunk carriage, VLANIF existence, endpoint gateways, and cross-VLAN reachability as separate gates.
- Decision logic: Derive endpoint VLANs and access bindings; confirm every transport segment carries the required VLANs; confirm the gateway SVI and endpoint default gateway; then test each gateway and cross-VLAN path.
- Recompute parameters: VLAN IDs, access/trunk ports, allowed VLANs, VLANIF identifiers, gateway addresses, endpoint addresses, and positive/negative path assertions.
- Applicability boundary: Use this as a planning and verification guardrail; without a clean topology export or independent rerun, do not claim end-to-end runtime reproduction, and a successful ping does not prove every transport segment.
- Common failure: A client is in the right VLAN but the trunk or SVI is absent, or a source-run result is treated as a clean independent reproduction.
- Implementation order: Normalize endpoints; validate access; validate trunk; validate VLANIF/direct routes; then execute gateway and cross-VLAN tests.
- Verification method: Correlate VLAN/trunk state with gateway ARP/direct routes and endpoint results.

## DR-GW-003: Separate VRRP role transitions from failure and recovery claims
- Tags: vrrp, gateway, failover, recovery, verification
- Requires: `redundant-gateway-ready`
- Provides: `gateway-failover-plan-ready`, `fault-test-plan-ready`
- Trigger: A VRRP experiment changes priority or reports a new Master and also requires gateway failure/recovery.
- Design goal: Keep role state, upstream path selection, actual fault execution, and recovery timing as distinct claims.
- Decision logic: Record initial Master/Backup and paths; identify whether the transition came from priority, interface loss, or tracking; execute the stated fault; capture post-convergence role/path; restore and measure the required recovery window.
- Recompute parameters: VRID, virtual IP, real SVI addresses, priorities, uplinks, fault target, convergence wait, and path assertions.
- Applicability boundary: Do not claim the named fault or recovery until both are executed; priority change alone cannot satisfy a physical-failure requirement.
- Common failure: A manual priority change is labeled failover, or a new Master state is treated as proof of upstream reachability and recovery.
- Implementation order: Establish normal gateway/path; record baseline; perform the requested fault; verify state and reachability; restore and measure recovery.
- Verification method: Use VRRP state, client path output, fault logs, and timed recovery evidence as separate records.
