# Transferable Design Rule Index

Use this file to select design-rule catalogs. Rules are portable design constraints, not command templates. A case is evidence, not a source of fixed device names, ports, VLANs, addresses, IDs, priorities, costs, or scripts.

## Loading workflow

1. Identify the current task's design domains and protocol tags.
2. Read only the matching active catalogs below. Do not load every catalog by default.
3. Use only rules whose `Status` is `validated` and whose trigger and applicability boundary match the confirmed topology and requirements.
4. Recompute every item under `Recompute parameters` from the current project evidence. Never copy case-specific identifiers, addresses, interfaces, credentials, command text, topology placement, model-support assumptions, captured outputs, timestamps, or pass/fail conclusions.
5. If no active catalog matches, solve from confirmed evidence and protocol knowledge; do not invent a validated rule.

## Active catalogs

| Design domain | Catalog | Primary tags |
|---|---|---|
| Campus Layer 2 | [campus-layer2.md](design-rules/campus-layer2.md) | mac, vlan, trunk, stp, rstp, mstp, lacp, smart-link |
| Platform Infrastructure | [platform-infrastructure.md](design-rules/platform-infrastructure.md) | poe, hardware, power, stacking, istack, change-safety |
| IP Foundation and Services | [ip-foundation-services.md](design-rules/ip-foundation-services.md) | ipv4, arp, proxy-arp, dhcp, dhcpv6 |
| Gateway and Edge | [gateway-edge.md](design-rules/gateway-edge.md) | vlanif, inter-vlan, vrrp, gateway, nat |
| OSPF | [ospf.md](design-rules/ospf.md) | ospf, multiarea, nssa, stub, abr |
| WAN and Tunneling | [wan-tunneling.md](design-rules/wan-tunneling.md) | ppp, pppoe, gre, ipsec, authentication, nat-edge |
| Routing Policy | [routing-policy.md](design-rules/routing-policy.md) | static-route, rip, redistribution, prefix-filter, route-policy, pbr |
| Resilience and OAM | [resilience-oam.md](design-rules/resilience-oam.md) | redundancy, failure, bfd, track, nqa, vrrp, oam, verification |
| Security and Access | [security-access.md](design-rules/security-access.md) | acl, management-access, dhcp-snooping, ipsg, source-guard |
| Operations and Automation | [operations-automation.md](design-rules/operations-automation.md) | snmp, nms, mib, trap, inform, management |
| QoS and Traffic Engineering | [qos-traffic-engineering.md](design-rules/qos-traffic-engineering.md) | qos, mqc, classifier, behavior, traffic-policy, policing, statistics |
| Wireless | [wireless.md](design-rules/wireless.md) | wlan, ac, ap, capwap, ssid, vap, wireless-vlan |

## Reserved routes

These routes are inactive. Do not ship a catalog file for a reserved route until it contains at least one evaluated rule. Do not load reserved routes in normal projects or list them under Active catalogs until at least one rule is `validated` and its portable evidence level is recorded in the catalog.

Existing reserved catalog files use the listed basename under
`references/design-rules/`. A listed route with no file remains an empty
placeholder only.

| Design domain | Inactive catalog | Intended scope |
|---|---|---|
| BGP | `bgp.md` | IPv4/IPv6 BGP, MP-BGP, RR, confederation, policy, RPKI |
| IS-IS | `isis.md` | IPv4/IPv6 IS-IS design and convergence |
| Multicast | `multicast.md` | IGMP/MLD, PIM, RP, RPF, SSM |
| MPLS and VPN | `mpls-vpn.md` | MPLS, LDP, L2VPN/L3VPN, traditional TE |
| Data-Center Overlay | `overlay-datacenter.md` | EVPN, VXLAN, multihoming, anycast gateway, M-LAG |
| Segment Routing | `segment-routing.md` | SR-MPLS, SRv6, SR Policy |

## Rule ownership

- Store each rule in exactly one primary catalog; use tags for additional protocols and relationships.
- Choose ownership by the rule's design outcome: Layer-2 path selection belongs to Campus Layer 2, gateway behavior to Gateway and Edge, and failure coordination or proof to Resilience and OAM.
- Keep rule IDs stable when moving or refining rules.
- Split a catalog only when it becomes difficult to scan, normally around 40-60 validated rules or 300-500 lines with stable subdomains.

## Rule status

- `candidate`: extracted and generalized, but unavailable to normal configuration projects.
- `validated`: passed the approved evaluation flow, or received explicitly authorized direct adoption with a portable evidence limitation recorded; available only when trigger and boundary match.
- `deprecated`: retained for traceability but unavailable to normal projects.

Industry relevance does not prove simulator support. For EVPN/VXLAN, Segment Routing, model-driven management, and other platform-sensitive features, confirm the target device model and VRP/eNSP capability before generating executable commands.
