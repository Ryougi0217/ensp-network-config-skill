# Operations and Automation Design Rules

Read these rules for device-management reachability, monitoring access, and event delivery. Match each trigger and boundary before use.

## DR-SNMP-001: Design SNMP as a matched version, access scope, and notification tuple
- Status: validated
- Tags: snmp, nms, mib-view, acl, trap, inform, management
- Evidence level: source-derived design constraint; confirm target-platform support and runtime behavior.
- Requires: `management-path-ready`, `management-access-ready`
- Provides: `monitoring-ready`
- Trigger: A network-management system must poll a device or receive device notifications through SNMP.
- Design goal: Keep management reachability, protocol version, credentials/security level, managed MIB scope, permitted NMS sources, and notification target mutually consistent.
- Decision logic: Confirm the management path; select the SNMP version from the current security policy and platform support; restrict NMS sources and MIB scope; configure community-based access only when explicitly accepted or configure a version-3 user/group with the required authentication/privacy level; align Trap/Inform target parameters with the same version and security identity; then verify polling and one controlled notification.
- Recompute parameters: Management addresses and routes, NMS sources, version, read/write need, MIB scope, ACL, user/group or community, authentication/privacy policy, notification type, target, and test event.
- Applicability boundary: Confirm the device's current command set and organizational security policy; do not disable credential-complexity controls, expose write access, or choose obsolete authentication/privacy merely because the dated source demonstrates it.
- Common failure: NMS and device versions or credentials differ, polling works but notifications use another identity, management routing is absent, or an ACL/MIB view grants broader access than required.
- Implementation order: Establish management reachability; choose version/security level; restrict source and MIB scope; configure polling access; configure notifications; verify authorized polling, denied unauthorized access, and event delivery.
- Verification method: Correlate management routing, SNMP access configuration, authorized and denied polling outcomes, and receipt of a controlled Trap/Inform at the intended NMS.
