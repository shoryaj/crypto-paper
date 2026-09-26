# Research status and outstanding evidence

The local artifact executes all implemented models and includes a complete
seven-section manuscript draft. It does not complete the broader claim of
publication-ready, contract-level flash-loan immunity.

| Requested phase | Delivered | Remaining to support the original stronger claim |
|---|---|---|
| 1. Formalization | Full accounting model, proofs, derivatives, exact candidate optimum and sufficient liquidity bound | General adversarial schedules and contract refinement |
| 2. Engine | Runnable QF_NRA core, bounded swap DAG conservation, one concentrated range, concrete uint256 mode, unknown handling | Arbitrary interleaved protocol DAGs; universal uint256 lending/vault verification |
| 3. Cases | bZx-inspired spot geometry; two-pool Harvest proxy; Euler health transition; mitigated controls | Actual historical states, original contract semantics, exact liquidation profitability |
| 4. Experiments | 270 measured checks, rational replay, analytic agreement, CSV/JSON, graphs, RSS snapshots | Peak/isolated memory measurements, DAG scaling and matched baseline comparison |
| 5. Manuscript | IEEE-style complete source with measured table, figures, primary-source references and limitations | TeX compilation, visual review, complete bibliography metadata, novelty assessment and submission preparation |
| 6. Artifact | Reproducible local repository layout, pinned dependencies, tests, SMT2 queries and packaged archive | Public GitHub release and archival DOI |

The initial premise needed correction: A-input depresses the price of A;
collateral has an opportunity cost; reverse swaps recover principal; cash caps
change optimization; exponentials are outside polynomial QF_NRA; Euler is not
a spot-oracle-only attack. These corrections are incorporated throughout.

Existing economic verification and attack-synthesis work includes DeFiPoser,
Clockwork Finance and Foray. A novelty claim must be assessed against these,
not merely against Slither and Mythril. No performance superiority is claimed.

An UNSAT mitigation result assumes the oracle bound or policy. A SAT result
for a permissive bounded oracle is a witness in that abstraction, not proof
that a concrete TWAP can reach that price. Integer-mode SAT means a concrete
arithmetic trace is valid, not that it is a profitable exploit. Euler SAT means
health can be broken, not that a complete flash-funded profit has been proved.
