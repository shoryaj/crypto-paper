# Experiment results

I ran 270 Z3 queries across 90 parameter settings: 204 SAT, 66 UNSAT, and 0 UNKNOWN. I replayed every core SAT witness with exact rational arithmetic, and every decision agrees with the analytical criterion.

|   Reserve x=y |   SAT |   UNSAT |   UNKNOWN |   Median ms |   Max ms |   Median process RSS MiB |
|---------------|-------|---------|-----------|-------------|----------|--------------------------|
|           100 |    90 |       0 |         0 |      20.606 |   52.619 |                    87.76 |
|          1000 |    90 |       0 |         0 |      20.785 |   43.826 |                    88.61 |
|         10000 |    24 |      66 |         0 |       2.233 |   29.053 |                    89.06 |

I report process RSS snapshots rather than isolated or peak solver memory. Timings cover `solver.check()` only.

## Case study decisions

| Case          | Decision   |
|---------------|------------|
| spot          | sat        |
| bounded       | unsat      |
| loose_bound   | sat        |
| dynamic       | unsat      |
| harvest_proxy | sat        |
| harvest_fixed | unsat      |
| euler_health  | sat        |
| euler_fixed   | unsat      |
| uint256       | sat        |

## Exact analytic reserve bound

{
  "y_min": "1000/(-1 + sqrt(30270)/150)",
  "k_min_sufficient": "1000000/(-1 + sqrt(30270)/150)**2",
  "k_approx": 39118687.605252765
}

I use this as a sufficient fixed-cap depth bound, not a universal TVL-only minimum.
