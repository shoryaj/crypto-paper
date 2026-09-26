"""Check the public command-line path, not just its internal helpers."""

import json
from pathlib import Path

import pytest

from src.cli import load_scenario, main, run_scenario


ROOT = Path(__file__).resolve().parents[1]


def test_baseline_command_writes_reproducible_outputs(tmp_path, capsys):
    result_path = tmp_path / "result.json"
    query_path = tmp_path / "query.smt2"
    assert main(["--scenario", str(ROOT / "examples/baseline.json"),
                 "--json-out", str(result_path), "--query-out", str(query_path)]) == 0
    result = json.loads(result_path.read_text(encoding="utf-8"))
    assert result["solver"]["status"] == "sat"
    assert result["solver"]["witness_replayed"] is True
    assert result["spot_analytical_baseline"]["profitable"] is True
    assert result["decisions_agree"] is True
    assert "(check-sat)" in query_path.read_text(encoding="utf-8")
    assert "Z3 decision: SAT" in capsys.readouterr().out


def test_historical_input_is_explicitly_counterfactual():
    data, parameters = load_scenario(ROOT / "examples/historical_reserves.json")
    assert "hypothetical" in data["description"].lower()
    result = run_scenario(parameters)
    assert result["solver"]["status"] == "sat"
    assert result["decisions_agree"] is True


def test_bounded_oracle_does_not_claim_spot_closed_form():
    _, parameters = load_scenario(ROOT / "examples/baseline.json")
    parameters.update(oracle="bounded", epsilon="0.1")
    result = run_scenario(parameters)
    assert result["solver"]["status"] == "unsat"
    assert result["spot_analytical_baseline"] is None
    assert result["decisions_agree"] is None


def test_gamma_applies_to_both_solver_and_analytical_cap():
    _, parameters = load_scenario(ROOT / "examples/baseline.json")
    parameters["gamma"] = "0.1"
    result = run_scenario(parameters)
    assert result["solver"]["parameters"]["flash_cap"] == "100"
    assert result["decisions_agree"] is True
    assert result["spot_analytical_baseline"]["f_star_or_limit"] == "100"


def test_unknown_config_field_is_rejected(tmp_path):
    scenario = tmp_path / "invalid.json"
    scenario.write_text('{"parameters": {"cash_cap_typo": "400"}}', encoding="utf-8")
    with pytest.raises(ValueError, match="Unknown parameter fields"):
        load_scenario(scenario)
