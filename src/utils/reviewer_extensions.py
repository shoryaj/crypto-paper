"""Reproducible reserve calibration and structural scaling experiments.

The historical reserve numbers are transcribed from Fig. 4 of Qin et al.,
Financial Cryptography and Data Security (2021), DOI
10.1007/978-3-662-64322-8_1.  All lender parameters below are explicitly
counterfactual.  The historical bZx transaction is not replayed.
"""
import json
import platform
import time
from fractions import Fraction
from pathlib import Path
from statistics import median

import z3

from case_studies.bzx_exploit import run
from src.core.analysis import optimal_candidates
from src.core.verifier import DeFiEconomicVerifier, replay


ROOT = Path("results/reviewer_extensions")


def historical_reserve_case():
    x = Fraction("243441.12")  # sUSD, Uniswap pool before the February 2020 trade
    y = Fraction("879.76")  # ETH
    f = Fraction("540")  # ETH input to the pool in the published trace
    observed_x1 = Fraction("151021.42")
    observed_y1 = Fraction("1419.76")
    # Hypothetical lender settings.  In the actual event, collateral was
    # acquired during the transaction, contrary to this model's pre-owned C.
    c, ltv, fee, cap, cash = "100000", "0.75", "0.0009", "540", "500"
    verifier = run(x_init=str(x), y_init=str(y), collateral_val=c,
                   ltv_val=ltv, fee_rate=fee, flash_cap=cap,
                   lending_cash=cash)
    result = verifier.verify_economic_invariant()
    analysis = optimal_candidates(str(x), str(y), c, ltv, fee, cap, cash)
    if result["status"] != "unknown":
        assert (result["status"] == "sat") == analysis["profitable"]
    if result["status"] == "sat":
        assert replay(result)
    modeled_x1 = x*y/(y+f)
    v = Fraction(c)*y/x
    borrow_at_f = min(Fraction(cash), v*Fraction(ltv)*(1+f/y)**2)
    data = {
        "source": "Qin et al. 2021, Fig. 4, doi:10.1007/978-3-662-64322-8_1",
        "source_type": "published rounded reserve figures, not an archive-node query",
        "historical_pool": {
            "before_susd": "243441.12", "before_eth": "879.76",
            "reported_after_susd": "151021.42",
            "reported_after_eth": "1419.76",
            "reported_eth_input": str(f),
        },
        "fee_free_counterfactual": {
            "after_susd": float(modeled_x1),
            "after_eth": float(y+f),
            "susd_output": float(x-modeled_x1),
            "observed_susd_output": float(x-observed_x1),
            "spot_multiplier": float((1+f/y)**2),
            "hypothetical_collateral_susd": c,
            "hypothetical_ltv": ltv,
            "hypothetical_flash_fee_rate": fee,
            "hypothetical_lender_cash_eth": cash,
            "reference_collateral_value_eth": float(v),
            "borrow_at_reported_input_eth": float(borrow_at_f),
            "profit_at_reported_input_eth": float(borrow_at_f-v-Fraction(fee)*f),
        },
        "z3": {"status": result["status"],
               "check_ms": result["elapsed_ms"],
               "witness_replayed": replay(result) if result["status"] == "sat" else None},
        "analytical": analysis,
        "scope": "Historical AMM reserves only; not a bZx attack replay or historical profit estimate",
    }
    return data


def structural_scaling():
    rows = []
    for count in [1, 2, 4, 8, 16, 32]:
        trials = []
        for repeat in range(3):
            verifier = DeFiEconomicVerifier(timeout_ms=30000)
            graph = {
                "pools": {f"p{i}": ["A", "B", "1000", "1000"]
                          for i in range(count)},
                "balances": {"A": "1000", "B": "0"},
                "actions": [{"pool": f"p{i}",
                             "amount": z3.Real(f"amount_{i}"), "parents": []}
                            for i in range(count)],
            }
            start = time.perf_counter_ns()
            verifier.encode_multi_pool_dag(graph)
            assertions = len(verifier.solver.assertions())
            encoded_ms = (time.perf_counter_ns()-start)/1e6
            start = time.perf_counter_ns()
            decision = verifier.verify_dag_conservation()
            check_ms = (time.perf_counter_ns()-start)/1e6
            assert decision == {"status": "unsat", "feasible": True}
            trials.append({"encode_ms": encoded_ms, "check_ms": check_ms})
        rows.append({"independent_pools": count, "symbolic_swaps": count,
                     "assertions": assertions,
                     "median_encode_ms": median(t["encode_ms"] for t in trials),
                     "median_feasibility_and_conservation_ms":
                         median(t["check_ms"] for t in trials),
                     "status": "feasible; conservation counterexample UNSAT",
                     "trials": trials})
    return {"scope": "Auxiliary distinct-pool DAG conservation, not core attack-synthesis scalability",
            "platform": platform.platform(), "python": platform.python_version(),
            "z3": z3.get_version_string(), "rows": rows}


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    historical = historical_reserve_case()
    scaling = structural_scaling()
    (ROOT/"historical_reserve_case.json").write_text(
        json.dumps(historical, indent=2), encoding="utf-8")
    (ROOT/"structural_scaling.json").write_text(
        json.dumps(scaling, indent=2), encoding="utf-8")
    print(json.dumps({"historical": historical, "scaling": scaling}, indent=2))


if __name__ == "__main__":
    main()
