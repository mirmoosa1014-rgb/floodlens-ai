# Explain it simply

Imagine a landscape made from little trays. Rain fills each tray. Water moves to neighboring lower water surfaces, drains away or leaves the bottom edge. The program accounts for every drop. A few rulers (gauges) provide noisy readings. A learned equation estimates unseen crossings a minute later. A virtual inspection can give a fresh point reading, but only after traveling there. A blue surface is a picture of simulator numbers, not proof of real flooding.

## Ten reviewer questions

1. Is this real weather? No, reproducible synthetic storms.
2. Can it predict actual road safety? No.
3. Does water disappear? Drainage/outflow are explicit and the residual is reported.
4. Why not full hydraulics? A storage network is auditable but less realistic.
5. How is leakage prevented? Whole families split before scaling; features use past/current observations only.
6. What is learned? Eight-feature ridge coefficients predicting 60-second crossing depth.
7. Does ML always win? No; the quick benchmark loses to interpolation.
8. Are intervals reliable? Coverage is below nominal under unseen conditions.
9. Do inspections know future truth? Arrival gating prevents observations before travel/dwell completion.
10. What remains? Adaptive information optimization, calibrated hydraulics, real terrain and independent field validation.
