# OSPF Design Rules

Read these rules for OSPF area layout, adjacency dependencies, and route-learning decisions. Match the area topology and platform support before use.

## DR-OSPF-001: Build multi-area OSPF around explicit backbone and ABR continuity
- Status: validated
- Tags: ospf, multiarea, abr, router-id, routing
- Evidence cases: `003-ospf-multiarea`, `015-ospf-special-areas-vrrp`
- Validation basis: Multiple approved cases; blind test waived by user for batch learning.
- Trigger: The topology or requirement uses multiple OSPF areas and requires inter-area reachability.
- Design goal: Keep the backbone and area boundaries explicit so every non-backbone area has a valid route to the OSPF transit domain.
- Decision logic: Identify the backbone area and each ABR from the current graph; assign every routed link, LAN, and loopback to the intended area; use unique Router IDs; configure special-area behavior only after the ordinary area adjacency and route scope are consistent.
- Recompute parameters: OSPF process identifier, Router IDs, area membership, interface network/wildcard matches, ABR roles, loopback placement, and any special-area or default-route controls.
- Applicability boundary: Reassess when the topology has no multi-area requirement, when an area is intentionally disconnected from the backbone, or when the target platform's OSPF/special-area support is unconfirmed.
- Common failure: A non-backbone area has no valid ABR path, one link is advertised into the wrong area, Router IDs collide, or a loopback is placed outside the intended route scope.
- Implementation order: Confirm subnets and roles; assign unique Router IDs; configure backbone and non-backbone memberships; configure special-area behavior only where required; verify adjacency, inter-area route learning, and end-to-end reachability.
- Verification method: Check area/network structure and Router-ID uniqueness, inspect OSPF neighbor and route state, then test at least one positive inter-area path and the required endpoint or loopback reachability. Do not treat static configuration review as runtime adjacency proof.

## DR-OSPF-002: Apply special-area behavior consistently to all members of the area
- Status: candidate
- Tags: ospf, nssa, stub, totally-stub, area-policy
- Evidence cases: `015-ospf-special-areas-vrrp`
- Validation basis: One approved case with direct special-area evidence; no independent approved case and no blind test in this batch.
- Trigger: The requirement explicitly asks for NSSA, stub, totally stub, summary suppression, or a comparable special-area behavior.
- Design goal: Make the area policy predictable by applying the same area type semantics to the correct edge and internal members while preserving the ABR boundary.
- Decision logic: Identify the area edge/ABR and all area members from the topology; select the special-area type from the requirement's route-visibility/default-route goal; apply compatible member settings and verify the resulting route scope before adding gateway or service dependencies.
- Recompute parameters: Area membership, ABR and internal-router roles, special-area type, no-summary/default behavior, and any external-route injection requirements.
- Applicability boundary: Do not use when the requirement does not specify route suppression or external-route behavior, or when platform support for the selected special-area type is unclear.
- Common failure: ABR and internal routers disagree on area type, a no-summary setting is applied to the wrong device, or a default/external route is assumed without direct evidence.
- Implementation order: Establish ordinary OSPF adjacency and backbone reachability; apply consistent area-type settings; verify route-table behavior; then add VRRP or service paths.
- Verification method: Inspect area configuration and OSPF neighbor state, compare route tables on the ABR and internal routers, and test required inter-area reachability. Current evidence does not prove fault recovery or universal platform support.

## DR-OSPF-003: Keep single-area adjacency, route learning, and reachability separate
- Status: validated
- Tags: ospf, single-area, adjacency, route-learning, verification
- Evidence cases: 059-ospf-inter-vlan-exam
- Validation basis: Direct source-rule adoption authorized by the user; case 059 contains source-visual Full-neighbor and route observations, but no independent eNSP rerun or blind test.
- Trigger: A single-area OSPF design claims that internal VLAN or loopback prefixes are reachable through a transit link.
- Design goal: Prevent explicit network statements or one Full-neighbor screenshot from being treated as proof of the complete route and endpoint behavior.
- Decision logic: Confirm unique Router IDs and area/network scope; verify the intended adjacency; inspect learned prefixes on the receiving device; then test the required endpoint path.
- Recompute parameters: Process ID, Router IDs, area, wildcard statements, transit subnet, expected learned prefixes, and path assertions.
- Applicability boundary: When the source scope is incomplete or runtime adjacency/route evidence is not independently reproduced, keep the result explicitly unverified and do not extend it beyond the observed device and phase.
- Common failure: A Full neighbor is shown but the expected route is absent, a network statement matches an unintended interface, or static reachability is mistaken for OSPF learning.
- Implementation order: Establish interface addressing; configure and inspect OSPF scope; verify adjacency; verify learned routes; then test reachability.
- Verification method: Correlate configuration, neighbor state, protocol route entries, and endpoint results.
