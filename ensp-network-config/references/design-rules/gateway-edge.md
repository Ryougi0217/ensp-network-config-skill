# Gateway and Edge Design Rules

Read these rules for first-hop gateway, inter-VLAN, and edge-service decisions. Match each trigger and boundary before use.

## DR-MSTP-VRRP-004: Derive a VRRP tuple independently for each VLAN
- Status: validated
- Tags: vrrp, vlan, gateway, addressing
- Evidence cases: `013-vrrp-basic`, `014-vrrp-mstp-ethtrunk-rip`
- Trigger: A VLAN has two or more redundant Layer-3 gateway interfaces using VRRP.
- Design goal: Make the virtual gateway unambiguous, non-conflicting, and intentionally load-shared or failover-capable.
- Decision logic: Start from the current subnet and gateway participants; allocate non-conflicting real SVI and virtual addresses; use one matching VRID per VLAN across its peers; choose priorities to encode the requested master and backup roles.
- Recompute parameters: VLAN/subnet, real SVI addresses, virtual address, VRID, priority, host default gateway, and tracking requirements.
- Do not copy: Any evidence case's addresses, VRIDs, priorities, or endpoint values.
- Applicability boundary: Ignore when there is only one gateway or VRRP is not part of the requirement; do not treat priority alone as upstream-path health.
- Common failure: A virtual address collides with a real address, peers use different VRIDs, or both VLANs accidentally select the same master against the load-sharing requirement.
- Implementation order: Build VLAN/SVI reachability; create the VRRP groups; add tracking or routing convergence when required; then test gateway and upstream reachability.
- Verification method: Inspect VRRP state and address ownership, ping the virtual gateway from each VLAN, and repeat after the specified gateway/uplink fault.
