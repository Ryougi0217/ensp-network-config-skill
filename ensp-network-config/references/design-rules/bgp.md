# BGP Design Rules (Reserved)

This catalog remains reserved. Candidate rules are recorded for research traceability and are not available to normal configuration projects.

## DR-BGP-001: Separate BGP session, address-family, policy, and route-selection claims
- Status: candidate
- Tags: bgp, address-family, route-policy, next-hop, route-selection
- Evidence level: candidate; extracted from AR chapter 8 examples and not independently runtime-validated in this project.
- Requires: `platform-support-confirmed`, `layer3-adjacency-ready`, `internal-routing-ready`
- Provides: `bgp-control-plane-ready`, `dynamic-routing-ready`
- Trigger: A design uses BGP or MP-BGP and claims that a prefix is exchanged, preferred, or switched after a failure.
- Design goal: Keep peer session state, address-family enablement, policy attachment, next-hop resolution, and selected-route evidence distinct.
- Decision logic: Confirm underlay reachability and peer AS/role; enable the intended address family; attach import/export policy and next-hop handling; inspect peer and received/advertised routes; then execute the required path/failure test.
- Recompute parameters: Local/peer AS, router ID, peer address, AFI/SAFI, source interface, policy direction/order, next-hop behavior, preference, prefixes, and fault target.
- Applicability boundary: Candidate until both peers' session/AF state, route policy effect, and controlled failure output are independently confirmed.
- Common failure: A configured peer is treated as Established, a route table is treated as policy proof, or a preferred route is claimed without a before/after fault observation.
- Implementation order: Underlay; session; address family; policy/next hop; route inspection; endpoint/path test; controlled fault and recovery.
- Verification method: Correlate peer state, AF state, advertised/received routes, selected route, path trace, and fault evidence.
