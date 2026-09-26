"""Fee-free CPMM and single-range concentrated-liquidity primitives."""
import z3


def cpmm(solver, reserve_in, reserve_out, amount, name):
    """Transfer amount in, output out; require strictly positive reserves.

    Polynomial equality avoids division with an unconstrained denominator.
    This primitive excludes swap fees, rebasing and fee-on-transfer assets.
    """
    output = z3.Real(name)
    solver.add(reserve_in > 0, reserve_out > 0, amount >= 0,
               output >= 0, output < reserve_out,
               (reserve_in + amount) * (reserve_out - output)
               == reserve_in * reserve_out)
    return reserve_in + amount, reserve_out - output, output


def concentrated_range(solver, liquidity, sqrt_before, sqrt_after,
                       lower, upper, name):
    """B-input swap within ONE active range; no tick crossing or fees.

    A_out = L(1/s_before - 1/s_after), B_in = L(s_after-s_before).
    All sqrt prices are positive, so cross multiplication is equivalent.
    """
    amount, output = z3.Reals(name + '_in ' + name + '_out')
    solver.add(liquidity > 0, lower > 0, upper > lower,
               sqrt_before >= lower, sqrt_after <= upper,
               sqrt_after >= sqrt_before,
               amount == liquidity * (sqrt_after - sqrt_before),
               output * sqrt_before * sqrt_after
               == liquidity * (sqrt_after - sqrt_before))
    return amount, output
