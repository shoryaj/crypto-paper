"""Reproducible illustrative figures; no measured data are synthesized here."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "paper/figures"
OUT.mkdir(parents=True, exist_ok=True)

NAVY = "#17324D"
TEAL = "#007F86"
CORAL = "#D65F4B"
GOLD = "#B47A16"
INK = "#263B4D"
MUTED = "#597080"
LIGHT = "#E9F0F5"
WHITE = "#FFFFFF"
PALE_TEAL = "#E5F3F2"
PALE_CORAL = "#FAECE8"
PALE_GOLD = "#FFF4DF"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "text.color": INK,
    "axes.labelcolor": INK,
    "axes.edgecolor": "#AEBCC6",
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "savefig.facecolor": WHITE,
})


def save(fig, name):
    # Keep fixed page dimensions so all figure sizes are predictable in LaTeX.
    for extension in ("pdf", "png"):
        fig.savefig(OUT / f"color-{name}.{extension}", dpi=250)
    plt.close(fig)


def card(ax, xy, width, height, title, body, color=TEAL, fill=PALE_TEAL,
         title_size=9, body_size=8.1):
    x, y = xy
    patch = FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.006,rounding_size=0.013",
        edgecolor=color, linewidth=1.0, facecolor=fill,
        transform=ax.transAxes, zorder=3,
    )
    ax.add_patch(patch)
    ax.text(x + .015, y + height - .034, title, color=color,
            fontsize=title_size, fontweight="bold", va="top",
            transform=ax.transAxes, zorder=4)
    ax.text(x + .015, y + height - .091, body, color=INK,
            fontsize=body_size, va="top", linespacing=1.47,
            transform=ax.transAxes, zorder=4)


def arrow(ax, start, end, color=MUTED, lw=1.15, style="-|>"):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle=style,
                                mutation_scale=10, linewidth=lw, color=color,
                                transform=ax.transAxes, zorder=2))


def attack_flow():
    fig = plt.figure(figsize=(7.2, 4.35))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.text(.025, .967, "ATTACK TRACE AND TERMINAL EXTRACTION ACCOUNTING", fontsize=10,
            fontweight="bold", color=NAVY, va="top", transform=ax.transAxes)
    ax.text(.025, .906, "Token A = collateral  |  Token B = accounting unit", fontsize=8.5,
            color=MUTED, va="top", transform=ax.transAxes)
    ax.text(.702, .899, r"Pre-owned $C$ units of A", fontsize=8.5, color=GOLD,
            fontweight="bold", va="top", transform=ax.transAxes)
    arrow(ax, (.835, .855), (.835, .807), color=GOLD)
    positions = [.025, .36, .695]
    width, height = .278, .235
    top_y, bottom_y = .564, .209
    card(ax, (positions[0], top_y), width, height, "1  Borrow flash liquidity",
         r"Receive $f$ units of B" + "\n" + r"Repayment due: $f(1+r)$" + "\n" + r"Constraint: $0<f\leq F$", color=NAVY, fill=LIGHT)
    card(ax, (positions[1], top_y), width, height, "2  Swap B for A",
         r"Acquired A: $a=xf/(y+f)$" + "\n" + "Spot collateral price rises:" + "\n" + r"$p_1=p_0(1+f/y)^2$")
    card(ax, (positions[2], top_y), width, height, "3  Pledge C; borrow b",
         r"Pledge pre-owned $C$, not $a$" + "\n" + r"Borrow $b\leq\min(T,CLp_1)$" + "\n" + r"Liquid wallet: $(a,b)$", color=CORAL, fill=PALE_CORAL)
    card(ax, (positions[2], bottom_y), width, height, "4  Reverse acquired A",
         r"Sell all $a$ back for $f$ B" + "\n" + r"Reserves return to $(x,y)$" + "\n" + r"Liquid wallet: $(0,b+f)$")
    card(ax, (positions[1], bottom_y), width, height, "5  Repay the flash loan",
         r"Return $f(1+r)$ B" + "\n" + r"Final wallet: $(0,b-rf)$" + "\n" + "Ordinary debt remains", color=NAVY, fill=LIGHT)
    card(ax, (positions[0], bottom_y), width, height, "6  Settle by forfeiture",
         r"Forfeit collateral worth $V$" + "\n" + "Assume non-recourse debt" + "\n" + r"Net extraction: $\Pi=b-rf-V$", color=CORAL, fill=PALE_CORAL)
    for i in [0, 1]:
        arrow(ax, (positions[i] + width + .007, top_y + height / 2),
              (positions[i + 1] - .007, top_y + height / 2))
    arrow(ax, (positions[2] + width / 2, top_y - .008),
          (positions[2] + width / 2, bottom_y + height + .008))
    for i in [2, 1]:
        arrow(ax, (positions[i] - .007, bottom_y + height / 2),
              (positions[i - 1] + width + .007, bottom_y + height / 2))
    ax.text(.025, .125, "KEY SECURITY CHECK", fontsize=8.4, fontweight="bold", color=CORAL,
            transform=ax.transAxes)
    ax.text(.025, .084, "Restoring the AMM and repaying the flash lender do not settle the ordinary debt.",
            fontsize=8.5, transform=ax.transAxes)
    ax.text(.025, .039, "Model assumptions: no swap fee; fixed reference price; collateral forfeiture; bounded flash capacity.",
            fontsize=7.8, color=MUTED, transform=ax.transAxes)
    save(fig, "attack-flow")


def verification_pipeline():
    fig = plt.figure(figsize=(7.2, 4.05))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.text(.025, .967, "HOW THE VERIFIER CHECKS ECONOMIC SAFETY", fontsize=10,
            fontweight="bold", color=NAVY, va="top", transform=ax.transAxes)
    card(ax, (.025, .674), .282, .224, "1  Model inputs",
         r"Reserves, $C,L,r,F,T$" + "\n" + "Fixed transaction schedule" + "\n" + "Explicit policy assumptions", color=NAVY, fill=LIGHT)
    card(ax, (.385, .674), .588, .224, "2  Ask Z3 for a counterexample",
         "Exact rational constants; polynomial transition constraints" + "\n" +
         r"QF_NRA query: $\exists\,$ feasible execution with $\Pi>0$" + "\n" +
         "The query tests existence; it does not maximize profit.", color=TEAL, fill=PALE_TEAL)
    arrow(ax, (.315, .785), (.375, .785))
    # Fan-out connectors are rendered behind the three status cards.
    ax.plot([.172, .834], [.61, .61], color=MUTED, lw=1.15, transform=ax.transAxes, zorder=1)
    ax.plot([.679, .679], [.668, .61], color=MUTED, lw=1.15, transform=ax.transAxes, zorder=1)
    for center in [.172, .503, .834]:
        arrow(ax, (center, .61), (center, .564))
    card(ax, (.025, .291), .293, .26, "SAT: a witness exists",
         "Replay rational witnesses" + "\n" + "using exact Fraction arithmetic" + "\n" + "Check balances and guards" + "\n" + "Confirm net extraction", color=CORAL, fill=PALE_CORAL, body_size=8)
    card(ax, (.356, .291), .293, .26, "UNSAT: query excluded",
         "No profitable execution" + "\n" + "satisfies this encoding" + "\n" + "Safety is conditional on" + "\n" + "the model and assumptions", color=TEAL, fill=PALE_TEAL, body_size=8)
    card(ax, (.687, .291), .286, .26, "UNKNOWN: unresolved",
         "Timeout or solver limit" + "\n" + "provides no decisive result" + "\n" + "Record it explicitly" + "\n" + "Do not label it safe", color=GOLD, fill=PALE_GOLD, body_size=8)
    card(ax, (.025, .035), .948, .171, "3  Independent analytical comparison",
         r"SymPy-derived criterion: compare $g(0)$, $g(F)$ and an in-range cash-cap kink $g(f_c)$." + "\n" +
         "Compare the positivity decision with each core sweep result; optimality comes from this analysis.",
         color=NAVY, fill=LIGHT, body_size=8)
    save(fig, "verification-pipeline")


def analytical_curves():
    V, L, r, F, T = 100., .75, .0009, 1000., 400.
    f = np.linspace(0, F, 2001)
    fig = plt.figure(figsize=(7.2, 3.95))
    ax = fig.add_axes([.105, .245, .855, .59])
    fig.text(.025, .965, "ANALYTICAL PROFIT ENVELOPE UNDER FIXED FLASH CAPACITY", fontsize=10,
             fontweight="bold", color=NAVY, va="top")
    fig.text(.025, .902, r"$g(f)=\min\{T,VL(1+f/y)^2\}-V-rf$", fontsize=10.5, color=INK)
    ax.axhspan(0, 320, color=PALE_CORAL, alpha=.47, zorder=0)
    ax.axhspan(-40, 0, color=PALE_TEAL, alpha=.8, zorder=0)
    ax.axhline(0, color=NAVY, linewidth=1.0, zorder=2)
    metrics = []
    for y, color, linestyle in [(100., CORAL, "-"), (1000., TEAL, "--"), (10000., NAVY, "-.")]:
        g = np.minimum(T, V * L * (1 + f / y)**2) - V - r * f
        ax.plot(f, g, lw=2, color=color, ls=linestyle, label=f"x = y = {y:,.0f}")
        fc = y * (np.sqrt(T / (V * L)) - 1)
        candidates = [0., F] + ([fc] if 0 <= fc <= F else [])
        profits = [min(T, V * L * (1 + ff / y)**2) - V - r * ff for ff in candidates]
        idx = int(np.argmax(profits))
        metrics.append({"x": y, "y": y, "cap_kink": float(fc), "kink_in_domain": bool(0 <= fc <= F),
                        "optimal_f": candidates[idx], "optimal_g": profits[idx], "g_F": float(g[-1])})
        if 0 <= fc <= F:
            gc = min(T, V * L * (1 + fc / y)**2) - V - r * fc
            ax.plot([fc], [gc], "o", color=color, ms=4.5, zorder=4)
            ax.annotate(r"Cash cap binds: $f_c=130.94$", xy=(fc, gc), xytext=(290, 260),
                        fontsize=8, color=CORAL, arrowprops={"arrowstyle": "-", "color": CORAL,
                                                              "linewidth": .8})
        ax.plot([F], [g[-1]], "o", color=color, ms=4, zorder=4)
    ax.annotate("199.10 B", xy=(1000, 199.1), xytext=(760, 224), fontsize=8,
                color=TEAL, arrowprops={"arrowstyle": "-", "color": TEAL, "linewidth": .8})
    ax.annotate("-10.15 B", xy=(1000, -10.15), xytext=(813, -34), fontsize=8,
                color=NAVY, arrowprops={"arrowstyle": "-", "color": NAVY, "linewidth": .8})
    ax.text(325, 13, "Positive extraction possible", fontsize=7.8, color=CORAL)
    ax.set_xlim(0, 1025)
    ax.set_ylim(-42, 319)
    ax.set_xlabel("Flash amount f (token B)", labelpad=5)
    ax.set_ylabel("Maximum net extraction g(f) (token B)", labelpad=7)
    ax.set_yticks([0, 100, 200, 300])
    ax.set_xticks([0, 200, 400, 600, 800, 1000])
    ax.grid(axis="y", color="#CFD9DF", linewidth=.5)
    ax.spines[["top", "right"]].set_visible(False)
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc="center", bbox_to_anchor=(.565, .099), ncol=3, frameon=False,
               fontsize=8, handlelength=2.7, columnspacing=2.)
    fig.text(.105, .03, r"Synthetic analytical curves: $V=100$, $L=0.75$, $r=0.0009$, $F=1000$, $T=400$, $p_0=1$.",
             fontsize=7.6, color=MUTED)
    save(fig, "profit-curves")
    print(json.dumps({"parameters": {"V": V, "L": L, "r": r, "F": F, "T": T},
                      "analytical_curve_metrics": metrics}, indent=2))


if __name__ == "__main__":
    attack_flow()
    verification_pipeline()
    analytical_curves()
    print("Saved color-attack-flow, color-verification-pipeline, color-profit-curves as PDF and PNG.")
