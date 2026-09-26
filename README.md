# Crypto paper: economic invariant analysis for DeFi

This repository contains Shorya Jaiswal's revised research paper, an executable Python/Z3 model, synthetic experiment data, and the code used to generate the figures. The core result concerns a **fixed, abstract, single-transaction AMM and lender composition**. It is not a deployed-contract audit or a historical attack replay.

## Start here

- Revised paper: `paper/Shorya_Jaiswal_Revised_Research_Paper.docx` (PDF reading copy alongside it)
- Mathematical definitions and proofs: `FORMALIZATION.md`
- Python verifier: `src/core/`
- Simplified case studies: `case_studies/`
- Automated tests: `tests/`
- Saved synthetic results and exported SMT-LIB queries: `results/`
- Figure-generation scripts: `paper/scripts/`

## Reproduce

Use Python 3.12 or newer from this repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q
python -m src.utils.benchmark
python -m src.utils.plot_results
python -m src.utils.report
```

The saved run used Python 3.14.7, Z3 5.1.0, and SymPy 1.14.0. Its 90 distinct synthetic settings were each repeated three times, yielding 204 SAT, 66 UNSAT, and zero UNKNOWN solver calls. All core SAT witnesses were replayed with exact rational arithmetic. The 31 automated tests passed in the saved test log. Timing and memory figures are descriptive of this recorded run.

The benchmark rewrites files in `results/`; commit your rerun separately if you want to compare it to the supplied data. Each exported `.smt2` file is one query from the recorded sweep.

## Scope and research integrity

The analytical candidate rule decides the fixed core model. Z3 checks an independent constraint encoding, while the case-study models abstract different historical mechanisms. The manuscript does not claim original on-chain reserve calibration, cross-tool performance superiority, or security of a deployed protocol. See `REVISION_NOTES.md` for the status of reviewer requests.

The `paper/research-paper.tex` file is an earlier visual edition; the revised Word document is the current submission draft. No archival DOI has been assigned. Funding and conflict declarations require author confirmation before submission. AI assistance is disclosed in the manuscript.
