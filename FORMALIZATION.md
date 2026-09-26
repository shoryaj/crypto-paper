# Formal model, proofs, and scope

## 1. Correct direction and units

Let x,y>0 be reserves in A,B, respectively, and p0=y/x be the external reference
price in B per A. A B-denominated flash loan f>0 increases A's spot price:

    y1=y+f; x1=xy/(y+f); a=x-x1=xf/(y+f);
    p1=y1/x1=(y+f)^2/(xy)=p0(1+f/y)^2.

The proposed A-input transition instead gives p1=xy/(x+f)^2<p0 and cannot inflate
A collateral. All wealth comparisons below use B units, not sums of token amounts.

## 2. State and atomic transitions

State S=(AMM reserves, attacker wallets, lender cash, collateral custody,
ordinary debt, flash obligation). Initially the attacker owns C A, valued at
V=C p0 B, and no B. Flash-provider cash is H>=F; lender cash is T>=0.
The external reference price stays fixed throughout the transaction.

| Stage | AMM (A,B) | Attacker liquid (A,B) | Custody A | Lender cash B | Ordinary debt B | Flash due B |
|---|---|---|---|---|---|---|
| Initial | x,y | C,0 | 0 | T | 0 | 0 |
| Flash | x,y | C,f | 0 | T | 0 | f(1+r) |
| Manipulate | x1,y1 | C+a,0 | 0 | T | 0 | f(1+r) |
| Pledge/borrow | x1,y1 | a,b | C | T-b | b | f(1+r) |
| Reverse | x,y | 0,b+f | C | T-b | b | f(1+r) |
| Repay | x,y | 0,b-rf | C | T-b | b | 0 |

Flash-provider balance changes from H to H-f to H+rf. The fee is a transfer,
not token creation. Each transfer conserves each token across all custodians.
Ordinary debt is explicitly outstanding at the end. We assume non-recourse
default, with all pledged collateral forfeited. Thus realized extraction after
collateral forfeiture is Pi=b-rf-V. This is not conventional marked-to-market
net worth while the full debt remains collectible. If the ordinary debt must
also be repaid in the transaction, Pi=-rf (collateral returned), so this attack
does not work. This assumption is central, not an implementation detail.

Full reversal returns f because a=x-x1 and
(y+f)a/(x1+a)=(y+f)(xf/(y+f))/x=f. Collateral C is pre-owned and separate
from the acquired a; none of the pledged tokens are sold in the reversal.
Borrow constraints are 0<=b<=T and b<=C L p1. Repayment additionally requires
b-rf>=0. Define extracted wallet value before flash repayment as E=b+f;
E-f(1+r)-V equals Pi. Omitting V creates false apparent profit from ordinary
collateralized borrowing; omitting recovered f double-counts manipulation cost.

## 3. Exact existential query and optimum

Let A0=VL>0. For 0<f<=F, maximum available profit is

    g(f)=min(T,A0(1+f/y)^2)-V-rf.

Encode the negation of security as the quantifier-free existential formula
Transitions AND 0<f<=F AND Pi>0. Free solver variables are existential. UNSAT
therefore establishes forall feasible f in this domain, Pi<=0, trusting the
encoding and solver. Positive profit implies repayment feasibility automatically.

On the uncapped branch:

    g'(f)=2A0/y+2A0 f/y^2-r;
    g''(f)=2A0/y^2>0;
    f_stationary=r y^2/(2A0)-y.

The stationary point is a strict minimum, if it lies on this branch. The capped
branch has derivative -r<=0. If T>=A0 the cap begins at

    fc=y(sqrt(T/A0)-1).

**Theorem 1 (finite candidate reduction).** The supremum of g on (0,F] is the
largest of g(0), g(F), and g(fc) when 0<=fc<=F. If T<A0 the cap is active
everywhere and endpoints suffice. Proof: a convex function on a closed interval
attains its maximum at an endpoint; the capped branch is nonincreasing. Split
[0,F] at fc and apply both facts. At f=0 use a limit, not an allowed flash loan.
Since g(0)<=V(L-1)<0, every positive maximum lies at an allowed nonzero candidate.
Consequently SAT iff this largest candidate value is strictly positive; equality
is UNSAT for the strict profit query. For C=0, no borrowing is possible and
Pi<=0 directly. The implementation handles this case separately.

**Concrete exact example.** x=y=1000,C=100,L=3/4,r=9/10000,F=1000,T=400.
At f=1000: a=500,p1=4,b=300,reverse=1000,fee=9/10,
Pi=300-100-9/10=1991/10 B. The cap kink is beyond F; the optimum is f*=1000.
At the same parameters with F=100 the convex endpoint profits are both negative.
These are synthetic parameters, not the bZx transaction parameters.

## 4. Mitigation theorems

**Theorem 2 (bounded oracle).** If 0<poracle<=p0(1+epsilon) and
L(1+epsilon)<=1, then b<=V and Pi<=-rf<=0. This proof is independent of the
pool distortion size. The bound must itself be established by the deployed
oracle implementation. A TWAP name alone supplies no such bound. Multi-block
manipulation, observation updates, manipulation duration, and oracle sampling
are outside this model. The tests include a loose bound that remains SAT.

**Theorem 3 (rational dynamic LTV).** Set L(f)=L0/(1+f/y)^2. Then
C p1 L(f)=VL0<V, implying no positive extraction. This is a hypothetical
policy with access to the modeled distortion; it is not a deployed oracle.

For the requested exponential rule L0 exp(-lambda f), log(1+u)<=u implies
L(f)p1 <= L0 p0 exp((2/y-lambda)f). Thus lambda>=2/y is a sufficient
condition for the same upper bound. This is an analytic sufficient result,
not an exact Z3 QF_NRA encoding of exp. Any polynomial approximation would
need a proved, directional remainder bound; this artifact does not use one.

## 5. Liquidity bounds and TVL

Fix p0, V>0, L in (0,1), flash cap F>0, fee r>=0. Ignoring the cash cap is
conservative because min(T,z)<=z. The uncapped endpoint g(F)<=0 iff

    y >= y_safe = F/(sqrt((V+rF)/(VL))-1).
    x=y/p0; k_safe=y_safe^2/p0.

By convexity and g(0)<0 this suffices for every allowed flash size. It is exact
for the uncapped model, but only sufficient with a binding T. The exact capped
criterion is Theorem 1. T<=V is already safe regardless of pool liquidity.
Lending TVL alone does not determine V or F, and k alone does not determine y
unless p0 is fixed. Therefore no universal k_min(TVL) follows from the prompt.
If flash capacity scales as F=gamma y, greater depth scales accessible loans
too; substitute that relation afresh rather than applying a fixed-F claim.
For unbounded f and r=0 with T>V, any finite pool can eventually reach the cap
and be profitable. These counterexamples delimit any claimed global guarantee.

## 6. Composition and precision

For any token t, sum of liquid balances and custody balances across every
participant is constant in a closed transfer-only system. Fees redistribute
balances. Claims/debts must be accounted separately without counting them as
new underlying tokens. Weighted conservation follows with fixed reference
prices. Summing gross outflows is not a conservation invariant: the same asset
can circulate through multiple pools and be counted repeatedly.

The DAG module consumes wallet inputs, credits outputs and updates reserves
in topological order. The local identity -input+input=0 and +output-output=0
proves conservation inductively over any finite number of actions. Branches
share a ledger, preventing double spending. Pools may appear once in this
module; the core five-step model separately revisits a pool for reversal.
This is not an arbitrary contract-call scheduler and the auxiliary DAG wallet
is not merged into the core lending profit query. Composition of lending,
vaults and liquidations requires explicit additional transition modules.

Real arithmetic omits atomic-unit rounding. The uint256 module uses unsigned
division, widened overflow checks and concrete 256-bit inputs. For the stated
round-trip formula, q=floor(xf/(y+f))<=xf/(y+f) and
back=floor((y+f)q/x)<=f; hence flooring cannot make this isolated round trip
profitable. This does not imply all Solidity operation orders round safely.
The module is a concrete arithmetic replay, not symbolic all-input EVM
verification. No reserve-width, token-decimal, bytecode, gas, tick-crossing,
or signed-arithmetic refinement claim is made.

## 7. Trust boundary

QF_NRA remains nonlinear after reserve window bounds; bounding is not
linearization. Known constants and positive-denominator polynomial equations
make these small instances manageable. Every solver has a 30-second timeout;
UNKNOWN is inconclusive. SMT-LIB queries and statistics enable replay. Z3
UNSAT is not a separately checked proof certificate. Tests and exact rational
SAT replay increase confidence but cannot establish contract/model equivalence.
