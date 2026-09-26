"""Behavioral checks, independent arithmetic replay, and regression boundaries."""
import pytest
import z3
from case_studies.bzx_exploit import run
from case_studies.harvest_exploit import run as harvest
from case_studies.euler_exploit import run as euler
from src.core.verifier import DeFiEconomicVerifier, replay
from src.core.analysis import optimal_candidates
from src.core.uint256 import check_roundtrip
from src.core.amm_model import concentrated_range


def test_spot_witness_replays():
    result = run().verify_economic_invariant()
    assert result['status'] == 'sat'
    assert replay(result)


@pytest.mark.parametrize('oracle', ['bounded', 'dynamic'])
def test_mitigation(oracle):
    assert run(oracle, epsilon='0.1').verify_economic_invariant()['status'] == 'unsat'


def test_loose_bound_is_not_automatically_safe():
    assert run('bounded', epsilon='1').verify_economic_invariant()['status'] == 'sat'


def test_no_collateral_no_extraction():
    assert run(collateral_val=0).verify_economic_invariant()['status'] == 'unsat'


def test_cash_cap_covers_collateral_cost():
    assert run(lending_cash=100).verify_economic_invariant()['status'] == 'unsat'


@pytest.mark.parametrize('fixed,expected', [(False,'sat'),(True,'unsat')])
def test_vault(fixed, expected):
    assert harvest(fixed)['status'] == expected


@pytest.mark.parametrize('fixed,expected', [(False,'sat'),(True,'unsat')])
def test_donation_health(fixed, expected):
    assert euler(fixed)['status'] == expected


def test_dag_conservation():
    v = DeFiEconomicVerifier()
    v.encode_multi_pool_dag({'pools': {'ab':['A','B',1000,1000],
                                      'bc':['B','C',1000,1000]},
        'balances': {'A':100}, 'actions': [dict(pool='ab',amount=100),
                                          dict(pool='bc',amount=50,parents=[0])]})
    assert v.verify_dag_conservation() == {'status':'unsat','feasible':True}


def test_dag_double_spend_rejected():
    v = DeFiEconomicVerifier()
    v.encode_multi_pool_dag({'pools': {'ab':['A','B',1000,1000],
                                      'ac':['A','C',1000,1000]},
        'balances': {'A':100}, 'actions': [dict(pool='ab',amount=100),
                                          dict(pool='ac',amount=100)]})
    assert v.verify_dag_conservation()['feasible'] is False


def test_dag_cycle_rejected():
    v = DeFiEconomicVerifier()
    with pytest.raises(ValueError):
        v.encode_multi_pool_dag({'pools':{'ab':['A','B',1000,1000]},
            'balances':{'A':100},'actions':[dict(pool='ab',amount=1,parents=[0])]})


@pytest.mark.parametrize('f', [1,2,19,100,1000])
def test_integer_roundtrip(f):
    result = check_roundtrip(1000,1000,f)
    assert result['status'] == 'sat'
    out = 1000*f//(1000+f)
    back = (1000+f)*out//1000
    assert result['a_out'] == out and result['returned'] == back <= f


def test_checked_overflow_reverts():
    assert check_roundtrip(2**256-1,1000,2)['status'] == 'unsat'


def test_concentrated_range():
    s=z3.SolverFor('QF_NRA')
    amount,out=concentrated_range(s,z3.RealVal(100),z3.RealVal(1),
                                 z3.RealVal(2),z3.RealVal(1),z3.RealVal(3),'cl')
    s.add(z3.Or(amount != 100,out != 50))
    assert s.check() == z3.unsat


@pytest.mark.parametrize('reserve', [100,1000,10000])
@pytest.mark.parametrize('ltv', ['0.5','0.75','0.95'])
def test_analytic_smt_agreement(reserve,ltv):
    expected=optimal_candidates(reserve,reserve,100,ltv,'0.003',1000,400)
    result=run(x_init=reserve,y_init=reserve,ltv_val=ltv,fee_rate='0.003').verify_economic_invariant()
    assert (result['status']=='sat') == expected['profitable']
    if result['status']=='sat':
        assert replay(result)


def test_invalid_parameters():
    with pytest.raises(ValueError):
        run(ltv_val=1)


def test_unknown_is_inconclusive():
    verifier=run()
    verifier.solver.set(rlimit=1)
    result=verifier.verify_economic_invariant()
    assert result['status']=='unknown'
    assert result['reason_unknown']
    assert 'witness' not in result
