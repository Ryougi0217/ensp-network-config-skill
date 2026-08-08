# Verification rules

## Validation layers

### Static structure

- Topology files parse successfully.
- Device IDs and link endpoints are valid.
- Addresses and masks form consistent subnets.
- Configuration files exist and target the intended devices.

### Configuration semantics

- Required VLANs and port modes match the topology.
- Gateways and routed interfaces match host networks.
- Routing processes advertise every required prefix.
- Redundancy or isolation policies contain both positive and negative checks.

### Runtime outcomes

Use concise result assertions:

```yaml
- id: pc1-reaches-pc2
  type: basic_ipv4_connectivity
  expected: {source: PC1, destination: PC2, result: reachable}
```

```yaml
- id: pc1-isolated-from-pc2
  type: ipv4_isolation
  expected: {source: PC1, destination: PC2, result: unreachable}
```

Do not promote incidental Ping details such as packet sequence, latency, or duplicated reverse tests into learned case knowledge. Retain raw screenshots separately as evidence if provided.

## Case approval

Use:

- `imported`: raw source only
- `normalized`: structured topology and configurations exist
- `statically_validated`: deterministic and semantic checks pass
- `runtime_validated`: required results were observed or credibly attested
- `approved`: suitable as trusted evidence

Do not approve a case when `missing_required_evidence` is non-empty.

When the user states that supplied scripts were already verified:

1. independently reason through topology, addressing, and protocol consistency
2. report contradictions instead of overriding them
3. record both user attestation and static reasoning as the validation basis
4. approve only the capabilities actually demonstrated

## Failure cases

Preserve failed configurations as negative evaluation cases only when the expected failure is explicit. Never mix them into trusted generation references.
