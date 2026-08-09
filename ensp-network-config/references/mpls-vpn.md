# MPLS and VPN Design Rules (Reserved)

This catalog remains reserved. Candidate rules are recorded for research traceability and are not available to normal configuration projects.

## DR-MPLS-001: Keep underlay, LSR identity, label session, service, and protection claims separate
- Status: candidate
- Tags: mpls, ldp, lsp, vpn, te, frr, underlay
- Evidence level: candidate; extracted from AR chapters 6 and 10 and not independently runtime-validated in this project.
- Trigger: A design uses LDP/static LSP/MPLS TE or carries a VPN service through an MPLS core.
- Design goal: Prevent an operational LDP/TE state or a source Ping from being generalized into service reachability or protection proof.
- Decision logic: Confirm model/version support and IGP underlay; assign unique LSR IDs; enable label sessions and required interfaces; define service/label or TE path; inspect LDP/LSP/tunnel state; then test customer flow and the named fault.
- Recompute parameters: Supported models/VRP, LSR IDs, loopbacks, IGP prefixes, LDP peers, FEC/prefix triggers, labels, VPN/TE path, FRR protection, and fault target.
- Applicability boundary: Candidate because the source explicitly excludes several AR models and the examples depend on high-end platforms; no MPLS capability should be inferred for eNSP without target support evidence.
- Common failure: LSR ID or underlay is missing, static labels do not match hop-by-hop, TE extensions are absent, a bypass protects the wrong link, or service Ping is claimed from tunnel state alone.
- Implementation order: Capability gate; underlay; LSR ID; label/TE sessions; service path; state inspection; service tests; controlled fault and recovery.
- Verification method: Correlate support boundary, IGP, LDP/LSP/tunnel state, label/service tables, endpoint flow, and fault output.
