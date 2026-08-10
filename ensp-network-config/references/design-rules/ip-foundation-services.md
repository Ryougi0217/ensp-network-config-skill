# IP Foundation and Services Design Rules

Read these rules for basic IPv4 adjacency, ARP/Proxy ARP, and DHCP service dependencies. Match each trigger and boundary before use.

## DR-IP-001: Separate Layer-3 adjacency, neighbor resolution, and endpoint reachability claims
- Status: candidate
- Tags: ipv4, adjacency, arp, proxy-arp, reachability
- Evidence level: candidate; exclude from normal projects until independently validated.
- Requires: `interface-map-confirmed`, `topology-baseline-confirmed`
- Provides: `layer3-adjacency-ready`, `neighbor-resolution-ready`
- Trigger: A design claims IPv4 reachability across a direct or routed interface, especially when ARP or Proxy ARP affects neighbor resolution.
- Design goal: Keep address/subnet structure, neighbor-resolution state, and endpoint reachability as separate evidence layers.
- Decision logic: Confirm interface roles and address masks; identify whether the destination is directly on-link or requires routing/Proxy ARP; inspect the relevant ARP state; then test the required endpoint path without silently rewriting source masks or example MAC values.
- Recompute parameters: Interface addresses, masks, host gateways, connected prefixes, ARP entries, Proxy ARP interfaces, and positive/negative assertions.
- Applicability boundary: Keep this rule candidate until independent validation covers materially different IPv4 neighbor-resolution behavior; never infer Proxy ARP from static addressing alone.
- Common failure: A successful direct Ping is generalized to routed reachability, a source MAC example is treated as confirmed, or a Proxy ARP method is claimed without interface-state and host evidence.
- Implementation order: Confirm addressing and link roles; determine neighbor-resolution behavior; inspect ARP/Proxy ARP state; then test the required path and isolation assertions.
- Verification method: Correlate interface/subnet facts, ARP state, and endpoint results; retain any mask or MAC mismatch as a boundary.

## DR-DHCP-001: Choose DHCP pool scope from the client attachment and verify the lease separately
- Status: validated
- Tags: dhcp, address-pool, interface-pool, global-pool, lease
- Evidence level: source-derived design constraint; confirm target-platform support and runtime behavior.
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
- Status: validated
- Tags: dhcp, global-pool, interface-pool, phase-transition, lease
- Evidence level: source-derived design constraint; confirm target-platform support and runtime behavior.
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

## DR-DHCP-003: Treat DHCP relay as a three-sided reachability and return-path contract
- Status: candidate
- Tags: dhcp, relay, server-group, return-route, reachability
- Evidence level: candidate; extracted from source examples, but not independently runtime-validated in this project.
- Requires: `layer3-adjacency-ready`, `internal-routing-ready`, `return-path-defined`
- Provides: `address-service-ready`
- Trigger: DHCP clients and the DHCP server are on different subnets and a router or gateway relays the request.
- Design goal: Keep client-to-relay attachment, relay-to-server reachability, and server-to-client return routing explicit before interpreting a lease.
- Decision logic: Derive the client subnet and relay interface from the topology; define the server group and relay selection on the client-facing interface; confirm routes in both directions; then renew a client and correlate relay/server state with the lease.
- Recompute parameters: Client prefix, relay interface, server address/group, server return route, gateway, relay scope, trust boundaries, and lease assertions.
- Applicability boundary: Candidate until the target platform's relay syntax and a clean relay/server/client runtime path are confirmed; a displayed relay configuration or source `ipconfig` output is not proof of relay operation.
- Common failure: The server route back to the client subnet is missing, relay selection is attached to the wrong interface, or a direct/local DHCP mode is confused with relay mode.
- Implementation order: Establish client and server routing; define the server group; enable relay on the client-facing interface; inspect relay/server state; renew the client; then validate options and return reachability.
- Verification method: Correlate relay configuration, server receipt/response, client lease/options, and bidirectional routing evidence.
