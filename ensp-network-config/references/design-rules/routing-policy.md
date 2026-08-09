# Routing Policy Design Rules

Read these rules for static routing, dynamic routing method boundaries, route preference, and route filtering. Recompute all route prefixes, next hops, preferences, and policy attachments from the current topology.

## DR-ROUTE-001: Design forward and return paths as separate obligations
- Status: validated
- Tags: static-route, asymmetric-routing, return-path, verification
- Evidence level: validated design constraint; require current-project runtime evidence for operational claims.
- Trigger: Endpoints require directed forwarding paths, primary/backup static routes, or any behavior where the forward and return paths may differ.
- Design goal: Make reachability, route installation, and path direction independently explainable for both traffic directions.
- Decision logic: Derive the forward and reverse path from the current topology and requirements; check a destination route or default-route decision at every transit and edge device; specify primary and alternate choices separately; never infer the return path from a successful forward test.
- Recompute parameters: Source and destination prefixes, next hops, transit devices, route preference, default-route scope, endpoint gateways, and the exact path assertions required by the project.
- Applicability boundary: Reassess when the topology is directly connected, when a dynamic protocol owns the route, or when the requirement does not constrain path direction. Failover remains unproven until the requested fault is executed and observed.
- Common failure: A forward route is present but the return route or endpoint gateway is missing, or a single successful Ping is treated as proof of the intended path and redundancy behavior.
- Implementation order: Confirm endpoint gateways and connected prefixes; derive forward routes; derive return routes; add primary/alternate preference only when required; inspect both route directions; then run path and fault assertions.
- Verification method: Correlate routing-table entries with bidirectional reachability and, where requested, forward/return path captures or traces. Record static completeness separately from runtime path and failover evidence.

## DR-ROUTE-002: Use route preference to stage active and alternate paths
- Status: candidate
- Tags: static-route, floating-static, preference, load-balance, failover
- Evidence level: candidate; exclude from normal projects until independently validated.
- Trigger: A design needs an active static route, a higher-preference backup, or a later equal-preference load-sharing stage.
- Design goal: Make route selection changes observable and reversible instead of assuming that adding a second route changes the forwarding state as intended.
- Decision logic: Establish the direct/primary route first; add the alternate with an explicitly higher preference; inspect active and hidden entries; test the requested link/device fault; only then attempt equal-preference load sharing and confirm whether the platform updated or duplicated prior entries.
- Recompute parameters: Destination prefix, next hops, preference values, failure target, expected active/backup state, and route-inspection commands.
- Applicability boundary: Candidate only until runtime route-table output and a controlled failure test confirm the platform behavior; do not claim load balancing from equal-looking configuration lines.
- Common failure: A route is left at an unintended preference, a prior entry is duplicated rather than updated, or a backup is declared working without a failure observation.
- Implementation order: Install primary; inspect; install alternate; inspect; execute the requested fault; restore; then validate equal-cost eligibility if required.
- Verification method: Use route-table protocol/state output before and after the fault, plus reachability/path evidence for both directions.

## DR-RIP-001: Separate dynamic-routing method scope from learned-route proof
- Status: validated
- Tags: rip, dynamic-routing, route-learning, debugging
- Evidence level: source-derived design constraint; confirm target-platform support and runtime behavior.
- Trigger: A project introduces RIP or another dynamic-routing process and claims that remote prefixes have been learned.
- Design goal: Keep protocol configuration, version/method scope, process state, and learned-route results as separate claims.
- Decision logic: Derive participating interfaces and advertised networks from the topology; state the protocol/version actually present in the source; verify process and peer/update state; then verify the expected learned prefixes and reachability.
- Recompute parameters: Protocol version, process ID, advertised prefixes, interfaces, neighbors or peers, learned destinations, and debug/status evidence.
- Applicability boundary: Do not infer RIPv2 commands from a title-only heading, and do not treat static reachability or a protocol packet screenshot as proof of every learned route.
- Common failure: Method text is mistaken for runtime convergence, a debugging anomaly is copied as a command template, or route learning is claimed without a route-table observation.
- Implementation order: Establish interface reachability; configure the explicitly supported protocol method; verify process/peer state; inspect learned routes; then test reachability and cleanup debugging.
- Verification method: Retain separate evidence for configuration method, process state, learned routes, and endpoint reachability.

## DR-ROUTE-003: Treat source protocol outputs as scoped observations
- Status: validated
- Tags: rip, ospf, route-learning, source-evidence, verification
- Evidence level: source-derived design constraint; confirm target-platform support and runtime behavior.
- Trigger: A screenshot or excerpt contains a dynamic-routing peer, route, or path result for only one device or phase.
- Design goal: Preserve the observed scope and avoid expanding one protocol output into a claim about every participant or endpoint.
- Decision logic: Identify the device, command, phase, peer, and prefixes visible in the evidence; normalize method statements separately; require independent state and reachability evidence for claims outside that scope.
- Recompute parameters: Device, process, area/version, peer identity, learned prefixes, direction, endpoint path, and test phase.
- Applicability boundary: Complete device-by-device output and a clean rerun are required before extending an observed result into a broader convergence claim.
- Common failure: A route table on one router is presented as a converged domain, or a protocol configuration is treated as proof of learned routes.
- Implementation order: Normalize source scope; validate configuration structure; collect state on each required participant; then test endpoint reachability.
- Verification method: Label each observation by device and phase, and retain missing-scope evidence as a boundary.

## DR-POLICY-001: Treat a route-filter object as inactive until attachment and effect are proven
- Status: candidate
- Tags: rip, route-filter, acl, ip-prefix, policy-attachment
- Evidence level: candidate; exclude from normal projects until independently validated.
- Trigger: A route filter, ACL, or IP Prefix object is defined for a routing protocol.
- Design goal: Prevent an unattached or untested policy object from being described as an active route-filtering behavior.
- Decision logic: Record the match rules and ordering; identify the protocol and direction of attachment; verify the attachment command; inspect the filtered/learned result; preserve overlapping source prefixes and missing application commands as evidence boundaries.
- Recompute parameters: Prefixes, match lengths, rule order, protocol, import/export direction, attachment point, and expected route-table result.
- Applicability boundary: Candidate only while the attachment or runtime effect is missing; an object definition alone is not a validated policy rule.
- Common failure: A prefix list is created but never referenced, rule order is assumed, or a filtered route is claimed without route-table and reachability evidence.
- Implementation order: Confirm source prefixes; define and inspect match order; apply to the intended protocol direction; verify attachment; then inspect and test the resulting route set.
- Verification method: Compare object definition, protocol attachment, route-table state, and the required positive/negative route assertions.
