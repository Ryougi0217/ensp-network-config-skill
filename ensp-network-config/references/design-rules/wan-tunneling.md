# WAN and Tunneling Design Rules

Read these rules for PPP, PPPoE, GRE, IPsec, and related WAN dependency decisions. Match the access role, authentication method, and platform support before use.

## DR-PPP-001: Keep PPP authentication roles explicit before validating reachability
- Status: validated
- Tags: ppp, pppoe, pap, chap, aaa, authentication
- Evidence level: validated design constraint; require current-project runtime evidence for operational claims.
- Requires: `interface-map-confirmed`, `platform-support-confirmed`
- Provides: `wan-session-ready`
- Trigger: A point-to-point PPP or PPPoE link requires PAP/CHAP or equivalent subscriber authentication.
- Design goal: Make the authentication direction, credential ownership, and dependent link state unambiguous before using the link for routing or services.
- Decision logic: Identify the server/authenticator and client/supplicant from the topology; configure the server-side user/service and authentication method; configure the client-side matching identity/secret; keep the bearer, dialer/virtual-template, and authentication roles aligned.
- Recompute parameters: Server/client roles, authentication method, user identity, credential storage form, serial or Ethernet bearer, dialer/virtual-template identifiers, and address-negotiation behavior.
- Applicability boundary: Reassess when the link is not PPP/PPPoE, when authentication is delegated externally, or when the target VRP/eNSP version changes supported syntax.
- Common failure: Both peers act as clients, the server lacks a PPP service user, PAP/CHAP methods disagree, or the session is assumed usable before authentication reaches an operational state.
- Implementation order: Confirm the bearer and addressing context; configure server authentication; configure client credentials and binding; verify the PPP session and peer address; only then add routing, NAT, or application tests.
- Verification method: Check the negotiated/session state and authentication role, then run a positive peer or downstream reachability test. Do not infer session success from a complete-looking configuration alone.

## DR-PPP-002: Treat PPPoE address negotiation as a prerequisite to edge services
- Status: candidate
- Tags: pppoe, nat, address-pool, dialer, default-route
- Evidence level: candidate; exclude from normal projects until independently validated.
- Requires: `interface-map-confirmed`, `platform-support-confirmed`
- Provides: `wan-session-ready`, `egress-route-resolved`
- Trigger: An edge router must obtain a negotiated PPPoE address and then provide NAT or a default route to an internal network.
- Design goal: Prevent NAT or routing claims from masking a missing PPPoE session, pool, or virtual-template dependency.
- Decision logic: Build the server AAA/pool/virtual-template chain and client dialer/bearer binding first; confirm negotiated addressing and session state; then install the default route and apply NAT to the intended outbound interface.
- Recompute parameters: Pool network and exclusions, virtual-template address, dialer/bearer identifiers, client source networks, ACL match scope, default-route interface, and public-side reachability checks.
- Applicability boundary: Do not generalize to a static WAN, a different authentication backend, or a platform whose PPPoE/NAT behavior is unconfirmed.
- Common failure: NAT is bound to an interface that never comes up, a default route points at the wrong bearer, the pool overlaps a real interface, or public-to-private isolation is assumed without a negative test.
- Implementation order: Establish PPPoE session and negotiated address; verify peer reachability; install default route; apply source policy/NAT; test positive internal-to-public and negative unsolicited public-to-private paths.
- Verification method: Inspect session and negotiated address, routing table and NAT binding, then run both positive and negative reachability assertions. Because this rule is candidate and platform-sensitive, do not generalize support beyond the verified target.

## DR-WAN-001: Resolve serial identity and address conflicts before protocol claims
- Status: candidate
- Tags: wan, serial, hdlc, addressing, static-route, conflict
- Evidence level: candidate; exclude from normal projects until independently validated.
- Requires: `interface-map-confirmed`, `topology-baseline-confirmed`
- Provides: `layer3-adjacency-ready`
- Trigger: A serial WAN design depends on slot/index mapping, point-to-point addressing, and a link protocol such as HDLC.
- Design goal: Make the physical interface identity, peer addresses, link protocol, and static path mutually consistent before claiming WAN reachability.
- Decision logic: Map topology indexes to actual serial interfaces; preserve source values; resolve duplicate or incomplete interface/address commands with user confirmation or runtime evidence; configure the link protocol on both peers; then inspect serial state and route reachability.
- Recompute parameters: Serial interface names, peer network/address pair, protocol, static next hop, Ethernet edge networks, and endpoint tests.
- Applicability boundary: Candidate while a source conflict is unresolved or PC/runtime route evidence is absent; normalization alone is not approval.
- Common failure: Both WAN endpoints use the same address, a protocol is configured on only one side, or an inferred interface mapping is treated as runtime fact.
- Implementation order: Confirm slot/index mapping; resolve addresses; configure both link peers and protocol; inspect interface/protocol state; then verify static route and endpoint reachability.
- Verification method: Correlate topology, interface identity, address uniqueness, serial/HDLC state, route table, and reachability.

## DR-PPP-003: Treat PAP-to-CHAP changes as sequential phases on one link
- Status: candidate
- Tags: ppp, pap, chap, authentication, transition
- Evidence level: candidate; exclude from normal projects until independently validated.
- Requires: `interface-map-confirmed`, `platform-support-confirmed`
- Provides: `authentication-transition-ready`
- Trigger: A PPP link must be tested with PAP and then reconfigured for CHAP.
- Design goal: Keep authentication roles, credentials, cleanup, and reachability assertions tied to the active phase rather than combining incompatible final states.
- Decision logic: Establish the server/client role and routing baseline; configure and verify PAP; remove PAP state; configure CHAP on the same link; verify CHAP and the required end-to-end path; record any AAA/domain conflict before trusting the phase result.
- Recompute parameters: Link endpoints, server/client roles, authentication method, AAA domain, local-user identity, cleanup operation, and phase-specific reachability evidence.
- Applicability boundary: Candidate until both phases have runtime authentication evidence and the domain/credential source is resolved; PAP and CHAP are not simultaneous final configuration.
- Common failure: PAP residue remains during CHAP, a source domain typo is silently changed without confirmation, or a Ping is used without proving authentication state.
- Implementation order: Verify underlay/OSPF; configure PAP and test; cleanly remove PAP; configure CHAP and test; then verify downstream reachability.
- Verification method: Capture PPP authentication state and interface/route/reachability evidence separately for each phase.

## DR-IPSEC-001: Match both ends of the IPsec traffic selector
- Status: validated
- Tags: ipsec, selector, acl, site-to-site, security-policy
- Evidence level: source-derived design constraint; confirm target-platform support and runtime behavior.
- Requires: `internal-routing-ready`, `return-path-defined`
- Provides: `vpn-selector-ready`
- Trigger: A site-to-site IPsec policy protects traffic between two private prefixes.
- Design goal: Ensure both peers classify the same bidirectional traffic for encryption.
- Decision logic: Derive source/destination selectors from the current topology; compare the reverse selector on the peer; keep routing and NAT exceptions aligned with the selector.
- Recompute parameters: Local/remote prefixes, direction, peer addresses, ACL/rule order, return path, and NAT match/exemption.
- Applicability boundary: A matching ACL object alone does not prove an active SA or encrypted business flow; verify target platform selector semantics.
- Common failure: One side reverses or narrows the selector, a local subnet is omitted, or NAT changes the packet before IPsec classification.
- Implementation order: Confirm underlay; define both selectors; align route/NAT; attach policy; inspect SA; test bidirectional protected traffic.
- Verification method: Compare selectors, SA endpoints, encrypted counters/ESP, and bidirectional business reachability.

## DR-IPSEC-002: Keep IKE and IPsec proposals paired across both peers
- Status: validated
- Tags: ipsec, ike, proposal, authentication, algorithm
- Evidence level: source-derived design constraint; confirm target-platform support and runtime behavior.
- Requires: `platform-support-confirmed`
- Provides: `vpn-negotiation-ready`
- Trigger: IPsec uses manual parameters or IKE negotiation between two peers.
- Design goal: Prevent a complete-looking policy from failing because one side's authentication, encryption, integrity, DH, or encapsulation parameters differ.
- Decision logic: Record the selected IKE and IPsec suites as explicit tuples; compare both peers; ensure the policy references the intended proposals/peer; only then interpret SA state.
- Recompute parameters: IKE version, authentication method/material, encryption/integrity algorithms, DH group, encapsulation, peer address, proposal identifiers, and policy reference.
- Applicability boundary: Algorithm support and command hierarchy vary by device/version; do not infer interoperability from vendor naming alone.
- Common failure: IKE parameters match but IPsec proposal differs, a policy references the wrong proposal, or a manual SPI/key is asymmetric.
- Implementation order: Confirm platform support; define IKE; define IPsec proposal; bind peer/policy; apply interface; inspect SA and counters.
- Verification method: Compare both configurations, negotiation/SA state, algorithm display, and encrypted traffic.

## DR-IPSEC-003: Plan routing, NAT exemption, and tunnel policy as one dependency chain
- Status: validated
- Tags: ipsec, nat, route, default-route, exemption, packet-processing-order
- Evidence level: source-derived design constraint; confirm target-platform support and runtime behavior.
- Requires: `vpn-selector-ready`, `vpn-negotiation-ready`, `egress-route-resolved`, `return-path-defined`, `packet-processing-order-defined`
- Provides: `vpn-policy-ready`
- Trigger: IPsec and Internet access share an edge device with default routing or source NAT.
- Design goal: Keep protected site traffic un-NATed while allowing unrelated Internet traffic to use NAT.
- Decision logic: Derive protected and non-protected flows; make the VPN selector take precedence over NAT matching; verify forward and return routes; then test one flow from each class.
- Recompute parameters: Protected prefixes, NAT permit/deny order, default route, return route, egress interface, and non-VPN test destination.
- Applicability boundary: Processing order differs across platforms; confirm whether policy NAT, ACL NAT, and IPsec classification use the assumed order.
- Common failure: VPN traffic is translated, a broad NAT rule hides an exemption, or the tunnel works while non-VPN egress is broken.
- Implementation order: Underlay/routes; selectors; NAT exception; remaining NAT; policy attachment; SA; protected and non-protected tests.
- Verification method: Correlate route table, NAT/session match, SA counters, and protected/non-protected reachability.

## DR-IPSEC-004: Verify IPsec in layers rather than using one Ping
- Status: validated
- Tags: ipsec, verification, sa, counters, packet-capture
- Evidence level: source-derived design constraint; confirm target-platform support and runtime behavior.
- Requires: `vpn-policy-ready`
- Provides: `vpn-validation-ready`
- Trigger: A configuration is being evaluated as an IPsec success.
- Design goal: Distinguish underlay reachability, negotiation, encryption, and application success.
- Decision logic: Check peer reachability; check policy/SA state; check bidirectional encrypted counters or ESP; check business reachability; record any layer that is missing.
- Recompute parameters: Peer test addresses, protected flow, expected SA directions, counter baseline, capture interface, and application test.
- Applicability boundary: A Ping can pass without using the intended tunnel, and an SA can exist without a usable return path; require the layer-specific evidence.
- Common failure: Only the final Ping is recorded, or a static SA is mistaken for data-plane encryption.
- Implementation order: Underlay; policy/SA; counters/capture; protected flow; reverse flow; teardown/recovery if required.
- Verification method: Report each layer as observed, pending, or failed with the exact command/output or capture evidence.
