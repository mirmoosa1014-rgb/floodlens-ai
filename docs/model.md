# Model card

Eight standardized features: inverse-distance gauge depth; change since three steps ago; current rainfall /100 mm/h; trailing seven-step rainfall /100; target elevation; weighted gauge elevation; nearest-gauge distance / grid size; depth×rain interaction. No hidden labels, future rain or future depths enter features. Target is crossing depth three steps (60 s) later. Ridge L2=0.05; intercept unpenalized. NumPy solves the small normal equation. JSON avoids executable pickle models.

Terrain families split before scaling/fitting; means/scales use training only. Validation residuals set one 90th-percentile absolute interval. Test identities are in model JSON. Missing model uses current gauge interpolation. Malformed schemas fail rather than loading arbitrary serialized content.

Gauge-only interval coverage is 70.03% on mixed heldout/OOD evaluation. Inspection corrections do not inherit this calibration. Training uses fixed relief-selected gauges; random/grid placement is an additional distribution shift. Point corrections are causal, short-lived and nonnegative. Neither training nor testing provides field-safety certification or a calibrated probability of flooding.
