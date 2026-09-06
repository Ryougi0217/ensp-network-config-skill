# WAN and Tunneling Design Rules

Read these rules for PPP, PPPoE, GRE, IPsec, and related WAN dependency decisions. Match the access role, authentication method, and platform support before use.

## DR-PPP-001: Keep PPP authentication roles explicit before validating reachability
- Tags: ppp, pppoe, pap, chap, aaa, authentication
- Requires: `interface-map-confirmed`, `platform-support-confirmed`
- Provides: `wan-session-ready`
- Trigger: A point-to-point PPP or PPPoE link requires PAP/CHAP or equivalent subscriber authentication.
- Design goal: Make the authentication direction, credential ownership, and dependent link state unambiguous before using the link for routing or services.
- Decision logic: Identify the server/authenticator and client/supplicant from the topology. For PPPoE, keep the server AAA user/service, address pool, Virtual-Template, authentication mode, and bearer binding complete; keep the client `dialer-rule`, Dialer interface, `dialer user`, bundle, `dialer-group`, credentials, negotiated address, and bearer `pppoe-client` binding complete. Add default routing and NAT only when the client role requires them.
- Recompute parameters: Server/client roles, authentication method, user identity, credential storage form, address pool and gateway, bearer interface, dialer-rule/group/bundle, Dialer/Virtual-Template identifiers, address negotiation, default route, and NAT scope.
- Applicability boundary: Reassess when the link is not PPP/PPPoE, when authentication is delegated externally, or when the target VRP/eNSP version changes supported syntax.
- Common failure: Both peers act as clients, the server lacks a PPP service user or pool binding, the client omits `dialer-rule` or `dialer-group`, PAP/CHAP methods disagree, or NAT/default routing masks a missing session.
- Implementation order: Confirm bearer and addressing; configure the complete server AAA/pool/Virtual-Template chain; configure the complete client dialer rule/interface/group/bundle and bearer binding; verify session and negotiated address; only then add routing, NAT, or application tests.
- Verification method: Check the negotiated/session state and authentication role, then run a positive peer or downstream reachability test. Do not infer session success from a complete-looking configuration alone.

## DR-IPSEC-001: Match both ends of the IPsec traffic selector
- Tags: ipsec, selector, acl, site-to-site, security-policy
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

## DR-IPSEC-002: Choose one IPsec keying mode and keep both peers symmetric
- Tags: ipsec, ike, manual, keying, proposal, authentication, algorithm
- Requires: `platform-support-confirmed`
- Provides: `vpn-keying-ready`
- Trigger: A site-to-site IPsec policy uses either manually configured SA parameters or IKE negotiation between two peers.
- Design goal: Select one keying model and keep both peers' algorithms, identities, and directional parameters symmetric without mixing manual and negotiated state.
- Decision logic: Select exactly one `ipsec-keying-mode` for the tunnel scope. In `manual` mode, configure no IKE peer/proposal; pair each local outbound SPI/key with the remote inbound SPI/key and each local inbound SPI/key with the remote outbound values. In `ike` mode, configure no manual SPI/key; match IKE version, authentication material, IKE suite, IPsec proposal, peer identity/address, and policy references across both peers. Interpret SA state only after the selected branch is complete.
- Recompute parameters: Keying mode, peer addresses, IPsec encryption/integrity algorithms, encapsulation, proposal and policy identifiers; for manual mode, both directional SPI/key pairs; for IKE mode, IKE version, authentication method/material, encryption/integrity suite, DH group, and peer/proposal references.
- Applicability boundary: Do not combine manual and IKE keying in one policy scope. Confirm target device/version command hierarchy and algorithm support; do not infer the mode or suite from a reference example.
- Common failure: A manual policy also contains IKE objects, an IKE policy retains manual SPI/key commands, directional manual values are not inverse-matched across peers, or the IKE and IPsec suites differ between peers.
- Implementation order: Confirm platform support and select the keying mode; define the common IPsec proposal; configure only the manual SA branch or only the IKE branch; bind the selected policy; apply the interface; inspect SA, algorithms, and counters.
- Verification method: Confirm the selected mode and absence of the opposite branch, compare both peers' common proposal plus mode-specific parameters, then inspect SA state, encrypted counters/ESP, and protected traffic.

## DR-IPSEC-003: Plan routing, NAT exemption, and tunnel policy as one dependency chain
- Tags: ipsec, nat, route, default-route, exemption, packet-processing-order
- Requires: `vpn-selector-ready`, `vpn-keying-ready`, `egress-route-resolved`, `return-path-defined`, `packet-processing-order-defined`
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
- Tags: ipsec, verification, sa, counters, packet-capture
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
