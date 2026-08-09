# Topology schema

Use one JSON document as the canonical intermediate representation. Keep screenshots and user-facing tables as views of this document.

## Core shape

```json
{
  "schema_version": "0.1.0",
  "case_id": "optional-case-id",
  "source": {"type": "screenshot", "path": "raw/topology.png"},
  "devices": [],
  "links": [],
  "uncertainties": []
}
```

## Device

Record only observed or confirmed interfaces. Model optional modules as properties of a device instance, not as permanent ports of the device model.

```json
{
  "id": "AR1",
  "type": "router",
  "vendor": "Huawei",
  "model": null,
  "environment": "eNSP",
  "roles": ["abr"],
  "installed_modules": [
    {"slot": "1", "module_type": "2GE", "status": "confirmed"}
  ],
  "interfaces": [
    {
      "name": "GigabitEthernet0/0/0",
      "display_label": "GE 0/0/0",
      "source": ["image", "provided_config"],
      "confidence": 0.99,
      "status": "confirmed",
      "ipv4": [{"address": "192.168.0.1", "prefix_length": 24}]
    }
  ]
}
```

Allowed device types include `router`, `switch`, `layer3_switch`, `firewall`, `wireless_controller`, `access_point`, `wireless_client`, `host`, `server`, and `cloud`. Preserve an unknown type as `unknown` and ask for confirmation. Use `wireless_controller` for an AC, `access_point` for an AP, and `wireless_client` for a STA when the source identifies those roles.

## Link

Use full interface names internally. A link requires exactly two endpoints.

```json
{
  "id": "L1",
  "a": {"device": "AR1", "interface": "GigabitEthernet0/0/0"},
  "b": {"device": "AR2", "interface": "GigabitEthernet0/0/0"},
  "network": "192.168.0.0/24",
  "confidence": 0.97,
  "status": "confirmed"
}
```

Compact `DEVICE:INTERFACE` endpoints are acceptable in case data, but normalize them before generation.

## Status and source

Use these statuses:

- `observed`: extracted from an artifact but not confirmed
- `needs_user_confirmation`: ambiguous or conflicting
- `confirmed`: safe to use for generation

Record source provenance whenever a field comes from configuration rather than an image.

## Uncertainty

```json
{
  "id": "U1",
  "field": "links[1].b.interface",
  "reason": "The endpoint label is obscured in the screenshot."
}
```

Do not put a guessed value into the canonical field when confidence is below 0.70.

## Consistency rules

- Require unique device IDs.
- Require every link endpoint to reference an existing device.
- Prevent an interface from terminating multiple physical links unless the representation explicitly models a shared medium.
- Validate IP addresses, masks, networks, gateways, and duplicate addresses.
- Confirm that a configured interface exists on the corresponding observed device instance.
- Keep address plans, VLAN membership, and routing areas consistent with the requirement.
