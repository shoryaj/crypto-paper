"""Analytical optimum and sufficient liquidity bound for the core model."""
import sympy as sp


def derive():
    f, y, V, L, r = sp.symbols('f y V L r', positive=True)
    profit = V*L*(1+f/y)**2-V-r*f
    first = sp.diff(profit, f)
    second = sp.diff(first, f)
    return {'profit': str(profit), 'derivative': str(first),
            'second_derivative': str(second),
            'stationary_minimum': str(sp.solve(first, f)[0])}


def optimal_candidates(x, y, c, ltv, fee, cap, cash):
    """Exact finite candidate reduction; zero is the excluded endpoint limit.

    Negative candidates need not meet repayment feasibility: positive profit
    implies that constraint. A returned maximum <=0 proves no profitable trace.
    """
    x, y, c, ltv, fee, cap, cash = map(lambda v: sp.Rational(str(v)),
                                     (x, y, c, ltv, fee, cap, cash))
    if not (x>0 and y>0 and c>=0 and 0<ltv<1 and fee>=0 and cap>0 and cash>=0):
        raise ValueError('Invalid parameters')
    V, a = c*y/x, c*y/x*ltv
    points = [sp.S(0), cap]
    if a > 0 and cash >= a:
        kink = y*(sp.sqrt(cash/a)-1)
        if 0 <= kink <= cap:
            points.append(kink)
    values = [(f, sp.Min(cash, a*(1+f/y)**2)-V-fee*f) for f in points]
    best = max(values, key=lambda item: item[1])
    return {'candidates': [(str(f), str(p)) for f, p in values],
            'f_star_or_limit': str(best[0]), 'profit_star_or_supremum': str(best[1]),
            'profitable': bool(best[1] > 0),
            'maximum_attained': bool(best[0] > 0)}


def sufficient_liquidity(V, ltv, fee, cap, p0=1):
    """Fixed flash cap and fixed external price; conservative for any cash cap.

    y_min = F/(sqrt((V+rF)/(VL))-1); k_min_sufficient=y_min^2/p0.
    This is NOT a necessary bound when the lending cash cap binds.
    """
    V, ltv, fee, cap, p0 = map(lambda v: sp.Rational(str(v)),
                              (V, ltv, fee, cap, p0))
    if not (V>0 and 0<ltv<1 and fee>=0 and cap>0 and p0>0):
        raise ValueError('Positive value, cap, price and valid LTV required')
    y = cap/(sp.sqrt((V+fee*cap)/(V*ltv))-1)
    return {'y_min': str(y), 'k_min_sufficient': str(y*y/p0),
            'k_approx': float(y*y/p0)}
