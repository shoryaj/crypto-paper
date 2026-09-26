"""Optional exact uint256 trace checking, not an EVM-wide refinement proof.

Output is floor(reserve_out*amount/(reserve_in+amount)). Checked arithmetic
rejects overflow, matching this specified expression's Solidity 0.8 semantics.
The concrete input trace is checked using QF_BV, unsigned UDiv and ZeroExt.
"""
import z3


def check_roundtrip(x, y, f, timeout_ms=30000):
    if not all(isinstance(v, int) and 0 < v < 2**256 for v in (x, y, f)):
        raise ValueError('Positive uint256 inputs required')
    s = z3.SolverFor('QF_BV')
    s.set(timeout=timeout_ms)
    X, Y, F = [z3.BitVecVal(v, 256) for v in (x, y, f)]
    limit = z3.BitVecVal(2**256-1, 512)
    wide = lambda v: z3.ZeroExt(256, v)
    s.add(z3.ULE(wide(Y)+wide(F), limit),
          z3.ULE(wide(X)*wide(F), limit))
    out = z3.simplify(z3.UDiv(X*F, Y+F))
    s.add(z3.ULT(out, X))
    s.add(z3.ULE((wide(Y)+wide(F))*wide(out), limit))
    returned = z3.simplify(z3.UDiv((Y+F)*out, X))
    status = s.check()
    result = {'status': str(status), 'mode': 'concrete uint256 trace'}
    if status == z3.sat:
        result.update(a_out=out.as_long(), returned=returned.as_long(),
                      rounding_loss=f-returned.as_long())
    elif status == z3.unsat:
        result['interpretation'] = 'Trace reverts under checked arithmetic'
    else:
        result['reason_unknown'] = s.reason_unknown()
    return result
