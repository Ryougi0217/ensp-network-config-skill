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

## Existing configuration

Treat removal and replacement as higher risk than addition. Before changing an existing lab:

- inspect `display current-configuration`
- identify existing interface, VLAN, and routing ownership
- produce an incremental change set
- explain destructive or compatibility risks before delivery

Do not generate command-level rollback scripts. If partial execution or rework makes the actual state uncertain, identify the smallest affected device set, ask whether the user wants to reset it, and let the user perform all clearing operations. Rebuild from persisted cumulative stage scripts after reset.

Do not include `save` in stage scripts. Let the user decide whether to persist a stage after its gate passes.

## Abbreviations

Accept common lab abbreviations such as `int`, `ip ad`, `v b`, `a`, and `n` as input. Expand them in final configurations to improve reviewability.
