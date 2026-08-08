# eNSP configuration project workflow

## Contents

1. Project modes
2. Project directory
3. Planning baseline
4. Stage skeleton and status
5. Stage TXT contract
6. Static delivery gate
7. Runtime gate
8. Failure, reset, and change handling
9. Completion and case learning

## 1. Project modes

### Simple mode

Use one configuration stage when all are true:

- no more than three network devices
- one main technology
- no meaningful redundancy or Layer 2 loop
- no dynamic-routing, security, authentication, or exit dependency
- failure has a small local impact

Use the same project structure as staged mode, but create only `01-完整配置-v1.txt` and one acceptance gate.

### Staged mode

Use staged mode when any are true:

- access, aggregation, and core roles exist
- redundant links or Layer 2 loops exist
- MSTP, VRRP, Eth-Trunk, BFD, or similar reliability features exist
- multi-area OSPF, route import, or several routing domains exist
- ACL, NAT, PPPoE, DHCP, or several services depend on the underlay
- the user requests phased implementation

## 2. Project directory

Treat the project directory as the only persistent source of truth.

```text
projects/PROJECT-SLUG/
├── project.json
├── topology.json
├── requirements.yaml
├── stage-plan.yaml
├── planning/
│   ├── 网络设备与链路规划.txt
│   ├── VLAN与网关规划.txt
│   ├── 终端与服务器地址规划.txt
│   └── 阶段实施计划.txt
├── scripts/
├── validation/
└── evidence/
```

Store complete details in files. In chat, show the baseline version, counts, stage summary, conflicts, and uncertainties only.

## 3. Planning baseline

Build and confirm one baseline before configuration. Include:

- devices, types, profiles, and layer roles
- links and both endpoint ports
- planned expansion modules when relevant
- VLANs, networks, gateways, and endpoint addressing
- Layer 2 and Layer 3 boundaries
- routing areas and exit position
- reachability, isolation, redundancy, service, and security requirements
- stage dependencies and safe parallel branches

Use these interface rules:

- clear screenshot or project value -> `observed`
- proposed non-conflicting value on known hardware -> `planned`
- obscured label, resource conflict, or unknown expansion module -> `needs_user_confirmation`
- user-approved observed or planned value -> `confirmed`

Never generate commands for an unresolved used interface.

Confirm the baseline once. Increment its version after an approved change. Do not repeat full tables in chat.

## 4. Stage skeleton and status

Use this skeleton and dynamically skip or split stages:

```text
planning baseline
→ access
→ aggregation
→ core and backbone routing
→ independent routing areas or service branches
→ services and exit
→ security policy
→ end-to-end acceptance
```

The normal gate unit is a network layer or independent fault domain. A stage may contain many related commands; do not create a conversational gate for each command family.

Default to serial execution. Mark independent branches as parallelizable, but require the user to choose parallel execution. Join branches only after each branch passes its own gate.

Use these stage states:

| State | Meaning |
|---|---|
| `planned` | scope, dependencies, and assertions defined |
| `script_generated` | versioned stage TXT exists |
| `statically_validated` | deterministic and semantic checks passed |
| `delivered` | user received the stage script |
| `passed` | gate passed normally |
| `failed` | a required assertion failed |
| `forced_pass` | user chose to continue after failure |
| `needs_rework` | baseline change invalidated the stage |
| `skipped` | topology does not require this stage |

Only `passed` permits normal automatic advancement. `forced_pass` permits advancement only after the user explicitly chooses it and leaves a project risk.

## 5. Stage TXT contract

Create one versioned TXT per stage. Use UTF-8 and stable machine-readable section markers:

```text
===== STAGE: 01-access | 接入层 =====
===== CONFIG DEVICE: LSW5 =====
system-view
...
return

===== CONFIG DEVICE: LSW3 =====
system-view
...
return

===== VERIFY DEVICE: LSW5 =====
display vlan
display interface brief
```

Rules:

- put configuration blocks before verification blocks
- order configuration blocks by recommended execution order
- use one configuration block per device in a stage
- use full command forms unless the user explicitly requests abbreviations
- generate incremental commands for this stage only
- do not include `save`
- do not include endpoint address planning in a stage file
- keep explanations outside device command blocks
- create a new `-vN.txt` version after change; never overwrite an executed or delivered version

The user copies one device block at a time. Section markers are file navigation aids, not VRP commands.

## 6. Static delivery gate

Before delivery:

1. parse every device block
2. validate markers and script structure
3. ensure no `save` command exists
4. compare devices and interfaces with the confirmed topology
5. check addressing, VLAN, trunk, gateway, routing, and policy consistency
6. ensure the stage changes only its allowed scope
7. check that prior passed-stage intent remains intact
8. perform protocol semantic review

Automatically repair only mechanical issues such as representation, block ordering, or unambiguous command expansion. Ask before changing any confirmed network-design value.

## 7. Runtime gate

Define assertions before configuration. Use the smallest evidence set that proves the stage goal.

Allow two gate paths:

### User attestation

Accept only explicit statements such as “本阶段验证通过”. Record:

```json
{"gate":"passed","evidence_type":"user_attestation"}
```

Treat uncertain wording such as “好像可以” as `uncertain`.

### Runtime evidence

Give minimal verification commands. Accept pasted output or screenshots. For screenshots, extract structured facts first, then pass assertion states to deterministic evaluation.

Use:

```json
{
  "assertions": [
    {"id": "gateway-reachable", "state": "passed"},
    {"id": "guest-isolated", "state": "passed"}
  ]
}
```

Return `passed` only when every required assertion passed, `failed` when any required assertion failed, and `uncertain` when evidence is missing or ambiguous.

Ping success records `reachable`; ignore timing, TTL, packet sequence, and redundant reverse Ping unless direction is part of policy.

## 8. Failure, reset, and change handling

On failure:

1. report failed and missing assertions
2. explain downstream impact
3. let the user choose repair or forced continuation
4. record explicit forced continuation as `forced_pass`

Do not generate rollback scripts. For partial execution or rework, identify the smallest affected device set and ask whether the user wants to reset it. The user performs all reset and clearing operations. Rebuild the affected device from persisted cumulative stages.

When the baseline changes:

1. identify directly affected objects
2. identify dependent stages
3. show the rework scope
4. ask whether to rework

If the user rejects rework, either keep the old baseline active or record forced adoption with unresolved risk. Never preserve a normal pass against an incompatible new baseline.

## 9. Completion and case learning

After all stage gates, generate `98-全网验收.txt` from the original confirmed requirements. Include all required positive and negative outcomes and every forced-risk retest.

Use `assemble_stage_scripts.py` on demand to create `99-全网最终完整配置.txt`. The assembler groups configuration blocks by device in stage-file order and excludes verification blocks. It must not semantically deduplicate commands.

Use project result states:

- `script_ready`: scripts exist and passed static validation
- `implemented`: user says scripts were applied
- `verified`: every required stage and final acceptance passed normally
- `completed_with_risks`: execution ended with forced passes or unresolved risks

Ask once after completion whether to save the work as a case. Do not import or update the capability matrix without explicit user authorization.
