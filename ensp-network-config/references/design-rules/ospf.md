# OSPF Design Rules

Read these rules for OSPF area layout, adjacency dependencies, and route-learning decisions. Match the area topology and platform support before use.

## DR-OSPF-001: Build multi-area OSPF around explicit backbone and ABR continuity
- Tags: ospf, multiarea, abr, router-id, routing
- Requires: `layer3-adjacency-ready`, `topology-baseline-confirmed`
- Provides: `dynamic-routing-ready`, `internal-routing-ready`
- Trigger: The topology or requirement uses multiple OSPF areas and requires inter-area reachability.
- Design goal: Keep the backbone and area boundaries explicit so every non-backbone area has a valid route to the OSPF transit domain.
- Decision logic: Identify the backbone area and each ABR from the current graph; assign every routed link, LAN, and loopback to the intended area; use unique Router IDs; configure special-area behavior only after the ordinary area adjacency and route scope are consistent.
- Recompute parameters: OSPF process identifier, Router IDs, area membership, interface network/wildcard matches, ABR roles, loopback placement, and any special-area or default-route controls.
- Applicability boundary: Reassess when the topology has no multi-area requirement, when an area is intentionally disconnected from the backbone, or when the target platform's OSPF/special-area support is unconfirmed.
- Common failure: A non-backbone area has no valid ABR path, one link is advertised into the wrong area, Router IDs collide, or a loopback is placed outside the intended route scope.
- Implementation order: Confirm subnets and roles; assign unique Router IDs; configure backbone and non-backbone memberships; configure special-area behavior only where required; verify adjacency, inter-area route learning, and end-to-end reachability.
- Verification method: Check area/network structure and Router-ID uniqueness, inspect OSPF neighbor and route state, then test at least one positive inter-area path and the required endpoint or loopback reachability. Do not treat static configuration review as runtime adjacency proof.

## DR-OSPF-003: Keep single-area adjacency, route learning, and reachability separate
- Tags: ospf, single-area, adjacency, route-learning, verification
- Requires: `layer3-adjacency-ready`
- Provides: `dynamic-routing-ready`, `internal-routing-ready`
- Trigger: A single-area OSPF design claims that internal VLAN or loopback prefixes are reachable through a transit link.
- Design goal: Prevent explicit network statements or one Full-neighbor screenshot from being treated as proof of the complete route and endpoint behavior.
- Decision logic: Confirm unique Router IDs and area/network scope; verify the intended adjacency; inspect learned prefixes on the receiving device; then test the required endpoint path.
- Recompute parameters: Process ID, Router IDs, area, wildcard statements, transit subnet, expected learned prefixes, and path assertions.
- Applicability boundary: When the source scope is incomplete or runtime adjacency/route evidence is not independently reproduced, keep the result explicitly unverified and do not extend it beyond the observed device and phase.
- Common failure: A Full neighbor is shown but the expected route is absent, a network statement matches an unintended interface, or static reachability is mistaken for OSPF learning.
- Implementation order: Establish interface addressing; configure and inspect OSPF scope; verify adjacency; verify learned routes; then test reachability.
- Verification method: Correlate configuration, neighbor state, protocol route entries, and endpoint results.
