# IP Foundation and Services Design Rules

Read these rules for basic IPv4 adjacency, ARP/Proxy ARP, and DHCP service dependencies. Match each trigger and boundary before use.

## DR-IP-001: Separate Layer-3 adjacency, neighbor resolution, and endpoint reachability claims
- Status: candidate
- Tags: ipv4, adjacency, arp, proxy-arp, reachability
- Evidence cases: `001-ar-direct`, `019-arp-proxy-arp`
- Validation basis: One approved basic-connectivity case plus one pending method case; no blind test in this batch.
- Trigger: A design claims IPv4 reachability across a direct or routed interface, especially when ARP or Proxy ARP affects neighbor resolution.
- Design goal: Keep address/subnet structure, neighbor-resolution state, and endpoint reachability as separate evidence layers.
- Decision logic: Confirm interface roles and address masks; identify whether the destination is directly on-link or requires routing/Proxy ARP; inspect the relevant ARP state; then test the required endpoint path without silently rewriting source masks or example MAC values.
- Recompute parameters: Interface addresses, masks, host gateways, connected prefixes, ARP entries, Proxy ARP interfaces, and positive/negative assertions.
- Applicability boundary: Candidate only until a second approved case covers a materially different IPv4/neighbor-resolution scenario; Proxy ARP must not be inferred from static addressing alone.
- Common failure: A successful direct Ping is generalized to routed reachability, a source MAC example is treated as confirmed, or a Proxy ARP method is claimed without interface-state and host evidence.
- Implementation order: Confirm addressing and link roles; determine neighbor-resolution behavior; inspect ARP/Proxy ARP state; then test the required path and isolation assertions.
- Verification method: Correlate interface/subnet facts, ARP state, and endpoint results; retain any mask or MAC mismatch as a boundary.

## DR-DHCP-001: Choose DHCP pool scope from the client attachment and verify the lease separately
- Status: validated
- Tags: dhcp, address-pool, interface-pool, global-pool, lease
- Evidence cases: `039-dhcp-interface-pool`, `040-dhcp-global-pool`, `056-dhcp-global-pools-exam`
- Validation basis: Direct source-rule adoption authorized by the user; the Huawei manual explains interface/global pool selection and case 056 contains source-visual lease/pool observations, but no independent eNSP rerun or blind test.
- Trigger: A router must allocate addresses to clients on one or more directly attached LANs.
- Design goal: Make the selection between interface-scoped and global pools explicit while keeping gateway, exclusion, DNS, and lease claims tied to runtime allocation evidence.
- Decision logic: Derive the client network and gateway from the current interface; choose interface address-pool selection for local/simple scope or an explicitly named global pool for reusable policy; bind each pool to the correct client-facing interface; then verify lease, gateway, and options from the client or server state.
- Recompute parameters: Client VLAN/LAN, server interface, pool mode/name, network, gateway, excluded range, lease duration, DNS, and endpoint pre-test state.
- Applicability boundary: Do not claim successful allocation or options without current runtime lease evidence; static PC settings and an excluded address are source observations, not proof of DHCP behavior.
- Common failure: A global pool is bound to the wrong interface, a saved static address is mistaken for a lease, or configured options are claimed without a lease/output observation.
- Implementation order: Confirm client attachment and gateway; choose pool scope; configure and bind the pool; clear/identify endpoint pre-test state; then collect lease and option evidence.
- Verification method: Inspect pool/binding structure and correlate it with client lease, gateway, DNS, and lease-time output.

## DR-DHCP-002: Treat global-pool and interface-pool DHCP as separate phases
- Status: validated
- Tags: dhcp, global-pool, interface-pool, phase-transition, lease
- Evidence cases: 056-dhcp-global-pools-exam
- Validation basis: Direct source-rule adoption authorized by the user; case 056 contains source-visual phased DHCP observations, but no independent phase-reset rerun or blind test.
- Trigger: Source material demonstrates more than one DHCP allocation mode on the same VLANIF topology.
- Design goal: Prevent a lease or option observation from one mode being attributed to another mode or to a simultaneous final state.
- Decision logic: Label the active mode; record pool selection and options; clear or explicitly transition the previous mode; renew clients; then inspect lease, gateway, DNS, exclusion, and pool usage for the active phase.
- Recompute parameters: Phase order, pool names, client networks, SVI binding, excluded ranges, DNS, lease policy, and pre-test endpoint mode.
- Applicability boundary: Do not claim lease provenance until cleanup/renewal and current lease evidence are available; source ipconfig output alone does not prove which phase issued the lease.
- Common failure: Two phases are merged into one topology state, an excluded static address is treated as a DHCP lease, or the global pool remains bound during the interface-pool test.
- Implementation order: Establish VLAN/SVI; run and verify one mode; document transition/cleanup; run and verify the next mode; retain separate evidence.
- Verification method: Correlate active binding, server pool state, client lease/options, and phase timestamps.
