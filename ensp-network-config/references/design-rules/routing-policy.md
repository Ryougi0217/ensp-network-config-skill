# Routing Policy Design Rules

Read these rules for static routing, dynamic routing method boundaries, route preference, and route filtering. Recompute all route prefixes, next hops, preferences, and policy attachments from the current topology.

## DR-ROUTE-001: Design forward and return paths as separate obligations
- Tags: static-route, asymmetric-routing, return-path, verification
- Requires: `layer3-adjacency-ready`
- Provides: `forward-path-defined`, `return-path-defined`, `internal-routing-ready`
- Trigger: Endpoints require directed forwarding paths, primary/backup static routes, or any behavior where the forward and return paths may differ.
- Design goal: Make reachability, route installation, and path direction independently explainable for both traffic directions.
- Decision logic: Derive the forward and reverse path from the current topology and requirements; check a destination route or default-route decision at every transit and edge device; specify primary and alternate choices separately; never infer the return path from a successful forward test.
- Recompute parameters: Source and destination prefixes, next hops, transit devices, route preference, default-route scope, endpoint gateways, and the exact path assertions required by the project.
- Applicability boundary: Reassess when the topology is directly connected, when a dynamic protocol owns the route, or when the requirement does not constrain path direction. Failover remains unproven until the requested fault is executed and observed.
- Common failure: A forward route is present but the return route or endpoint gateway is missing, or a single successful Ping is treated as proof of the intended path and redundancy behavior.
- Implementation order: Confirm endpoint gateways and connected prefixes; derive forward routes; derive return routes; add primary/alternate preference only when required; inspect both route directions; then run path and fault assertions.
- Verification method: Correlate routing-table entries with bidirectional reachability and, where requested, forward/return path captures or traces. Record static completeness separately from runtime path and failover evidence.

## DR-RIP-001: Separate dynamic-routing method scope from learned-route proof
- Tags: rip, dynamic-routing, route-learning, debugging
- Requires: `layer3-adjacency-ready`
- Provides: `dynamic-routing-ready`, `internal-routing-ready`
- Trigger: A project introduces RIP or another dynamic-routing process and claims that remote prefixes have been learned.
- Design goal: Keep protocol configuration, version/method scope, process state, and learned-route results as separate claims.
- Decision logic: Derive participating interfaces and advertised networks from the topology; state the protocol/version actually present in the source; verify process and peer/update state; then verify the expected learned prefixes and reachability.
- Recompute parameters: Protocol version, process ID, advertised prefixes, interfaces, neighbors or peers, learned destinations, and debug/status evidence.
- Applicability boundary: Do not infer RIPv2 commands from a title-only heading, and do not treat static reachability or a protocol packet screenshot as proof of every learned route.
- Common failure: Method text is mistaken for runtime convergence, a debugging anomaly is copied as a command template, or route learning is claimed without a route-table observation.
- Implementation order: Establish interface reachability; configure the explicitly supported protocol method; verify process/peer state; inspect learned routes; then test reachability and cleanup debugging.
- Verification method: Retain separate evidence for configuration method, process state, learned routes, and endpoint reachability.

## DR-ROUTE-003: Treat source protocol outputs as scoped observations
- Tags: rip, ospf, route-learning, source-evidence, verification
- Requires: `topology-baseline-confirmed`
- Provides: `validation-scope-ready`
- Trigger: A screenshot or excerpt contains a dynamic-routing peer, route, or path result for only one device or phase.
- Design goal: Preserve the observed scope and avoid expanding one protocol output into a claim about every participant or endpoint.
- Decision logic: Identify the device, command, phase, peer, and prefixes visible in the evidence; normalize method statements separately; require independent state and reachability evidence for claims outside that scope.
- Recompute parameters: Device, process, area/version, peer identity, learned prefixes, direction, endpoint path, and test phase.
- Applicability boundary: Complete device-by-device output and a clean rerun are required before extending an observed result into a broader convergence claim.
- Common failure: A route table on one router is presented as a converged domain, or a protocol configuration is treated as proof of learned routes.
- Implementation order: Normalize source scope; validate configuration structure; collect state on each required participant; then test endpoint reachability.
- Verification method: Label each observation by device and phase, and retain missing-scope evidence as a boundary.
