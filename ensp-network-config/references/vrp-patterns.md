# Huawei VRP patterns

Use these as validation-oriented patterns, not as a command cookbook. Generate full commands in final output.

## Topic index

Use this index only after the project baseline and current stage design are confirmed. Read [Minimal command emission](#minimal-command-emission) plus only the sections that match the current stage; do not scan unrelated command patterns.

- **Foundation and campus:** [Interface addressing](#interface-addressing), [VLAN and port behavior](#vlan-and-port-behavior), [Eth-Trunk mode selection](#eth-trunk-mode-selection), [Layer 3 switching](#layer-3-switching)
- **Routing:** [OSPF](#ospf), [Static default and return-path pairing](#static-default-and-return-path-pairing), [RIPv2 method versus learned routes](#ripv2-method-versus-learned-routes), [BGP peer and address-family separation](#bgp-peer-and-address-family-separation), [IS-IS adjacency and route learning](#is-is-adjacency-and-route-learning)
- **Resilience and OAM:** [VRRP gateway ownership and transition](#vrrp-gateway-ownership-and-transition), [BFD-tracked path or gateway](#bfd-tracked-path-or-gateway), [NQA ICMP result](#nqa-icmp-result)
- **Addressing and access services:** [DHCP pool scope and phase boundaries](#dhcp-pool-scope-and-phase-boundaries), [DHCP relay dependency chain](#dhcp-relay-dependency-chain), [WLAN AC/AP template chain](#wlan-acap-template-chain)
- **Edge, security, and WAN:** [ACL data-plane placement](#acl-data-plane-placement), [PPPoE dependency chain](#pppoe-dependency-chain), [IPsec policy composition by keying mode](#ipsec-policy-composition-by-keying-mode), [IPsec and NAT coexistence](#ipsec-and-nat-coexistence), [Firewall zones and policy](#firewall-zones-and-policy-translation-is-conditional), [NAT service publication and hairpin review](#nat-service-publication-and-hairpin-review)
- **Traffic engineering and multicast:** [MQC classifier and policy attachment](#mqc-classifier-and-policy-attachment), [PIM/IGMP receiver path](#pimigmp-receiver-path)
- **Input normalization:** [Abbreviations](#abbreviations)

## Minimal command emission

Apply this rule globally to every protocol and service. First identify the
confirmed customer outcome, then derive the complete base and dependency chain
needed to achieve it, and finally add only the optional features that the
requirement, approved baseline, existing peer, or target platform explicitly
requires. A complete protocol configuration is the smallest working whole for
the requested behavior, not the protocol's maximum feature set.

Omit optional authentication, encryption, timers, network types,
redistribution, route injection, BFD/NQA tracking, hardening, logging, and
tuning when no requirement or dependency justifies them. Do not add a feature
merely because it is recommended in a reference case. For example, do not add
OSPF area or interface authentication when the customer did not require it and
the peers do not use it.

The same rule applies to housekeeping commands: `undo info-center enable`,
`undo shutdown`, and default-state cleanup are unnecessary unless the observed
starting state must change. If a potentially useful but unrequested option is
material to the requested outcome, raise it as a decision instead of silently
configuring it.

For any pattern that contains optional configuration, split it into a **base
block** and one or more **conditional feature blocks**, and keep execution or
inspection commands separate. A base block contains only the configuration
needed whenever the named behavior is selected. Emit a conditional feature
block only when the matching feature in the current scope's `feature_profiles`
entry is `required` or `selected`. Omit it when the feature is `omitted`, and
stop for a decision when it is `needs_confirmation`. A placeholder in a
conditional block is not permission to enable that feature.

## Interface addressing

```text
interface GigabitEthernet0/0/0
 ip address 192.168.0.1 255.255.255.0
```

Check that link endpoints share the expected subnet, host addresses are usable, and the interface name exists in the confirmed topology.

## VLAN and port behavior

```text
vlan batch 10 20
interface Ethernet0/0/1
 port link-type access
 port default vlan 10
interface Ethernet0/0/10
 port link-type trunk
 port trunk allow-pass vlan 10 20
```

For Hybrid ports, reason about ingress PVID and egress tagged/untagged membership separately. Validate both desired connectivity and desired isolation; a VLAN list alone does not prove the policy.

For an explicitly required parent/child fan-in design:

- An endpoint-facing port uses the child VLAN as its PVID and sends the parent
  plus its mapped child VLAN untagged.
- The local fan-in uplink uses the parent VLAN as its PVID and sends the parent
  plus all locally mapped child VLANs untagged.
- The peer side is an access port in the parent VLAN, and the upstream carries
  only the parent VLAN.
- Create a gateway/Vlanif only for the parent VLAN; child VLANs remain local.

Derive every mapping from the current topology. This pattern is not a generic
replacement for Trunk, MUX VLAN, Super-VLAN, or a policy-based isolation
design. Verify both directions, ARP, unicast, broadcast behavior, and the
required isolation boundaries.

## Eth-Trunk mode selection

For a requirement that says only `Eth-Trunk`, use the confirmed platform's
manual/default aggregation mode and omit `mode lacp-static`. Do not infer LACP
from a reference example. Add `mode lacp-static` only when the requirement
explicitly calls for LACP and both endpoints support the selected mode.

In either profile, confirm the bundle ID, member ports, peer-side membership,
allowed VLANs or Layer 3 addressing, and operational member state. Do not mix
manual and LACP profiles across the same link.

## Layer 3 switching

```text
interface Vlanif10
 ip address 192.168.10.1 255.255.255.0
```

Confirm that the VLAN exists, required trunks carry it, hosts use the correct gateway, and routing between Vlanifs is intended.

For a switch-to-router Layer 3 link, use a switched access link plus Vlanif as
the default design: keep the physical switch interface in Layer 2 access mode,
assign it to a dedicated transit VLAN, and place the IP address on that VLAN's
Vlanif. Carry only the required transit VLAN on that link.

Use a routed physical switch port with `undo portswitch` only when the user
explicitly requires that model. Never select it merely because a reference
case uses it. Do not combine the two models on one link, and do not silently
fall back to a routed physical port when the preferred Vlanif model is
unsupported; report the platform conflict for decision.

## OSPF

```text
ospf 1 router-id 1.1.1.1
 area 0
  network 10.0.0.0 0.0.0.3
```

Check:

- Router IDs are unique within the OSPF domain.
- Each point-to-point link uses one subnet at both endpoints.
- Wildcard masks correspond to the intended prefixes.
- Area 0 is continuous.
- Non-backbone areas attach to Area 0 through an ABR.
- Required LAN and Loopback prefixes are advertised.
- Every required neighbor has compatible area and subnet settings.
- A `/30` Ethernet subnet does not by itself require `ospf network-type p2p`.
  Add that command only when the topology, peer settings, or platform behavior
  explicitly requires the point-to-point network type.
- Omit authentication, special-area options, custom timers, silent-interface,
  route import/default injection, and OSPF-linked BFD unless a confirmed
  requirement or mandatory dependency calls for them. Their availability is
  not a reason to configure them.

## DHCP pool scope and phase boundaries

Base global-pool block:

    dhcp enable
    ip pool <pool-name>
     network <client-prefix> mask <mask>
    interface Vlanif<id>
     dhcp select global

Conditional feature block -- `dhcp-client-gateway` for routed client access:

    ip pool <pool-name>
     gateway-list <gateway-address>

Conditional feature block -- `dhcp-dns-option`:

    ip pool <pool-name>
     dns-list <dns-address> ...

Conditional feature block -- `dhcp-address-exclusion` for reservation or
conflict avoidance:

    ip pool <pool-name>
     excluded-ip-address <first-excluded> <last-excluded>

For an interface address pool, use dhcp select interface and keep
interface-pool options under that SVI. Treat global-pool and interface-pool
experiments as separate phases: clear or document the transition, then verify
the client lease and only the options selected for the active phase. Do not add
gateway, DNS, exclusions, or a non-default lease merely because the platform
supports them.

## Static default and return-path pairing

    ip route-static 0.0.0.0 0 <forward-next-hop>
    ip route-static <inside-prefix> <mask> <return-next-hop>

A default route on one device does not establish the return path. Derive
forward and reverse obligations from the current topology, inspect both route
tables, and use path output only for the exact source/destination pair tested.

## RIPv2 method versus learned routes

Base block:

    rip <process-id>
     version 2
     network <major-network>

Conditional feature block -- `rip-disable-summary`, only when the required
prefix visibility, discontiguous topology, or peer behavior needs it:

    rip <process-id>
     undo summary

Record the protocol version, process scope, and advertised networks separately
from peer state and learned-route output. Do not claim convergence from a
configuration snippet or from a title-only reference to RIPv2. Do not emit
`undo summary` as generic RIPv2 boilerplate.

## VRRP gateway ownership and transition

Base group block:

    interface Vlanif<id>
     vrrp vrid <vrid> virtual-ip <virtual-ip>

Conditional feature block -- `vrrp-explicit-priority`, only on peers whose
priority must differ from the platform default for the selected ownership:

    interface Vlanif<id>
     vrrp vrid <vrid> priority <priority>

Recompute the real SVI addresses, virtual IP, VRID, priorities, and client
gateway for each VLAN. Omit an explicit priority when no requested ownership or
load-sharing outcome requires it. A priority change can demonstrate a role transition,
but it is not equivalent to the required gateway/link failure and recovery
test; capture normal, fault, and restored states separately.

## BFD-tracked path or gateway

    bfd
    bfd <session-name> bind peer-ip <peer-ip> source-ip <source-ip>
     discriminator local <local-id>
     discriminator remote <remote-id>
     commit
    ip route-static <destination-prefix> <mask> <next-hop> track bfd-session <session-name>

Derive the real local upstream paths first and create a session for every
relevant upstream that the requirement expects to detect. A BFD session to a
peer switch or interconnect does not substitute for monitoring the actual
upstream path. Attach each session to the intended static route, gateway
tracking object, or other supported consumer, and choose decrement or
withdrawal behavior from the required fault outcome.

This pattern is platform- and simulator-sensitive. Keep default timers unless
the requirement or verified convergence target demands otherwise. Verify the
session state and intended route/gateway behavior in normal state, after each
named single fault, after required multiple faults, and after restoration.
One-arm echo is a separate capability.

## ACL data-plane placement

Trace the protected flow in both directions before choosing an attachment
point. Source-facing ingress, shared-uplink outbound, and protected-destination
outbound can all be valid when the ACL sees the intended original tuple and no
alternate path bypasses it. Prefer the smallest attachment set that is clear,
auditable, and sufficient for the requirement.

Physical-interface attachment may be a project-specific boundary, but it is
not a universal prohibition on Vlanif or policy-context attachment. Verify the
actual platform syntax, direction, tuple visibility, counters, intended denied
flow, intended permitted flow, reverse direction, and bypass paths. One failed
Ping proves only that exact reachability assertion; it does not prove every
protocol or isolation requirement.

## PPPoE dependency chain

Server-side pattern:

    aaa
     local-user <user> password <storage-form> <secret>
     local-user <user> service-type ppp
    ip pool <pool-name>
     network <subscriber-prefix> mask <mask>
     gateway-list <gateway-address>
    interface Virtual-Template<template-id>
     ppp authentication-mode <pap-or-chap>
     remote address pool <pool-name>
     ip address <gateway-address> <mask>
    interface <server-bearer-interface>
     pppoe-server bind virtual-template <template-id>

Client-side pattern:

    dialer-rule
     dialer-rule <rule-id> ip permit
    interface Dialer<dialer-id>
     link-protocol ppp
     ppp <pap-or-chap> local-user <user> password <storage-form> <secret>
     ip address ppp-negotiate
     dialer user <user>
     dialer bundle <bundle-id>
     dialer-group <rule-id>
    interface <client-bearer-interface>
     pppoe-client dial-bundle-number <bundle-id>

Treat AAA identity and service authorization, address pool, Virtual-Template,
bearer binding, dialer rule/group/bundle, authentication, and negotiated
addressing as one chain. Add default routing and NAT only after the PPPoE
session requirement is satisfied. Verify discovery/session state,
authentication, negotiated address, routes, return path, and service traffic;
do not infer success from configuration presence alone.

## NQA ICMP result

Base probe block:

    nqa test-instance <admin-name> <test-name>
     test-type icmp
     destination-address ipv4 <destination>

Conditional feature block -- `nqa-sampling-tuning`, selected by a convergence
or measurement requirement:

    nqa test-instance <admin-name> <test-name>
     frequency <seconds>
     probe-count <count>

Execution and inspection:

    nqa test-instance <admin-name> <test-name>
     start now
    display nqa results test-instance <admin-name> <test-name>

Use the result as evidence for the exact probe and time window. A successful
sample or zero-loss result is not a general service-level objective and should
not be reused as a current performance guarantee. Keep platform defaults for
sampling unless the feature profile selects explicit values.

## Abbreviations

Accept common lab abbreviations such as `int`, `ip ad`, `v b`, `a`, and `n` as input. Expand them in final configurations to improve reviewability.

## IPsec policy composition by keying mode

    acl <selector-id>
     rule <sequence> permit ip source <local-prefix> <wildcard> destination <remote-prefix> <wildcard>
    ipsec proposal <proposal-name>
     esp authentication-algorithm <integrity-algorithm>
     esp encryption-algorithm <encryption-algorithm>

Select exactly one `ipsec-keying-mode` for a tunnel scope.

Manual keying pattern:

    ipsec policy <policy-name> <sequence> manual
     security acl <selector-id>
     proposal <proposal-name>
     tunnel local <local-peer-address>
     tunnel remote <remote-peer-address>
     sa spi inbound esp <inbound-spi>
     sa spi outbound esp <outbound-spi>
     sa string-key inbound esp <storage-form> <inbound-key>
     sa string-key outbound esp <storage-form> <outbound-key>

IKE keying pattern:

    ike proposal <ike-proposal-id>
     authentication-method <authentication-method>
     authentication-algorithm <authentication-algorithm>
     encryption-algorithm <encryption-algorithm>
     dh <dh-group>
    ike peer <peer-name> <target-version-form>
     pre-shared-key <storage-form> <secret>
     remote-address <remote-peer-address>
     ike-proposal <ike-proposal-id>
    ipsec policy <policy-name> <sequence> isakmp
     security acl <selector-id>
     proposal <proposal-name>
     ike-peer <peer-name>

Common attachment and inspection:

    interface <egress-interface>
     ipsec policy <policy-name>
    display ipsec sa brief

Never emit IKE objects in manual mode or manual SPI/key commands in IKE mode.
For manual keying, local outbound SPI/key must equal the peer's inbound values,
and local inbound values must equal the peer's outbound values. For IKE, match
the selected IKE and IPsec suites, authentication material, peer identities,
and references at both ends. Treat the selector, selected keying branch,
proposal, policy reference, interface, underlay route, and return route as one
dependency chain. Verify peer reachability, both SA directions, encrypted
counters/ESP, and the protected business flow separately.

## IPsec and NAT coexistence

    acl <vpn-selector-id>
     rule <sequence> permit ip source <local-prefix> <wildcard> destination <remote-prefix> <wildcard>
    acl <nat-selector-id>
     rule <sequence> deny ip source <local-prefix> <wildcard> destination <remote-prefix> <wildcard>
     rule <later-sequence> permit ip source <internet-source-scope> <wildcard>
    interface <egress-interface>
     nat outbound <nat-selector-id>

Use platform-specific NAT-exemption or deny-first semantics only after confirming
the processing order. Verify one protected flow and one non-protected NAT flow;
do not infer the exemption from a successful SA alone.

## Firewall zones and policy; translation is conditional

Base zone and permit-policy block:

    firewall zone <zone-name>
     add interface <interface>
    security-policy
     rule name <rule-name>
      source-zone <source-zone>
      destination-zone <destination-zone>
      source-address <source-scope>
      destination-address <destination-scope>
      action permit

Conditional feature block -- `firewall-source-nat`, selected for this flow:

    nat-policy
     rule name <nat-rule-name>
      source-zone <source-zone>
      destination-zone <destination-zone>
      action source-nat <translation-object>

Do not add `nat-policy` merely because an inter-zone permit exists. For server
publication, use the target firewall's server-mapping syntax and pair it with
an exact untrust-to-DMZ permit. NAT transforms addresses; it does not replace
the security policy. Verify policy match, translated session when selected,
and an explicit negative service or direction.

## WLAN AC/AP template chain

    interface Vlanif<management-vlan>
     ip address <management-gateway> <mask>
    capwap source interface Vlanif<management-vlan>
    wlan
     security-profile name <security-profile>
     ssid-profile name <ssid-profile>
      ssid <ssid>
     vap-profile name <vap-profile>
      forward-mode <tunnel-or-direct>
      service-vlan vlan-id <service-vlan>
      security-profile <security-profile>
      ssid-profile <ssid-profile>
     ap-group name <ap-group>
      vap-profile <vap-profile> wlan <wlan-id> radio <radio-id>
    display ap all

The exact AC syntax is model/version dependent. Keep management VLAN,
service VLAN, security, SSID, VAP, AP-group, and radio references explicit.
`display ap all` proves AP control-plane state only; verify STA association,
DHCP/gateway, and egress as separate assertions.

## DHCP relay dependency chain
    dhcp enable
    dhcp server group <group-id>
     server <dhcp-server-address>
    interface Vlanif<client-vlan>
     dhcp select relay
     dhcp relay server-select <group-id>
    display dhcp relay
Confirm client-to-relay and server return routes; keep relay and local-pool phases separate.
## NAT service publication and hairpin review

Base publication block:

    nat server <target-platform-mapping> global <public-service> inside <server-service>

Conditional feature block -- `nat-dns-alg`, selected and supported for the
named protocol:

    nat alg dns enable

Conditional feature block -- `nat-dns-map`, selected for inside DNS mapping or
hairpin-name access:

    nat dns-map <public-name> <inside-address>

Conditional feature block -- `nat-outbound`, selected on the resolved egress:

    nat outbound <source-selector>

Treat mapping, DNS/ALG, inside exception, authorization, and outbound
translation as separate features. Do not emit one because another is selected;
test only the required inside, outside, and negative-service flows.

## MQC classifier and policy attachment
    traffic classifier <classifier> operator or
     if-match acl <acl-id>
    traffic behavior <behavior>
     <police-or-remark-action>
    traffic policy <policy>
     classifier <classifier> behavior <behavior>
    interface <visible-direction-interface>
     traffic-policy <policy> inbound|outbound
    display traffic-policy statistics interface <interface>
Attach where the original identity is visible; check direction, interface budget, counters, and an unaffected flow.

## BGP peer and address-family separation

Base peer and address-family block:

    bgp <local-as>
     peer <peer-address> as-number <peer-as>
     ipv4-family unicast
      peer <peer-address> enable

Conditional feature block -- `bgp-explicit-router-id`:

    bgp <local-as>
     router-id <router-id>

Conditional feature block -- `bgp-route-policy` for selected import or export
control:

    bgp <local-as>
     ipv4-family unicast
      peer <peer-address> route-policy <policy> import|export

Inspection:

    display bgp peer
    display ip routing-table protocol bgp
Keep underlay, session, AF, optional policy, optional next-hop handling, and
selected route as separate evidence layers. Do not attach a policy or rewrite
the next hop without a selected route-control outcome.

## IS-IS adjacency and route learning

Base adjacency block:

    isis <process-id>
     network-entity <net>
    interface <transit-interface>
     isis enable <process-id>

Conditional feature block -- `isis-explicit-level`, when an explicit level is
needed to express the selected area design or match peers instead of relying on
the platform default:

    isis <process-id>
     is-level <level-1|level-2|level-1-2>

Inspection:

    display isis peer
    display ip routing-table protocol isis
Recompute NET/area/level and interface set. Omit an explicit level when the
selected design already matches the confirmed platform default; do not infer
learned routes from configuration alone.

## PIM/IGMP receiver path

Common base block:

    multicast routing-enable
    interface <receiver-interface>
     igmp enable

Select exactly one `pim-forwarding-profile` per routed multicast domain. Apply
its interface command to every routed interface that must participate in that
domain; do not mix profiles inside the same domain.

`dm` branch:

    interface <pim-interface>
     pim dm

Do not configure an RP in the `dm` branch.

`sm-static-rp` branch:

    interface <pim-interface>
     pim sm
    pim
     static-rp <rp-address>

Use the same reachable RP and applicable group scope on every participating SM
router. Do not add BSR candidate roles in this branch.

`sm-bsr` branch:

    interface <pim-interface>
     pim sm
    pim
     c-bsr <candidate-bsr-interface>
     c-rp <candidate-rp-interface>

Configure candidate BSR/RP roles only on the selected devices, verify the
target platform's exact syntax, and do not add `static-rp` in this branch.

`sm-bsr-static-backup` branch -- only when RP fallback is explicitly required:

    interface <pim-interface>
     pim sm
    pim
     c-bsr <candidate-bsr-interface>
     c-rp <candidate-rp-interface>
     static-rp <backup-rp-address>

Configure candidate roles only on the selected devices and the same static RP
on every participating router. Confirm the target platform's RP precedence;
do not add `preferred` unless the static RP is intentionally selected as
primary rather than backup.

`sm-ssm` branch:

    interface <receiver-interface>
     igmp version 3
    interface <pim-interface>
     pim sm

Use the confirmed SSM group range and source-aware receiver behavior. SSM does
not use an RP; add a non-default SSM policy only when the feature profile
selects one.

Common inspection:

    display pim interface
    display pim routing-table
    display igmp group

Verify unicast RPF, the selected profile, receiver membership, and forwarding
separately; inspect RP consistency only for the three SM-ASM profiles.
Control-plane state is not delivery proof.
