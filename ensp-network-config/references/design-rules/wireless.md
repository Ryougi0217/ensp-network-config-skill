# Wireless Design Rules

Read these rules for Huawei AC/AP WLAN designs. Confirm the target AC/AP model, VRP/eNSP support, forwarding mode, and runtime evidence before claiming deployment success.

## DR-WLAN-001: Separate management VLAN from client service VLANs
- Tags: wlan, ac, ap, management-vlan, service-vlan
- Requires: `platform-support-confirmed`, `layer2-transport-ready`
- Provides: `wireless-management-ready`
- Trigger: An AC/AP WLAN must carry AP management/CAPWAP traffic and wireless user traffic.
- Design goal: Keep controller/AP management reachability independent from user policy and service addressing.
- Decision logic: Allocate a management VLAN and one or more service VLANs; carry only the required VLANs across each wired segment; bind AP management to the management path and VAPs to service VLANs.
- Recompute parameters: Management/service VLANs, trunk allow lists, SVI/DHCP scope, CAPWAP source, VAP service VLAN, gateway, and return route.
- Applicability boundary: Tunnel and direct-forward modes have different wired VLAN requirements; confirm the target AC/AP and switch behavior.
- Common failure: APs register but users receive no address because the service VLAN is absent from a trunk or gateway.
- Implementation order: Plan VLANs; build management path; register AP; build service templates; extend service VLAN; verify management and user paths separately.
- Verification method: Check AP management state, VLAN transport, STA address/gateway, and service reachability as separate assertions.

## DR-WLAN-002: Separate AP registration from user association
- Tags: wlan, capwap, ap-registration, sta, association
- Requires: `wireless-management-ready`
- Provides: `wireless-client-plane-ready`
- Trigger: A WLAN deployment reports that an AP is online or that a client can use an SSID.
- Design goal: Prevent AP control-plane success from being mistaken for client-plane success.
- Decision logic: Verify management VLAN/CAPWAP and AP authentication first; then verify SSID/VAP/radio binding; finally verify STA association, DHCP, gateway, and application access.
- Recompute parameters: AP identity/authentication, AP group, SSID, radio, VAP, client VLAN, DHCP pool, and test endpoint.
- Applicability boundary: `display ap all` normal state proves only the AP control-plane result; it does not prove RF association, address assignment, or egress.
- Common failure: AP is normal but the SSID is not bound to a radio, the security template is missing, or the client VLAN is not reachable.
- Implementation order: AP registration; template/reference chain; radio binding; client association; DHCP/gateway; egress test.
- Verification method: Record AP state, VAP/SSID state, STA association, IP/gateway, and business reachability separately.

## DR-WLAN-003: Keep the WLAN template reference chain complete
- Tags: wlan, ssid, security-profile, vap, radio, ap-group
- Requires: `platform-support-confirmed`
- Provides: `wireless-template-ready`
- Trigger: An SSID is built from reusable AC WLAN templates.
- Design goal: Ensure an advertised SSID has a complete security, service, and radio binding path.
- Decision logic: Create security profile; create SSID profile; create VAP with forwarding/service VLAN; bind both profiles; bind VAP to the AP group and intended radio; inspect the resulting reference chain.
- Recompute parameters: Profile names, security method/key, SSID, forwarding mode, service VLAN, AP group, and radio set.
- Applicability boundary: Template commands and supported security algorithms vary by AC version; a syntactically accepted profile may still be unbound.
- Common failure: The SSID is visible but security/VAP/service VLAN is not referenced, or only one radio receives the VAP.
- Implementation order: Security → SSID → VAP/service → AP-group/radio binding → client association → service verification.
- Verification method: Inspect each object and its reference, then test association and address assignment.

## DR-WLAN-004: Prove wired continuity for the selected forwarding mode
- Tags: wlan, tunnel-forward, direct-forward, vlan, gateway, dhcp
- Requires: `wireless-management-ready`, `wireless-template-ready`, `layer2-transport-ready`, `address-service-ready`, `gateway-ready`
- Provides: `wireless-service-ready`
- Trigger: Wireless users must reach a wired gateway or external network.
- Design goal: Make the selected forwarding mode and wired VLAN path agree end to end.
- Decision logic: If tunnel forwarding is selected, validate the CAPWAP/AC service path; if direct forwarding is selected, validate the AP/SW trunk and service VLAN at every hop; then validate DHCP, gateway, route, and return path.
- Recompute parameters: Forwarding mode, service VLAN, AP/SW trunk membership, VAP binding, DHCP scope, gateway, default route, and return route.
- Applicability boundary: AP online and SSID association are insufficient; the user VLAN and exit path need their own evidence.
- Common failure: Direct-forward traffic leaves the AP but the service VLAN is not allowed on a core/access trunk, or the return route is absent.
- Implementation order: Select mode; extend VLAN/service; bind VAP; configure address service; verify client gateway; verify egress and return path.
- Verification method: Inspect trunks/VLANIF/routes and then test STA address, gateway, and external destination separately.
