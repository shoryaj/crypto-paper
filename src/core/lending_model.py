"""Lending limits expressed as polynomial inequalities."""
import z3


def borrowing(solver, collateral, price, ltv, cash, name='borrow'):
    """Allow any feasible borrow; profit search chooses extraction if possible."""
    amount = z3.Real(name)
    solver.add(amount >= 0, amount <= cash,
               amount <= collateral * price * ltv)
    return amount
