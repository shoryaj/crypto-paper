"""Run one flash-loan model scenario from the command line.

Examples:
    python -m src.cli
    python -m src.cli --scenario examples/historical_reserves.json
    python -m src.cli --scenario examples/baseline.json --json-out run.json
"""

import argparse
import json
from fractions import Fraction
from pathlib import Path

import sympy as sp

from src.core.analysis import optimal_candidates
from src.core.verifier import DeFiEconomicVerifier, replay


DEFAULT_PARAMETERS = {
    "x_init": "1000",
    "y_init": "1000",
    "ltv_val": "0.75",
    "fee_rate": "0.0009",
    "collateral_val": "100",
    "flash_cap": "1000",
    "lending_cash": "400",
    "oracle": "spot",
    "epsilon": "0",
}
ALLOWED_PARAMETERS = set(DEFAULT_PARAMETERS) | {"gamma"}


def load_scenario(path):
    """Read data only; reject unexpected fields instead of silently ignoring them."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Scenario must be a JSON object")
    unknown = set(data) - {"name", "description", "source", "parameters"}
    if unknown:
        raise ValueError(f"Unknown scenario fields: {sorted(unknown)}")
    params = data.get("parameters", {})
    if not isinstance(params, dict):
        raise ValueError("parameters must be a JSON object")
    unknown = set(params) - ALLOWED_PARAMETERS
    if unknown:
        raise ValueError(f"Unknown parameter fields: {sorted(unknown)}")
    if any(isinstance(value, (dict, list, bool)) for value in params.values()):
        raise ValueError("Each parameter must be a number or decimal string")
    return data, {**DEFAULT_PARAMETERS, **params}


def run_scenario(parameters, *, query_path=None):
    """Return solver decision and, for spot prices, the exact analytical test."""
    if query_path is not None:
        Path(query_path).parent.mkdir(parents=True, exist_ok=True)
    verifier = DeFiEconomicVerifier()
    verifier.setup_protocol_states(**parameters)
    verifier.encode_flash_swap_logic()
    verifier.encode_lending_borrow_logic()
    solver = verifier.verify_economic_invariant(export_path=query_path)
    solver["witness_replayed"] = replay(solver) if solver["status"] == "sat" else None
    if solver["status"] == "sat" and not solver["witness_replayed"]:
        raise RuntimeError("SAT witness failed exact rational replay")

    analysis = None
    agrees = None
    if parameters.get("oracle", "spot") == "spot":
        effective_cap = Fraction(str(parameters["flash_cap"]))
        if parameters.get("gamma") is not None:
            effective_cap = min(effective_cap, Fraction(str(parameters["gamma"]))
                                * Fraction(str(parameters["y_init"])))
        analysis = optimal_candidates(
            parameters["x_init"], parameters["y_init"],
            parameters["collateral_val"], parameters["ltv_val"],
            parameters["fee_rate"], effective_cap,
            parameters["lending_cash"],
        )
        if solver["status"] != "unknown":
            agrees = (solver["status"] == "sat") == analysis["profitable"]
            if not agrees:
                raise RuntimeError("Analytical and Z3 decisions disagree")
    return {
        "model_scope": "Fixed fee-free swap, lend, reverse schedule; non-recourse collateral forfeiture",
        "solver": solver,
        "spot_analytical_baseline": analysis,
        "decisions_agree": agrees,
        "limitations": (
            "This checks an abstract model, not deployed contracts or a historical transaction. "
            "A SAT witness is feasible, not necessarily optimal."
        ),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", type=Path, help="JSON scenario file")
    parser.add_argument("--json-out", type=Path, help="Save the full result as JSON")
    parser.add_argument("--query-out", type=Path, help="Save the exact SMT-LIB query")
    args = parser.parse_args(argv)
    try:
        if args.scenario:
            scenario, parameters = load_scenario(args.scenario)
        else:
            scenario, parameters = {"name": "Synthetic baseline"}, DEFAULT_PARAMETERS.copy()
        result = run_scenario(parameters, query_path=args.query_out)
        result["scenario"] = scenario.get("name", "Unnamed scenario")
        result["description"] = scenario.get("description", "")
        result["source"] = scenario.get("source", "")
        if args.json_out:
            args.json_out.parent.mkdir(parents=True, exist_ok=True)
            args.json_out.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"Scenario: {result['scenario']}")
        print(f"Z3 decision: {result['solver']['status'].upper()}")
        if result["solver"]["status"] == "sat":
            witness = result["solver"]["witness"]
            print(f"Witness: flash={witness['f']} B, borrow={witness['borrow']} B, "
                  f"net extraction={witness['profit']} B")
            print(f"Exact witness replay: {result['solver']['witness_replayed']}")
        elif result["solver"]["status"] == "unknown":
            print(f"Unresolved: {result['solver'].get('reason_unknown', 'no reason supplied')}")
        if result["spot_analytical_baseline"] is not None:
            baseline = result["spot_analytical_baseline"]
            print(f"Analytical profitable: {baseline['profitable']}")
            print(f"Analytical maximum/supremum: {baseline['profit_star_or_supremum']} B")
            approx = sp.N(sp.sympify(baseline["profit_star_or_supremum"]), 8)
            print(f"Approximate value: {approx} B")
            print(f"Analytical and Z3 decisions agree: {result['decisions_agree']}")
        print(result["limitations"])
        if args.json_out:
            print(f"Full result: {args.json_out}")
        if args.query_out:
            print(f"SMT-LIB query: {args.query_out}")
        return 0
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        parser.exit(2, f"error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
