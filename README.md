# Economic invariant analysis of a DeFi flash-loan model

I study how a flash loan can distort the spot price of a constant-product AMM and affect a connected lending protocol. I derive exact profit conditions and mitigation bounds for a fixed transaction sequence, then check the model with Python and Z3. The repository contains my paper, source code, tests, figures, and experiment data.

## Project files

| Location | What I put there |
| --- | --- |
| [`paper/Research_Paper.pdf`](paper/Research_Paper.pdf) and [`paper/Research_Paper.docx`](paper/Research_Paper.docx) | My current paper in PDF and editable Word formats. |
| [`FORMALIZATION.md`](FORMALIZATION.md) | The model assumptions, equations, and proofs. |
| [`src/core/`](src/core/) | The AMM, lending, analytical, and Z3 verification code. |
| [`case_studies/`](case_studies/) | Small bZx-inspired, Harvest, and Euler models. |
| [`tests/`](tests/) | Automated checks of the model and its controls. |
| [`results/`](results/) | Saved solver decisions, SMT-LIB queries, measurements, and case outputs. |
| [`paper/figures/`](paper/figures/) | Figures for the paper and a plot of the saved experiment. |
| [`src/cli.py`](src/cli.py) and [`examples/`](examples/) | A single-scenario command I can run in VS Code, including a clearly labeled historical-reserve counterfactual. |

## Run the project

From the repository root, use Python 3.12 or newer. On Windows, I run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q
python -m src.utils.benchmark
python -m src.utils.reviewer_extensions
python -m src.utils.plot_results
python -m src.utils.report
```

To demonstrate the coding part without rerunning the full sweep, I use:

```powershell
python -m src.cli --scenario examples/baseline.json --json-out demo-result.json --query-out demo-query.smt2
python -m src.cli --scenario examples/historical_reserves.json
```

The first command prints a Z3 decision, a rationally replayed witness, the analytical maximum or supremum, and whether the two decision methods agree. It also saves the complete result and the exact SMT-LIB query for inspection. The second command uses published bZx pool reserves with **hypothetical** lender parameters; it is not a replay of the historical attack. I can edit the decimal strings in either JSON file to test another scenario. The `demo-result.json` and `demo-query.smt2` files are local demonstration outputs and are ignored by Git.

The benchmark writes to `results/`, so a rerun can replace the saved output files. I recommend committing or copying the supplied results before rerunning it if you want to compare runs. The measured experiment includes 90 parameter settings with three Z3 calls each: 204 SAT, 66 UNSAT, and no UNKNOWN results. The analytical decision agrees with every setting. The paper's recorded test run had 31 passing tests; the current suite, including the command-line checks, has 36.

## What the results mean

My core model uses a fixed, fee-free AMM swap–borrow–reverse sequence and an explicit non-recourse collateral assumption. Its analytical criterion is the primary decision method; Z3 provides a separate constraint-encoding check. The historical-reserve case uses published rounded sUSD/ETH pool figures with hypothetical lending settings, so it is a sensitivity test rather than a replay of the bZx transaction. The pool-scaling experiment checks conservation in an auxiliary model, not attack-synthesis scalability. I do not claim that this work verifies deployed contracts or outperforms other DeFi tools.

The repository has no archival DOI. The paper includes an AI-assistance disclosure.
