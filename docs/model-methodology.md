# Model methodology

All model inputs are HYPOTHETICAL training assumptions. Let E be eligible people; n, a, s, f be conditional rates in [0,1]; C be screening capacity in people; B be spend in INR. The current model starts with an eligible cohort, not district population.

- Need proxy N = E × n
- Aware A = N × a
- Screened S = min(A × s, C)
- Followed up F = S × f
- Unscreened need proxy U = N - S
- Spend = B, an input, not an estimated intervention cost

Conservation: 0 <= F <= S <= A <= N <= E. Raising uptake or screening capacity cannot lower S with other inputs fixed. Spend does not change reach in this funnel. The separate optimizer assumes explicit fictional people/INR yields; it does not infer them from the funnel.

Each input has low/mode/high, a field-specific unit and rationale. Rates cannot exceed 1; values must be finite and nonnegative. A percentage is not a fraction or a people count. At training modes E=10000, n=.2, a=.4, s=.5, f=.6, C=500, B=150000: N=2000, A=800, S=400, F=240. These are arithmetic training outputs, not observed patients.

## Uncertainty

Independent triangular input distributions are sampled with a local seeded Python RNG. p10/p50/p90 are conditional percentile bands, not confidence/credible intervals fitted to data. This is parameter propagation and scenario uncertainty. Sampling uncertainty of an empirical estimator, structural model uncertainty and posterior uncertainty are not estimated. Distribution families are not yet configurable.

OAT changes one mode to each bound while holding other modes fixed, ranks outcome swing and normalizes absolute swings to sum to 1 when nonzero. Morris screens global assumed bounds through SALib. Neither proves an assumption is wrong or measures a causal effect. Research scores remain a heuristic, not VOI.

Paired robustness shares an input quantile across scenarios and uses triangular inverse CDFs. This is an assumed dependence structure. Ties split evenly. Preference share maximizes screened count, not net benefit or cost-effectiveness. A one-input reversal scan varies shared awareness quantiles with other inputs at modes. It is not an empirical threshold.

Optimization exhaustively searches bounded integer INR steps (at most 100000 combinations), enforces total budget/dependencies and saturates yields at intervention/shared district capacity. Unused spend is allowed. Ties favor lower spend then stable lexicographic allocations. It is optimal only under the specified discrete grid and hypothetical yields. Fractional allocations, MILP and clinical effectiveness are not implemented.

Treatment linkage and population-to-eligibility stages are not in this model. A richer care pathway requires explicit semantics and tests, not relabeling existing outputs. See [limitations](limitations.md).
