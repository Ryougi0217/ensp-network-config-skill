# Transferable Design Rule Index

Use this file to select design-rule catalogs. Rules are portable design constraints, not command templates. A case is evidence, not a source of fixed device names, ports, VLANs, addresses, IDs, priorities, costs, or scripts.

## Loading workflow

1. Identify the current task's design domains and protocol tags.
2. Read only the matching active catalogs below. Do not load every catalog by default.
3. Use only rules whose `Status` is `validated` and whose trigger and applicability boundary match the confirmed topology and requirements.
4. Recompute every parameter from the current project evidence.
5. If no active catalog matches, solve from confirmed evidence and protocol knowledge; do not invent a validated rule.

## Active catalogs

| Design domain | Catalog | Primary tags |
|---|---|---|
| Campus Layer 2 | [campus-layer2.md](design-rules/campus-layer2.md) | mac, vlan, trunk, stp, rstp, mstp, lacp, smart-link |
| Gateway and Edge | [gateway-edge.md](design-rules/gateway-edge.md) | vlanif, inter-vlan, vrrp, gateway, nat |
| Resilience and OAM | [resilience-oam.md](design-rules/resilience-oam.md) | redundancy, failure, bfd, track, nqa, vrrp, oam, verification |

## Reserved routes

These routes define the future taxonomy. Their catalog files exist as empty placeholders to keep later batch classification stable. Do not load them or list them under Active catalogs until at least one rule has passed the approved case-learning and validation flow.

| Design domain | Future catalog | Intended scope |
|---|---|---|
| IP Foundation and Services | `ip-foundation-services.md` | IPv4/IPv6, ARP/NDP, ICMP, SLAAC, DHCP/DHCPv6 |
| Routing Policy | `routing-policy.md` | Static routes, RIP/RIPng, redistribution, prefix/route policy, PBR |
| OSPF | `ospf.md` | OSPFv2/OSPFv3 design and convergence |
| BGP | `bgp.md` | IPv4/IPv6 BGP, MP-BGP, RR, confederation, policy, RPKI |
| IS-IS | `isis.md` | IPv4/IPv6 IS-IS design and convergence |
| Multicast | `multicast.md` | IGMP/MLD, PIM, RP, RPF, SSM |
| MPLS and VPN | `mpls-vpn.md` | MPLS, LDP, L2VPN/L3VPN, traditional TE |
| WAN and Tunneling | `wan-tunneling.md` | PPP/PPPoE, GRE, IPsec/IKEv2, legacy Frame Relay |
| Security and Access | `security-access.md` | ACL, AAA, 802.1X, RADIUS/HWTACACS, device and control-plane security |
| Operations and Automation | `operations-automation.md` | SSH, SNMP, Syslog, NTP, NETCONF/YANG, RESTCONF, gNMI, telemetry |
| Data-Center Overlay | `overlay-datacenter.md` | EVPN, VXLAN, multihoming, anycast gateway, M-LAG |
| Segment Routing | `segment-routing.md` | SR-MPLS, SRv6, SR Policy |
| QoS and Traffic Engineering | `qos-traffic-engineering.md` | Classification, marking, policing, shaping, queuing, congestion, TE |

Reserve `sdn-sdwan.md` and `wireless.md` only if the Skill's supported scope expands beyond traditional routing, switching, and services.

## Rule ownership

- Store each rule in exactly one primary catalog; use tags for additional protocols and relationships.
- Choose ownership by the rule's design outcome: Layer-2 path selection belongs to Campus Layer 2, gateway behavior to Gateway and Edge, and failure coordination or proof to Resilience and OAM.
- Keep rule IDs stable when moving or refining rules.
- Split a catalog only when it becomes difficult to scan, normally around 40-60 validated rules or 300-500 lines with stable subdomains.

## Rule status

- `candidate`: extracted and generalized, but unavailable to normal configuration projects.
- `validated`: passed the approved evaluation flow and available when trigger and boundary match.
- `deprecated`: retained for traceability but unavailable to normal projects.

Industry relevance does not prove simulator support. For EVPN/VXLAN, Segment Routing, model-driven management, and other platform-sensitive features, confirm the target device model and VRP/eNSP capability before generating executable commands.
