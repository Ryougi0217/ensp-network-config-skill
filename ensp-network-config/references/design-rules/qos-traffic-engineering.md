# QoS and Traffic Engineering Design Rules

Read these rules for MQC classification, actions, attachment, and measurable effect. Match each trigger and boundary before use.

## DR-QOS-001: Keep MQC classification, behavior, policy, attachment, and counters aligned
- Status: validated
- Tags: qos, mqc, traffic-classifier, traffic-behavior, traffic-policy, policing, statistics
- Evidence cases: none; direct source-reference adoption
- Validation basis: Direct source-rule adoption authorized by the user from the Huawei manual QoS chapter; no independent throughput test, hardware-resource check, current-platform confirmation, or blind test was performed.
- Trigger: Traffic must be permitted, denied, redirected, remarked, policed, or counted according to a defined class.
- Design goal: Turn the service requirement into one traceable chain from packet match to action, attachment point/direction, and measurable result.
- Decision logic: Derive the traffic class from the requirement; choose one compatible behavior; bind classifier and behavior in a policy; attach the policy at the device, interface, or VLAN scope and direction where the target traffic is actually seen; inspect policy/counters; then measure the requested effect against a baseline.
- Recompute parameters: Match fields and ACLs, classifier operator/order, action, rates and burst values, policy name, attachment device/scope/direction, resource budget, baseline, and pass/fail thresholds.
- Applicability boundary: Confirm current device support, attachment restrictions, hardware resources, units, and action compatibility; a displayed policy or counter increment does not by itself prove throughput, latency, loss, or an SLA.
- Common failure: The classifier matches unintended traffic, behavior and ACL semantics conflict, the policy is attached in the wrong direction, rate units are copied blindly, or no baseline/counter proves that packets hit the policy.
- Implementation order: Define measurable intent; establish baseline; build and inspect the classifier; define the behavior; bind the policy; attach at the resolved scope/direction; inspect counters; measure the requested effect and rollback if it harms unrelated traffic.
- Verification method: Correlate classifier matches, policy attachment, counter changes, and before/after traffic measurements; include a negative flow that must remain unaffected.
