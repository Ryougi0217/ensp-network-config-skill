# Resilience and OAM Design Rules

Read these rules for cross-protocol redundancy, failure handling, and operational proof. Match each trigger and boundary before use.

## DR-OAM-001: Require a three-state proof for liveness-tracked routes
- Tags: bfd, nqa, static-route, tracking, failure, recovery
- Requires: `layer3-adjacency-ready`, `internal-routing-ready`
- Provides: `liveness-tracking-ready`, `fault-test-plan-ready`, `recovery-test-plan-ready`
- Trigger: A route or gateway decision is attached to BFD/NQA liveness.
- Design goal: Keep liveness configuration, normal state, fault response, and recovery state observable as separate gates.
- Decision logic: Derive the protected health condition from the real forwarding topology. Create a session for every local upstream path whose loss must affect the route or gateway decision; do not substitute a peer or aggregation interconnect for upstream reachability. Attach each session only to the intended route or active gateway group, choose the decrement/withdrawal behavior from the desired single- and multi-fault outcome, then prove normal, fault, and restored states. Keep platform defaults for timers unless the requirement or verified platform behavior needs explicit values.
- Recompute parameters: Relevant upstream links, probe/session names, source/destination, optional timers, tracked route or gateway groups, priority decrement or withdrawal rule, single/multi-fault targets, and recovery window.
- Applicability boundary: Confirm target VRP/simulator support before generating executable commands, and do not claim recovery without post-restore evidence; a successful NQA sample alone is not a service-level objective.
- Common failure: Only a peer/inter-switch session is monitored while the actual upstream fails, one relevant uplink is omitted, a decrement causes unintended takeover after a non-critical fault, or recovery is assumed from a normal-state result.
- Implementation order: Establish every relevant upstream; configure one liveness session per protected path; attach the sessions to the intended route/gateway decisions; verify normal state; execute each named single or combined fault; restore and verify recovery.
- Verification method: Correlate every session/probe state with route or gateway ownership across normal, each named fault, and restored phases; do not use one session or one Ping as proof for all upstreams.
