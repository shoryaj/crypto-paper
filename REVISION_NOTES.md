# Reviewer comment disposition

The revised Word paper is the current manuscript. Changes were checked against the supplied reviewer report.

| Request | Disposition |
| --- | --- |
| Match title to model scope; state contributions; answer research questions | Revised title and Sections 1 and 8 |
| Repair terminology, Theorem 1, square root, broken tables and orphaned text | Rebuilt Word paper from the clean model and rerendered |
| Explain role of SMT given the closed form | Sections 1 and 7.2 explicitly make the analytical criterion primary |
| Show the coding work in the manuscript | Section 5.1 maps equations and experiments to repository paths, prints short excerpts from the AMM constraint and verifier accounting, and gives reproduction commands. The full source remains in the repository; code screenshots were avoided in the main paper. |
| Position work against DeFiPoser, Clockwork Finance, FlashSyn, FORAY | Section 6 scope comparison with published citations |
| Expand bibliography, cite Z3, SymPy, AMM/oracle work | 13 references, including published versions where verified |
| Replace output screenshots, repair plot labels | Five clean model/data figures; screenshot evidence is not in the revised paper |
| Verify Z3 version | Installed Python API reports 5.1.0; saved environment file agrees |
| Add author, code availability, DOI, funding/conflict and AI statements | Author supplied a university affiliation, contact email, and declarations of no funding and no conflicts; these are in the revised paper. The private repository URL and AI disclosure are included. An archival DOI is not assigned. |
| Historical reserve calibration | Added a case using rounded February 2020 Uniswap sUSD/ETH reserves published by Qin et al. The other lender parameters are hypothetical; it is not a transaction replay. See Section 7.3 and `results/reviewer_extensions/historical_reserve_case.json`. |
| Scalability study | Added a limited auxiliary model-size experiment with 1–32 symbolic distinct-pool swaps and three fresh runs per size. It checks token conservation, not core attack synthesis. See Section 7.4 and `results/reviewer_extensions/structural_scaling.json`. |
| Executable comparison with existing DeFi verifier | Still not complete. The paper identifies FlashSyn's public artifact, setup, and semantic differences; no matched head-to-head benchmark is claimed. |
