# Huawei VRP patterns

Use these as validation-oriented patterns, not as a command cookbook. Generate full commands in final output.

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

## Layer 3 switching

```text
interface Vlanif10
 ip address 192.168.10.1 255.255.255.0
```

Confirm that the VLAN exists, required trunks carry it, hosts use the correct gateway, and routing between Vlanifs is intended.

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

## DHCP pool scope and phase boundaries

    dhcp enable
    ip pool <pool-name>
     network <client-prefix> mask <mask>
     gateway-list <gateway-address>
     dns-list <dns-address> ...
     excluded-ip-address <first-excluded> <last-excluded>
    interface Vlanif<id>
     dhcp select global

For an interface address pool, use dhcp select interface and keep
interface-pool options under that SVI. Treat global-pool and interface-pool
experiments as separate phases: clear or document the transition, then verify
the client lease, gateway, DNS, and lease duration for the active phase.

## Static default and return-path pairing

    ip route-static 0.0.0.0 0 <forward-next-hop>
    ip route-static <inside-prefix> <mask> <return-next-hop>

A default route on one device does not establish the return path. Derive
forward and reverse obligations from the current topology, inspect both route
tables, and use path output only for the exact source/destination pair tested.

## RIPv2 method versus learned routes

    rip <process-id>
     version 2
     undo summary
     network <major-network>

Record the protocol version, process scope, and advertised networks separately
from peer state and learned-route output. Do not claim convergence from a
configuration snippet or from a title-only reference to RIPv2.

## VRRP gateway ownership and transition

    interface Vlanif<id>
     vrrp vrid <vrid> virtual-ip <virtual-ip>
     vrrp vrid <vrid> priority <priority>

Recompute the real SVI addresses, virtual IP, VRID, priorities, and client
gateway for each VLAN. A priority change can demonstrate a role transition,
but it is not equivalent to the required gateway/link failure and recovery
test; capture normal, fault, and restored states separately.

## BFD-tracked static route

    bfd
    bfd <session-name> bind peer-ip <peer-ip> source-ip <source-ip>
     discriminator local <local-id>
     discriminator remote <remote-id>
     commit
    ip route-static <destination-prefix> <mask> <next-hop> track bfd-session <session-name>

This pattern is platform- and simulator-sensitive. Verify the session state,
route presence, route withdrawal after the specified fault, and route
reinstallation after restoration before treating it as a reusable design
pattern. One-arm echo is a separate capability.

## NQA ICMP result

    nqa test-instance <admin-name> <test-name>
     test-type icmp
     frequency <seconds>
     probe-count <count>
     destination-address ipv4 <destination>
     start now
    display nqa results test-instance <admin-name> <test-name>

Use the result as evidence for the exact probe and time window. A successful
sample or zero-loss result is not a general service-level objective and should
not be reused as a current performance guarantee.

## Abbreviations

Accept common lab abbreviations such as `int`, `ip ad`, `v b`, `a`, and `n` as input. Expand them in final configurations to improve reviewability.

## IPsec policy composition and layered verification

    acl <selector-id>
     rule <sequence> permit ip source <local-prefix> <wildcard> destination <remote-prefix> <wildcard>
    ipsec proposal <proposal-name>
     esp authentication-algorithm <integrity-algorithm>
     esp encryption-algorithm <encryption-algorithm>
    ipsec policy <policy-name> <sequence> manual
     security acl <selector-id>
     proposal <proposal-name>
     tunnel local <local-peer-address>
     tunnel remote <remote-peer-address>
    interface <egress-interface>
     ipsec policy <policy-name>
    display ipsec sa brief

Treat the selector, proposal, policy reference, interface, underlay route, and
return route as one dependency chain. Verify peer reachability, both SA
directions, encrypted counters/ESP, and the protected business flow separately.

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

## Firewall zones, policy, and translation

    firewall zone <zone-name>
     add interface <interface>
    security-policy
     rule name <rule-name>
      source-zone <source-zone>
      destination-zone <destination-zone>
      source-address <source-scope>
      destination-address <destination-scope>
      action permit
    nat-policy
     rule name <nat-rule-name>
      source-zone <source-zone>
      destination-zone <destination-zone>
      action source-nat <translation-object>

For server publication, use the target firewall's server-mapping syntax and
pair it with an exact untrust-to-DMZ permit. NAT transforms addresses; it does
not replace the security policy. Verify policy match, translated session, and
an explicit negative service or direction.

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
