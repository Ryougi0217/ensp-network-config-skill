# Design Rule Index

Use this file to choose the rule catalog for the current project. Rules are portable design constraints, not command templates. Recompute device names, ports, VLANs, addresses, IDs, priorities, costs, and scripts from the current topology and requirements.

## Loading workflow

1. Identify the task's design domains and protocol tags.
2. Read only the matching catalogs below.
3. Use a rule only when its trigger and applicability boundary match the confirmed topology and requirements.
4. Recompute every item under `Recompute parameters` from current project evidence. Do not copy case-specific values, command text, credentials, captured output, or conclusions.
5. If no rule matches, continue from confirmed evidence and protocol knowledge, and strengthen the verification plan for that part of the design.

## Catalogs

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
