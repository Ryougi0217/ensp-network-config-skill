# Security and Access Design Rules

Read these rules for ACL scope, DHCP trust boundaries, source validation, and positive/negative access assertions. Match each trigger and boundary before use.

## DR-ACL-001: Bind an ACL to the intended control-plane context and direction
- Tags: acl, vty, control-plane, direction, rule-order
- Requires: `management-path-ready`
- Provides: `management-source-policy-ready`
- Trigger: A device must restrict management or control-plane access with an ACL applied to a VTY or equivalent context.
- Design goal: Make the protected context, traffic direction, rule order, and underlying reachability explicit before claiming enforcement.
- Decision logic: Establish the routing path to the management context; define the permit/deny order from the requirement; apply the ACL in the stated direction and context; preserve ambiguous source syntax; then test allowed and denied sources.
- Recompute parameters: Protected context, source/destination scope, ACL type and identifier, rule order, direction, authentication mode, and positive/negative test sources.
- Applicability boundary: An ACL object or static route to the device does not prove enforcement; require runtime permit/deny outcomes before claiming the access policy succeeded.
- Common failure: The ACL is applied to the wrong direction/context, a deny precedes the intended permit, or a source syntax anomaly is silently normalized into a different policy.
- Implementation order: Confirm routing; define ordered rules; apply to the intended management context; inspect the resulting ACL; then test both permitted and denied sources.
- Verification method: Correlate route reachability, ACL display, application context/direction, and access outcomes.

## DR-ACL-002: Prove five-tuple permits together with an explicit negative destination
- Tags: acl, advanced-acl, five-tuple, placement, direction, original-source, negative-test
- Requires: `internal-routing-ready`
- Provides: `authorization-policy-ready`
- Trigger: An advanced ACL permits or denies a narrowly scoped protocol/source/destination tuple and depends on explicit or implicit treatment of other traffic.
- Design goal: Distinguish the intended positive or denied tuple from the remaining traffic space and prove both sides of the policy.
- Decision logic: Define the exact tuple, then trace both directions and choose the smallest physical or logical attachment set that sees the required packet identity before it changes. Ingress on a source-facing port, outbound on a shared uplink, or outbound near the protected destination may all be valid; choose by tuple visibility, bypass resistance, and clarity rather than copying an interface context. Avoid duplicate attachment when blocking one required direction already enforces the stated session boundary.
- Recompute parameters: Protocol, source/destination prefixes and services, original and transformed packet identity, possible attachment ports, ingress/outbound direction, alternate paths, rule order, and positive/negative assertions.
- Applicability boundary: A project may require physical-port placement, but Vlanif or policy-context ACLs remain valid in other designs. A failed bidirectional Ping after blocking one direction proves only that reachability assertion, not comprehensive control of every protocol or reverse/new session.
- Common failure: The ACL is bound where the original source is no longer visible, an alternate path bypasses the attachment, a broad rule is applied at too many points, or one failed Ping is treated as proof of the whole policy.
- Implementation order: Establish routing; define the tuple; trace both directions and alternate paths; select the clearest non-bypassable attachment and direction; configure and inspect the policy; then execute positive and negative tests.
- Verification method: Correlate route/path evidence, ACL counters, actual attachment/direction, and separate permitted/denied results for the exact tuples; include an alternate-path check when one exists.

## DR-DHCPSEC-001: Place DHCP trust only on the legitimate server path
- Tags: dhcp-snooping, rogue-dhcp, trusted-port, vlan, access-security
- Requires: `layer2-transport-ready`, `address-service-ready`
- Provides: `source-trust-ready`
- Trigger: DHCP clients share a Layer-2 access domain where unauthorized DHCP replies must be blocked.
- Design goal: Allow server-originated DHCP messages only from the legitimate server or relay path while preserving client requests and a usable binding table.
- Decision logic: Identify the real DHCP server/relay path from the topology; enable Snooping at the required global and VLAN/interface scopes; mark only the server-facing path as trusted; keep client-facing ports untrusted; then compare legitimate and rogue-server outcomes and inspect bindings.
- Recompute parameters: Client VLANs, server/relay location, trusted uplinks, client-facing ports, trunk path, Snooping scope, and legitimate/rogue assertions.
- Applicability boundary: Confirm device and VRP/eNSP support and account for relays, stacked devices, and multiple legitimate server paths; never mark a broad user-facing segment trusted merely to make DHCP work.
- Common failure: The client port is trusted, the actual server path is not trusted, Snooping is enabled at only one required scope, or a lease is treated as proof that rogue replies are blocked.
- Implementation order: Confirm DHCP path; establish normal allocation; enable Snooping; trust only the legitimate server path; inspect bindings; test valid allocation and the explicitly controlled rogue-server case.
- Verification method: Correlate trust state, Snooping bindings, legitimate lease acquisition, and rejected unauthorized server behavior.

## DR-IPSG-001: Enforce source identity only after the binding source is complete
- Tags: ipsg, source-guard, dhcp-snooping, ip-mac-binding, access-security
- Requires: `source-trust-ready`
- Provides: `source-identity-policy-ready`
- Trigger: Access ports must reject hosts whose source IP/MAC/VLAN/interface identity does not match the authorized assignment.
- Design goal: Prevent address spoofing without blocking legitimate users because the static or DHCP-derived binding table is missing or stale.
- Decision logic: Choose static bindings for deliberately static clients or DHCP Snooping bindings for dynamic clients; confirm the required identity fields and binding presence; enable source checking only on the intended user-facing scope; then test an authorized tuple and a controlled changed-source tuple.
- Recompute parameters: Binding source, client IP/MAC/VLAN/interface tuple, enforcement interfaces or VLANs, DHCP trust path, and positive/negative source assertions.
- Applicability boundary: Confirm platform support and binding completeness before enforcement; dynamic IPSG depends on correct DHCP Snooping, and incomplete bindings can deny valid traffic.
- Common failure: Enforcement is enabled before bindings exist, a dynamic client is represented by a stale static tuple, or checking is applied to an infrastructure/server-facing link.
- Implementation order: Confirm client addressing mode; build and inspect bindings; select user-facing enforcement scope; enable source checking; test the authorized identity; then test one controlled spoofed identity.
- Verification method: Compare binding-table state with permitted legitimate traffic and denied mismatched source traffic on the exact enforcement scope.

## DR-FW-001: Assign firewall interfaces to zones before writing policy
- Tags: firewall, security-zone, trust, dmz, untrust
- Requires: `interface-map-confirmed`, `layer3-adjacency-ready`
- Provides: `firewall-zones-ready`
- Trigger: A firewall policy refers to trust, DMZ, untrust, or equivalent security zones.
- Design goal: Make the policy's boundaries meaningful by resolving interface-to-zone membership first.
- Decision logic: Identify interface roles from the topology; configure and inspect zone membership; only then create source-zone/destination-zone policy and NAT objects.
- Recompute parameters: Interface identity, zone role, subnet, security-level/default behavior, transit path, and policy direction.
- Applicability boundary: Zone names and default inter-zone behavior vary by firewall model/version; do not infer policy effect from object existence.
- Common failure: An interface is in the wrong zone, a DMZ interface is omitted, or a policy is evaluated in an unintended direction.
- Implementation order: Address interfaces; assign zones; inspect zones; define policy; define NAT; test positive and negative flows.
- Verification method: Correlate zone display, policy match, session table, and source/destination test results.

## DR-FW-002: Express firewall policy direction and scope explicitly
- Tags: firewall, security-policy, direction, least-privilege, service
- Requires: `firewall-zones-ready`, `internal-routing-ready`
- Provides: `security-policy-ready`, `authorization-policy-ready`
- Trigger: A firewall must permit a specific inter-zone business flow.
- Design goal: Allow only the required source/destination/service combination and avoid relying on a vague “any-to-any” interpretation.
- Decision logic: State source zone, destination zone, source/destination scope, protocol/service, action, and rule order; add a reverse/new-session negative assertion.
- Recompute parameters: Zones, prefixes, service/port, policy name/order, source restrictions, and negative test path.
- Applicability boundary: Statefulness and default deny/permit behavior vary; confirm target firewall semantics before claiming reverse blocking.
- Common failure: Only the direction label is tested, a publish rule permits an entire DMZ, or rule order makes a later deny unreachable.
- Implementation order: Define minimal scope; create rule; inspect ordering; test allowed service; test reverse/new session and adjacent service.
- Verification method: Use policy counters/logs, session table, positive result, and explicit negative result.

## DR-FW-003: Treat NAT as address transformation, not authorization
- Tags: firewall, nat, security-policy, source-nat, server-publish
- Requires: `security-policy-ready`, `egress-route-resolved`, `return-path-defined`
- Provides: `firewall-translation-ready`
- Trigger: A firewall uses source NAT, PAT, or destination/server mapping.
- Design goal: Keep translation scope and access authorization independently reviewable.
- Decision logic: Define the required policy first; define only the translation scope needed for the same business flow; verify both policy match and translated session.
- Recompute parameters: Private/public addresses, ports, protocol, translation mode, address pool, source/destination zones, return path, and service scope.
- Applicability boundary: A successful translation does not prove policy authorization or return-path correctness; platform processing order must be confirmed.
- Common failure: NAT is configured without a permit policy, a broad pool translates protected traffic, or server publication exposes extra ports.
- Implementation order: Zone/policy; route; NAT object; binding; session; positive/negative service tests.
- Verification method: Check policy action, NAT/session translation, and endpoint behavior separately.

## DR-FW-004: Pair every allow rule with a deliberate deny test
- Tags: firewall, negative-test, stateful, access-control, verification
- Requires: `security-policy-ready`
- Provides: `security-validation-ready`
- Trigger: A firewall rule is described as successfully enforcing an access boundary.
- Design goal: Prove both intended access and the protection against the closest unauthorized flow.
- Decision logic: For each allow, choose a same-scope positive flow and a reverse/new-session or adjacent-service negative flow; capture rule/session/log evidence for both.
- Recompute parameters: Positive source/destination/service, negative source/destination/service, statefulness, NAT dependency, and expected log/session behavior.
- Applicability boundary: A failed Ping can reflect routing/NAT/host issues; classify the layer before calling it a firewall deny.
- Common failure: Only the positive path is tested, a reverse established flow is confused with a new session, or a NAT failure is misreported as policy denial.
- Implementation order: Establish underlay; inspect zones; test positive; initiate controlled negative; inspect policy/session/logs; report the failure layer.
- Verification method: Require separate positive/negative outcomes and policy/session evidence tied to the exact flow.
