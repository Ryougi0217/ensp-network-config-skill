# QoS and Traffic Engineering Design Rules

Read these rules for MQC classification, actions, attachment, and measurable effect. Match each trigger and boundary before use.

## DR-QOS-001: Keep MQC classification, behavior, policy, attachment, and counters aligned
- Status: validated
- Tags: qos, mqc, traffic-classifier, traffic-behavior, traffic-policy, policing, statistics
- Evidence level: source-derived design constraint; confirm target-platform support and runtime behavior.
- Trigger: Traffic must be permitted, denied, redirected, remarked, policed, or counted according to a defined class.
- Design goal: Turn the service requirement into one traceable chain from packet match to action, attachment point/direction, and measurable result.
- Decision logic: Derive the traffic class from the requirement; choose one compatible behavior; bind classifier and behavior in a policy; attach the policy at the device, interface, or VLAN scope and direction where the target traffic is actually seen; inspect policy/counters; then measure the requested effect against a baseline.
- Recompute parameters: Match fields and ACLs, classifier operator/order, action, rates and burst values, policy name, attachment device/scope/direction, resource budget, baseline, and pass/fail thresholds.
- Applicability boundary: Confirm current device support, attachment restrictions, hardware resources, units, and action compatibility; a displayed policy or counter increment does not by itself prove throughput, latency, loss, or an SLA.
- Common failure: The classifier matches unintended traffic, behavior and ACL semantics conflict, the policy is attached in the wrong direction, rate units are copied blindly, or no baseline/counter proves that packets hit the policy.
- Implementation order: Define measurable intent; establish baseline; build and inspect the classifier; define the behavior; bind the policy; attach at the resolved scope/direction; inspect counters; measure the requested effect and rollback if it harms unrelated traffic.
- Verification method: Correlate classifier matches, policy attachment, counter changes, and before/after traffic measurements; include a negative flow that must remain unaffected.

## DR-QOS-002: Place identity-sensitive policing where the original identity is visible
- Status: candidate
- Tags: qos, policing, pre-nat, post-nat, direction, source-ip, destination-ip, counters
- Evidence level: candidate; source-derived from S V600 and AR QoS examples and not independently runtime-validated in this project.
- Trigger: Per-IP, per-subnet, or service policing must remain tied to an address identity while traffic crosses NAT or dual exits.
- Design goal: Align classifier visibility, traffic direction, NAT phase, and counter evidence so the configured identity is the identity actually matched.
- Decision logic: Determine whether the requirement is upload/source-based or download/destination-based; locate the interface and direction before NAT for the original identity; define the classifier and rate/burst values; attach the policy there; then compare pre/post-NAT counters and an unaffected flow.
- Recompute parameters: Original source/destination prefix, NAT boundary, ingress/egress direction, ACL/classifier, CIR/PIR/burst units, attachment interface, exit path, baseline, and counter thresholds.
- Applicability boundary: Candidate until platform processing order, units, hardware resource limits, and runtime counter/traffic evidence are confirmed; a queue profile or displayed counter is not an SLA.
- Common failure: A source identity is matched after NAT has hidden it, download policy is placed on the wrong direction, CIR values are copied without interface-budget checks, or a counter increment is treated as proof of the requested throughput.
- Implementation order: Establish NAT and route phases; identify the visible identity; build classifier/behavior/policy; attach at the pre-NAT direction; inspect counters and interface budget; measure positive and unaffected flows.
- Verification method: Correlate NAT phase, direction, classifier matches, policy counters, queue statistics, and before/after traffic measurements.
