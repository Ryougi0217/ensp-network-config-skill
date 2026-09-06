# IP Foundation and Services Design Rules

Read these rules for basic IPv4 adjacency, ARP/Proxy ARP, and DHCP service dependencies. Match each trigger and boundary before use.

## DR-DHCP-001: Choose DHCP pool scope from the client attachment and verify the lease separately
- Tags: dhcp, address-pool, interface-pool, global-pool, lease
- Requires: `gateway-ready`
- Provides: `address-service-ready`
- Trigger: A router must allocate addresses to clients on one or more directly attached LANs.
- Design goal: Make the selection between interface-scoped and global pools explicit while keeping gateway, exclusion, DNS, and lease claims tied to runtime allocation evidence.
- Decision logic: Derive the client network and gateway need from the current interface and required client behavior; choose interface address-pool selection for local/simple scope or an explicitly named global pool for reusable policy; bind each pool to the correct client-facing interface; add only the selected gateway, DNS, exclusion, and lease options; then verify the lease and those selected options from the client or server state.
- Recompute parameters: Client VLAN/LAN, server interface, pool mode/name, network, gateway, excluded range, lease duration, DNS, and endpoint pre-test state.
- Applicability boundary: Do not claim successful allocation or options without current runtime lease evidence; static PC settings and an excluded address are source observations, not proof of DHCP behavior.
- Common failure: A global pool is bound to the wrong interface, a saved static address is mistaken for a lease, or configured options are claimed without a lease/output observation.
- Implementation order: Confirm client attachment and gateway; choose pool scope; configure and bind the pool; clear/identify endpoint pre-test state; then collect lease and option evidence.
- Verification method: Inspect pool/binding structure and correlate it with client lease, gateway, DNS, and lease-time output.

## DR-DHCP-002: Treat global-pool and interface-pool DHCP as separate phases
- Tags: dhcp, global-pool, interface-pool, phase-transition, lease
- Requires: `gateway-ready`
- Provides: `address-service-transition-ready`
- Trigger: Source material demonstrates more than one DHCP allocation mode on the same VLANIF topology.
- Design goal: Prevent a lease or option observation from one mode being attributed to another mode or to a simultaneous final state.
- Decision logic: Label the active mode; record pool selection and options; clear or explicitly transition the previous mode; renew clients; then inspect lease, gateway, DNS, exclusion, and pool usage for the active phase.
- Recompute parameters: Phase order, pool names, client networks, SVI binding, excluded ranges, DNS, lease policy, and pre-test endpoint mode.
- Applicability boundary: Do not claim lease provenance until cleanup/renewal and current lease evidence are available; source ipconfig output alone does not prove which phase issued the lease.
- Common failure: Two phases are merged into one topology state, an excluded static address is treated as a DHCP lease, or the global pool remains bound during the interface-pool test.
- Implementation order: Establish VLAN/SVI; run and verify one mode; document transition/cleanup; run and verify the next mode; retain separate evidence.
- Verification method: Correlate active binding, server pool state, client lease/options, and phase timestamps.
