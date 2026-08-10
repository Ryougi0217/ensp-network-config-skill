# Multicast Design Rules (Reserved)

This catalog remains reserved. Candidate rules are recorded for research traceability and are not available to normal configuration projects.

## DR-MCAST-001: Separate multicast mode, RPF, membership, and forwarding proof
- Status: candidate
- Tags: multicast, igmp, pim, pim-sm, pim-dm, rp, bsr, ssm, rpf, snooping
- Evidence level: candidate; extracted from AR chapter 9 examples and command hierarchy cross-checked against Huawei documentation, but not independently runtime-validated in this project.
- Requires: `platform-support-confirmed`, `internal-routing-ready`
- Provides: `multicast-service-ready`
- Trigger: A design must deliver multicast data through PIM-DM, PIM-SM with a static or BSR-learned RP, PIM-SSM, or an IGMP Snooping policy.
- Design goal: Keep the selected PIM profile, global/interface state, source RPF routing, receiver membership, and actual forwarding as separate claims.
- Decision logic: Select exactly one `pim-forwarding-profile` per routed multicast domain: `dm`, `sm-static-rp`, `sm-bsr`, `sm-bsr-static-backup`, or `sm-ssm`. Use no RP with `dm` or `sm-ssm`; use one consistent reachable static RP with `sm-static-rp`; use candidate BSR/RP roles without a static RP with `sm-bsr`; combine BSR and a consistently configured static fallback only when the requirement selects `sm-bsr-static-backup` and the target platform's RP precedence is confirmed. Establish unicast RPF reachability, enable PIM on every required routed interface, and enable IGMP or Snooping only on the receiver-facing scope before inspecting membership and forwarding.
- Recompute parameters: Source/receiver prefixes, group range, selected PIM profile, participating routed interfaces, RP address or candidate BSR/RP roles when applicable, SSM range and receiver version when applicable, RPF route, receiver interface, VLAN policy, and positive/negative group assertions.
- Applicability boundary: Candidate until platform capability, complete control-plane state, and controlled receiver/forwarding evidence are confirmed. Do not generate executable SM-ASM configuration while the RP method is unresolved, and do not infer delivery from displayed IGMP/PIM state.
- Common failure: `static-rp` is copied into a DM or SSM design, SM-ASM has no RP method, static and BSR methods are combined without an explicit backup/precedence design, routers disagree on the RP/group scope, RPF is wrong, or a forwarding-table entry is treated as end-to-end delivery.
- Implementation order: Underlay/RPF; multicast global state; select one PIM profile; configure all required PIM interfaces; configure only that profile's RP/BSR/SSM dependency; enable receiver membership/Snooping; inspect state; run positive and filtered-group tests.
- Verification method: Correlate the selected profile with interface mode, absence or presence of the matching RP mechanism, unicast route/RPF, PIM/IGMP state, group membership, forwarding table, and receiver output.
