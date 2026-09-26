"""Bounded atomic manipulation verifier with exact rational witness replay.

    SAT supplies a witness, never an optimality claim. UNSAT certifies only
    absence of the encoded behavior, trusting Z3; it is not a proof object.
"""
from fractions import Fraction
from pathlib import Path
import time
import z3
from .amm_model import cpmm
from .lending_model import borrowing


def Q(value):
    """Convert decimal text/rationals without introducing binary floats."""
    return z3.RealVal(str(value))


class DeFiEconomicVerifier:
    def __init__(self, logic='QF_NRA', timeout_ms=30000):
        if logic != 'QF_NRA':
            raise ValueError('Use the separate uint256 verifier for bit-vectors')
        self.solver = z3.SolverFor(logic)
        self.solver.set(timeout=timeout_ms)
        self.stage = 0

    def setup_protocol_states(self, x_init, y_init, ltv_val, fee_rate,
                              collateral_val, *, flash_cap=10000,
                              lending_cash=10000, oracle='spot', epsilon='0',
                              gamma=None):
        """A collateral, B debt/numeraire. Attacker initially owns C A.

        Collateral is forfeited after borrowing: non-recourse debt assumption.
        Flash loan is in B (the price-inflating direction). No external trades.
        """
        if self.stage:
            raise RuntimeError('Construct a new verifier for each scenario')
        vals = list(map(lambda v: Fraction(str(v)),
                        [x_init, y_init, ltv_val, fee_rate, collateral_val,
                         flash_cap, lending_cash, epsilon]))
        x, y, ltv, fee, c, cap, cash, eps = vals
        if not (x > 0 and y > 0 and 0 < ltv < 1 and fee >= 0
                and c >= 0 and cap > 0 and cash >= 0 and eps >= 0):
            raise ValueError('Invalid economic parameter domain')
        if oracle not in ('spot', 'bounded', 'dynamic'):
            raise ValueError('Unsupported oracle policy')
        if gamma is not None:
            if Fraction(str(gamma)) <= 0:
                raise ValueError('gamma must be positive')
            cap = min(cap, Fraction(str(gamma)) * y)
        self.parameters = dict(x=str(x), y=str(y), ltv=str(ltv), fee=str(fee),
                               collateral=str(c), flash_cap=str(cap), cash=str(cash),
                               oracle=oracle, epsilon=str(eps))
        self.x, self.y, self.ltv, self.r, self.c, self.F, self.T, self.eps = map(
            Q, [x, y, ltv, fee, c, cap, cash, eps])
        self.oracle_policy = oracle
        self.p0 = self.y / self.x
        self.f = z3.Real('f')
        self.solver.add(self.f > 0, self.f <= self.F)
        self.stage = 1

    def encode_flash_swap_logic(self):
        """B -> A manipulation, then reserve-restoring A -> B reversal."""
        if self.stage != 1:
            raise RuntimeError('Call setup first')
        self.y1, self.x1, self.a_out = cpmm(
            self.solver, self.y, self.x, self.f, 'a_out')
        self.price = z3.Real('spot_price')
        self.solver.add(self.price * self.x1 == self.y1)
        self.x2, self.y2, self.b_return = cpmm(
            self.solver, self.x1, self.y1, self.a_out, 'b_return')
        self.stage = 2

    def encode_lending_borrow_logic(self):
        """Oracle read occurs before reversal; repayment occurs afterwards."""
        if self.stage != 2:
            raise RuntimeError('Encode swaps first')
        oracle = self.price
        ltv = self.ltv
        if self.oracle_policy == 'bounded':
            oracle = z3.Real('bounded_price')
            self.solver.add(oracle > 0, oracle <= self.p0 * (1 + self.eps))
        elif self.oracle_policy == 'dynamic':
            # Rational inverse-distortion rule, NOT the requested exponential.
            ltv = z3.Real('dynamic_ltv')
            self.solver.add(ltv > 0, ltv * (self.y + self.f)**2
                           == self.ltv * self.y**2)
        self.borrow = borrowing(self.solver, self.c, oracle, ltv, self.T)
        self.wallet_final = self.borrow + self.b_return - self.f * (1 + self.r)
        self.profit = self.wallet_final - self.c * self.p0
        self.solver.add(self.wallet_final >= 0)
        self.stage = 3

    def encode_multi_pool_dag(self, pool_graph):
        """Add a separately funded, finite swap DAG and its token ledgers.

        Schema: pools={id:[token_in,token_out,reserve_in,reserve_out]},
        balances={token:amount}, actions=[{pool,amount,parents:[earlier index]}].
        Amount may be an exact constant or a Z3 Real. Actions are topologically
        ordered; balances prevent spending outputs twice. Each pool is used
        once. This module composes swaps, not arbitrary contract calls; its
        terminal wallets are NOT silently added to the core profit expression.
        Call verify_dag_conservation for its separate conservation property.
        """
        if hasattr(self, 'dag'):
            raise RuntimeError('Only one DAG per verifier')
        pools = pool_graph['pools']
        balances = {t: Q(v) for t, v in pool_graph['balances'].items()}
        initial = dict(balances)
        used = set()
        totals = dict(initial)
        reserves = {}
        for pid, (a, b, x, y) in pools.items():
            if a == b:
                raise ValueError('Pool tokens must differ')
            reserves[pid] = (a, b, Q(x), Q(y))
            for t, v in [(a, Q(x)), (b, Q(y))]:
                self.solver.add(v > 0)
                totals[t] = totals.get(t, Q(0)) + v
                balances.setdefault(t, Q(0))
        for v in balances.values():
            self.solver.add(v >= 0)
        for i, action in enumerate(pool_graph['actions']):
            if any(p < 0 or p >= i for p in action.get('parents', [])):
                raise ValueError('Actions must be a topologically ordered DAG')
            pid = action['pool']
            if pid in used:
                raise ValueError('A pool may occur only once in this DAG')
            used.add(pid)
            a, b, x, y = reserves[pid]
            amount = action['amount']
            amount = amount if isinstance(amount, z3.ArithRef) else Q(amount)
            self.solver.add(amount <= balances[a])
            nx, ny, out = cpmm(self.solver, x, y, amount, 'dag_out_' + str(i))
            balances[a] -= amount
            balances[b] += out
            reserves[pid] = (a, b, nx, ny)
        final_totals = dict(balances)
        for a, b, x, y in reserves.values():
            final_totals[a] = final_totals.get(a, Q(0)) + x
            final_totals[b] = final_totals.get(b, Q(0)) + y
        self.dag = (totals, final_totals, balances)
        return balances

    def verify_dag_conservation(self):
        """Check feasibility before conservation, avoiding vacuous success."""
        initial, final, _ = self.dag
        feasible = self.solver.check()
        if feasible != z3.sat:
            return {'status': str(feasible), 'feasible': False}
        self.solver.push()
        self.solver.add(z3.Or(*[initial[t] != final[t] for t in initial]))
        status = self.solver.check()
        self.solver.pop()
        return {'status': str(status), 'feasible': True}

    def verify_economic_invariant(self, export_path=None):
        """Check existential negation of forall f: feasible(f) => profit<=0."""
        if self.stage != 3:
            raise RuntimeError('Encode the lending model first')
        self.solver.push()
        self.solver.add(self.profit > 0)
        if export_path:
            Path(export_path).write_text(self.solver.to_smt2(), encoding='utf-8')
        start = time.perf_counter_ns()
        status = self.solver.check()
        result = {'status': str(status), 'elapsed_ms': (time.perf_counter_ns()-start)/1e6,
                  'parameters': self.parameters, 'z3_version': z3.get_version_string(),
                  'statistics': str(self.solver.statistics())}
        if status == z3.sat:
            model = self.solver.model()
            result['witness'] = {n: str(model.eval(v, model_completion=True)) for n, v in
                [('f', self.f), ('a_out', self.a_out), ('price', self.price),
                 ('borrow', self.borrow), ('b_return', self.b_return),
                 ('profit', self.profit), ('wallet_final', self.wallet_final)]}
            result['interpretation'] = 'Feasible counterexample; not an optimum'
        elif status == z3.unknown:
            result['reason_unknown'] = self.solver.reason_unknown()
        else:
            result['interpretation'] = 'Invariant holds only for this encoded model'
        self.solver.pop()
        return result


def replay(result):
    """Independent Fraction replay for the core model; no SMT evaluation.

    Algebraic (irrational) witnesses require interval replay and are rejected
    explicitly by Fraction rather than rounded to a misleading decimal.
    """
    p, w = result['parameters'], result['witness']
    x, y, c, ltv, r, cap, cash, eps = [Fraction(p[n]) for n in
        ('x', 'y', 'collateral', 'ltv', 'fee', 'flash_cap', 'cash', 'epsilon')]
    f, b = Fraction(w['f']), Fraction(w['borrow'])
    a = x * f / (y + f)
    price = (y + f)**2 / (x*y)
    oracle_max = y/x*(1+eps) if p['oracle'] == 'bounded' else price
    effective_ltv = ltv*y*y/(y+f)**2 if p['oracle'] == 'dynamic' else ltv
    returned = (y+f)*a/(x-a+a)
    profit = b + returned - f*(1+r) - c*y/x
    return (0 < f <= cap and 0 <= b <= cash and b <= c*oracle_max*effective_ltv
            and returned == f and profit > 0
            and profit == Fraction(w['profit']) and a == Fraction(w['a_out'])
            and price == Fraction(w['price'])
            and returned == Fraction(w['b_return'])
            and b+returned-f*(1+r) == Fraction(w['wallet_final']))
