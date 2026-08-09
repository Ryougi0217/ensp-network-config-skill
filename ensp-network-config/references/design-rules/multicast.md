# Multicast Design Rules (Reserved)

This catalog remains reserved. Candidate rules are recorded for research traceability and are not available to normal configuration projects.

## DR-MCAST-001: Separate multicast control plane, RPF, membership, and forwarding proof
- Status: candidate
- Tags: multicast, igmp, pim, rp, rpf, snooping
- Evidence level: candidate; extracted from AR chapter 9 examples and not independently runtime-validated in this project.
- Requires: `platform-support-confirmed`, `internal-routing-ready`
- Provides: `multicast-service-ready`
- Trigger: A design must deliver multicast data to receivers through IGMP/PIM, a static/dynamic RP, or an IGMP Snooping policy.
- Design goal: Keep global/interface protocol state, source RPF routing, receiver membership, and actual forwarding as separate claims.
- Decision logic: Enable multicast routing and the intended interface roles; establish unicast reachability for RPF; align PIM/RP or SSM parameters; enable IGMP or Snooping only on receiver-facing scope; then inspect membership, routing, and forwarding state.
- Recompute parameters: Source/receiver prefixes, group range, PIM mode, RP/BSR, RPF route, receiver interface, VLAN policy, and positive/negative group assertions.
- Applicability boundary: Candidate until platform capability, complete control-plane state, and controlled receiver/forwarding evidence are confirmed; a displayed IGMP/PIM state is not proof of video delivery.
- Common failure: Receiver membership is present but RPF is wrong, static RP differs across routers, Snooping policy order is wrong, or a forwarding-table entry is treated as end-to-end delivery.
- Implementation order: Underlay/RPF; multicast global state; PIM/RP; receiver membership/Snooping; state inspection; positive and filtered-group tests.
- Verification method: Correlate unicast route/RPF, PIM/IGMP state, group membership, forwarding table, and receiver output.
