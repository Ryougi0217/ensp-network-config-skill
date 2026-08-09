# IS-IS Design Rules (Reserved)

This catalog remains reserved. Candidate rules are recorded for research traceability and are not available to normal configuration projects.

## DR-ISIS-001: Align NET, level, area, and interface enablement before route claims
- Status: candidate
- Tags: isis, net, level, area, adjacency, route-learning
- Evidence level: candidate; extracted from AR chapter 8 examples and not independently runtime-validated in this project.
- Trigger: A design uses IS-IS or IS-IS for IPv6 and claims adjacency or learned routes.
- Design goal: Keep process identity, NET/area, level scope, interface enablement, and learned-route evidence aligned.
- Decision logic: Derive the intended level and area from the topology; assign unique NETs and system IDs; enable IS-IS on the required interfaces and address families; inspect adjacency; then verify learned routes and endpoint paths.
- Recompute parameters: Process ID, NET/system ID, level, area, interface set, IPv4/IPv6 address family, metric, prefixes, and expected neighbors.
- Applicability boundary: Candidate until complete neighbor state and route-learning evidence exist for all required participants; a configuration excerpt is not convergence proof.
- Common failure: NET/area or level mismatches prevent adjacency, an interface is omitted, or one route table is generalized to the whole domain.
- Implementation order: Addressing/underlay; NET and level; interface enablement; adjacency; route inspection; endpoint and failure tests.
- Verification method: Correlate NET/level configuration, peer state, route table, and path evidence by device and phase.
