# Gateway and Edge Design Rules

Read these rules for first-hop gateway, inter-VLAN, and edge-service decisions. Match each trigger and boundary before use.

## DR-MSTP-VRRP-004: Derive a VRRP tuple independently for each VLAN
- Status: validated
- Tags: vrrp, vlan, gateway, addressing
- Evidence level: validated design constraint; require current-project runtime evidence for operational claims.
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
- Status: validated
- Tags: nat, easy-ip, acl, default-route, gateway
- Evidence level: validated design constraint; require current-project runtime evidence for operational claims.
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

## DR-GW-001: Align access VLAN transport with the selected Layer-3 gateway boundary
- Status: deprecated
- Tags: gateway, inter-vlan, vlanif, router-on-a-stick, trunk
- Evidence level: deprecated; superseded by DR-GW-002.
- Requires: `layer2-transport-ready`, `vlan-roles-defined`
- Provides: `gateway-ready`
- Trigger: Multiple endpoint VLANs must reach one or more Layer-3 gateway interfaces through access and trunk transport.
- Design goal: Make the endpoint VLAN, transport VLAN set, and gateway termination mapping agree before interpreting cross-VLAN reachability.
- Decision logic: Derive access membership and inter-switch VLAN carriage from the endpoint placement; choose VLANIF or 802.1Q subinterfaces from the gateway design; map each VLAN to one gateway boundary and address scope; then verify interface state, direct routes/ARP, and cross-VLAN results.
- Recompute parameters: VLAN roles, access ports, trunk allow sets, gateway termination type, subinterface/VLANIF identifiers, gateway addresses, endpoint addresses, and expected positive/negative paths.
- Applicability boundary: Candidate while endpoint settings and runtime gateway/cross-VLAN evidence are missing; do not assume a method script is a complete deployable configuration.
- Common failure: A VLAN is allowed on one trunk but not the next, a subinterface tag does not match the switch transport, a Vlanif lacks active member ports, or a static gateway annotation is mistaken for runtime reachability.
- Implementation order: Confirm endpoint/VLAN roles; configure access and transport; configure the chosen gateway termination; verify interface/direct-route state; then test cross-VLAN reachability and any required isolation.
- Verification method: Correlate VLAN/access/trunk state, gateway interface state, ARP/direct routes, and endpoint results.

## DR-NAT-002: Treat multi-mode NAT exercises as ordered transitions with per-phase proof
- Status: validated
- Tags: nat, static-nat, outbound, easy-ip, nat-server, phase-transition
- Evidence level: source-derived design constraint; confirm target-platform support and runtime behavior.
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
- Status: validated
- Tags: gateway, inter-vlan, vlan, trunk, verification
- Evidence level: source-derived design constraint; confirm target-platform support and runtime behavior.
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
- Status: validated
- Tags: vrrp, gateway, failover, recovery, verification
- Evidence level: source-derived design constraint; confirm target-platform support and runtime behavior.
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

## DR-NAT-003: Separate server publication, hairpin access, ALG, and outbound translation claims
- Status: candidate
- Tags: nat, nat-server, hairpin, dns-map, alg, pbr, dual-exit, packet-processing-order
- Evidence level: candidate; source-derived from sequential examples and not independently runtime-validated in this project.
- Requires: `egress-route-resolved`, `return-path-defined`, `authorization-policy-ready`, `packet-processing-order-defined`
- Provides: `server-publication-ready`
- Trigger: A multi-exit edge must publish an internal service while also supporting inside access, DNS mapping, ALG, or general outbound NAT.
- Design goal: Keep service publication, inside-to-published-name access, protocol assistance, and outbound source translation as separate contracts.
- Decision logic: Derive the inside server, public service tuple, exit path, return route, and required client locations; configure only the required server mapping and outbound scope; add DNS mapping/ALG only for the named protocol; place a more-specific inside exception before a generic redirect or exit policy; then test each traffic direction separately.
- Recompute parameters: Server/private and public addresses, service ports, exit interfaces, NAT selectors, DNS-map name/address, ALG requirement, PBR order, return routes, and positive/negative service assertions.
- Applicability boundary: Candidate until target-platform processing order, hairpin behavior, ALG support, and runtime translation/session evidence are independently confirmed; a source NAT table or successful Ping does not prove service publication.
- Common failure: A generic redirect captures an inside server response, DNS mapping is treated as authorization, an ALG is enabled without a protocol need, or an outbound rule changes the published-service path.
- Implementation order: Establish underlay and return path; define authorization; define server mapping; add the inside exception and any required DNS/ALG function; bind outbound NAT; inspect translations/sessions; test inside, outside, and negative-service cases.
- Verification method: Correlate policy match, translation direction, DNS/ALG state, applied-policy records, session state, and the exact service results.
